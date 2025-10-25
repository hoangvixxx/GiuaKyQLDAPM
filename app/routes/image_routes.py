from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.image_model import Image
from ..models.tag_model import Tag 
from ..services.ai_service import get_tags_from_image_url
from .. import db
from ..services.cloudinary_service import upload_to_cloudinary
from ..services.cloudinary_service import delete_from_cloudinary
import re 
import os # <-- Đảm bảo import os

image_bp = Blueprint('image', __name__)

# --- Hàm trợ giúp để tìm hoặc tạo tag ---
def find_or_create_tag(tag_name):
    """Tìm tag trong CSDL, nếu chưa có thì tạo mới"""
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit() 
    return tag
# ------------------------------------


@image_bp.route('/upload', methods=['POST'])
@jwt_required() 
def upload_image():
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str)
    
    if 'image' not in request.files:
        return jsonify({"msg": "Không tìm thấy file ảnh"}), 400
        
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"msg": "Chưa chọn file"}), 400
        
    if file:
        # SỬA LỖI LOGIC: HÀM UPLOAD TRẢ VỀ 2 GIÁ TRỊ (URL và PUBLIC_ID)
        # Giả sử hàm upload_to_cloudinary vẫn trả về 1 giá trị (URL) như trong code bạn gửi
        image_url = upload_to_cloudinary(file, file.filename) 
        
        if image_url is None:
            return jsonify({"msg": "Lỗi khi upload lên Cloudinary"}), 500
            
        try:
            new_image = Image(
                user_id=current_user_id,
                image_url=image_url,
                original_name=file.filename
            )
            db.session.add(new_image)
            
            tags_list = get_tags_from_image_url(image_url)
            
            if tags_list:
                for tag_name in tags_list:
                    tag_obj = find_or_create_tag(tag_name)
                    new_image.tags.append(tag_obj)
            
            db.session.commit()
            
            return jsonify({
                "msg": "Upload và phân loại thành công!", 
                "url": image_url,
                "image_id": new_image.id,
                "tags": tags_list 
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Lỗi khi lưu CSDL hoặc xử lý AI", "error": str(e)}), 500

# ===============================================
# === XÓA ẢNH (ĐÃ SỬA LỖI UNBOUNDLOCALERROR) ===
# ===============================================

@image_bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str)
    
    public_id = None # Khai báo public_id sớm

    image = Image.query.filter_by(id=image_id, user_id=current_user_id).first()
    
    if not image:
        return jsonify({"msg": "Image not found or access denied"}), 404

    try:
        # --- LOGIC TRÍCH XUẤT PUBLIC_ID MỚI VÀ AN TOÀN HƠN ---
        
        # 1. Tách chuỗi URL theo dấu '/'
        parts = image.image_url.split('/')
        
        # 2. Tìm vị trí của phần tử 'upload'
        if 'upload' not in parts:
             # Đây là URL không phải của Cloudinary, không cần xóa trên cloud
             public_id = 'NO_PUBLIC_ID'
        else:
            upload_index = parts.index('upload')
            # Public ID là phần tử thứ 2 sau 'upload' (vị trí upload_index + 2)
            
            # Cần lấy hết các phần tử từ timestamp trở đi, bao gồm folder/ten_file.jpg
            public_id_with_timestamp_and_ext = "/".join(parts[upload_index + 1:])
            
            # Regex để loại bỏ timestamp (v<số>/) và giữ lại phần folder/ten_file
            # Ví dụ: v1761356045/my_project_uploads/anh-meo.jpg
            # Ta muốn: my_project_uploads/anh-meo
            
            # Công thức đơn giản nhất: Lấy phần nằm sau /upload/v<timestamp>/
            public_id_with_ext = "/".join(parts[upload_index + 2:])

            # Loại bỏ phần mở rộng
            public_id = os.path.splitext(public_id_with_ext)[0] 


        # 3. Kiểm tra và Xóa
        if not public_id:
             raise Exception("Could not derive public ID.")
             
        # 4. Xóa khỏi Cloudinary (Chỉ khi có Public ID thật sự)
        if public_id != 'NO_PUBLIC_ID':
            delete_from_cloudinary(public_id)

        # 5. Xóa khỏi CSDL
        db.session.delete(image)
        db.session.commit()

        return jsonify({"msg": f"Image ID {image_id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        # Trả về lỗi chi tiết hơn
        return jsonify({"msg": "Lỗi xóa ảnh server", "error": str(e), "public_id_tentative": public_id}), 500


# ===============================================
# === CÁC HÀM GET (LẤY VÀ TÌM KIẾM) ===
# ===============================================

@image_bp.route('/my-images', methods=['GET'])
@jwt_required()
def get_my_images():
    """Lấy tất cả ảnh của user đang đăng nhập"""
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str)
    
    user_images = Image.query.filter_by(user_id=current_user_id).order_by(Image.created_at.desc()).all()
    
    results = []
    for img in user_images:
        results.append({
            "id": img.id,
            "url": img.image_url,
            "uploaded_at": img.created_at.isoformat(),
            "tags": [tag.name for tag in img.tags]
        })
        
    return jsonify(results), 200


@image_bp.route('/search', methods=['GET'])
@jwt_required()
def search_images_by_tag():
    """Tìm kiếm ảnh theo tag (chỉ trong kho ảnh của user)"""
    tag_name = request.args.get('tag') 
    if not tag_name:
        return jsonify({"msg": "Thiếu tham số 'tag'"}), 400
        
    tag_obj = Tag.query.filter_by(name=tag_name.lower()).first()
    
    if not tag_obj:
        return jsonify({"msg": f"Không tìm thấy ảnh nào với tag '{tag_name}'"}), 404
        
    current_user_id_str = get_jwt_identity()
    current_user_id = int(current_user_id_str)
    
    user_images_with_tag = [img for img in tag_obj.images if img.user_id == current_user_id]
    
    results = []
    for img in user_images_with_tag:
        results.append({
            "id": img.id,
            "url": img.image_url,
            "uploaded_at": img.created_at.isoformat()
        })
        
    return jsonify(results), 200