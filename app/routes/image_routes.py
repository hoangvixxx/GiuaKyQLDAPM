from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.image_model import Image
from ..models.tag_model import Tag 
from ..services.ai_service import get_tags_from_image_url # Import logic AI
from .. import db
from ..services.cloudinary_service import upload_to_cloudinary # Import logic Cloudinary

image_bp = Blueprint('image', __name__)

# --- Hàm trợ giúp để tìm hoặc tạo tag ---
def find_or_create_tag(tag_name):
    """Tìm tag trong CSDL, nếu chưa có thì tạo mới"""
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        # Tạm commit ở đây để lấy được tag.id
        db.session.commit() 
    return tag
# ------------------------------------


@image_bp.route('/upload', methods=['POST'])
@jwt_required() 
def upload_image():
    # Lấy ID (dưới dạng chuỗi) từ token
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str) # Chuyển lại thành SỐ
    
    if 'image' not in request.files:
        return jsonify({"msg": "Không tìm thấy file ảnh"}), 400
        
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"msg": "Chưa chọn file"}), 400
        
    if file:
        # 1. Tải file lên Cloudinary
        image_url = upload_to_cloudinary(file, file.filename)
        
        if image_url is None:
            return jsonify({"msg": "Lỗi khi upload lên Cloudinary"}), 500
            
        try:
            # 2. Lưu ảnh vào CSDL (chưa commit)
            new_image = Image(
                user_id=current_user_id, # Dùng ID đã chuyển thành SỐ
                image_url=image_url,
                original_name=file.filename
            )
            db.session.add(new_image)
            
            # --- PHẦN MỚI: XỬ LÝ AI TAGS ---
            # 3. Gọi AI để lấy tags
            tags_list = get_tags_from_image_url(image_url)
            
            if tags_list:
                # 4. Lưu tags vào CSDL
                for tag_name in tags_list:
                    tag_obj = find_or_create_tag(tag_name)
                    # Gắn tag này vào ảnh
                    new_image.tags.append(tag_obj)
            # ---------------------------------
            
            # 5. Commit mọi thứ vào CSDL
            db.session.commit()
            
            return jsonify({
                "msg": "Upload và phân loại thành công!", 
                "url": image_url,
                "image_id": new_image.id,
                "tags": tags_list # Trả về tags cho client xem
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Lỗi khi lưu CSDL hoặc xử lý AI", "error": str(e)}), 500

# ===============================================
# === CÁC HÀM MỚI (PHẢI NẰM BÊN NGOÀI) =====
# ===============================================

@image_bp.route('/my-images', methods=['GET'])
@jwt_required()
def get_my_images():
    """Lấy tất cả ảnh của user đang đăng nhập"""
    # Lấy ID (dưới dạng chuỗi) từ token
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str) # Chuyển lại thành số để query
    
    # Sắp xếp theo ngày tạo mới nhất
    user_images = Image.query.filter_by(user_id=current_user_id).order_by(Image.created_at.desc()).all()
    
    results = []
    for img in user_images:
        results.append({
            "id": img.id,
            "url": img.image_url,
            "uploaded_at": img.created_at.isoformat(), # Dùng isoformat cho JSON
            "tags": [tag.name for tag in img.tags] # Lấy danh sách tên tags
        })
        
    return jsonify(results), 200


@image_bp.route('/search', methods=['GET'])
@jwt_required()
def search_images_by_tag():
    """Tìm kiếm ảnh theo tag (chỉ trong kho ảnh của user)"""
    tag_name = request.args.get('tag') # Lấy ?tag=... từ URL
    if not tag_name:
        return jsonify({"msg": "Thiếu tham số 'tag'"}), 400
        
    # Tìm tag trong CSDL
    tag_obj = Tag.query.filter_by(name=tag_name.lower()).first()
    
    if not tag_obj:
        return jsonify({"msg": f"Không tìm thấy ảnh nào với tag '{tag_name}'"}), 404
        
    # Lấy ID (dưới dạng chuỗi) từ token
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str) # Chuyển lại thành số
    
    # Lọc những ảnh vừa có tag đó, vừa có user_id_đúng
    user_images_with_tag = [img for img in tag_obj.images if img.user_id == current_user_id]
    
    results = []
    for img in user_images_with_tag:
        results.append({
            "id": img.id,
            "url": img.image_url,
            "uploaded_at": img.created_at.isoformat() # Dùng isoformat
        })
        
    return jsonify(results), 200