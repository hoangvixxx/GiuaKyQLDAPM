from flask import request, jsonify, Blueprint
from ..models.user_model import User
from .. import db, bcrypt
from flask_jwt_extended import create_access_token

# Tạo một "Blueprint" (một nhóm các routes) tên là 'auth'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Lấy dữ liệu JSON người dùng gửi lên (ví dụ: từ Postman)
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Thiếu email hoặc password"}), 400

        # Kiểm tra xem email đã có ai dùng chưa
        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "Email đã tồn tại"}), 409 # 409 = Conflict

        # Mã hóa mật khẩu
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Tạo user mới
        new_user = User(email=email, password_hash=hashed_password)
        
        # Thêm user vào CSDL
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"msg": "Đăng ký thành công"}), 201
        
    except Exception as e:
        db.session.rollback() # Hoàn tác nếu có lỗi
        return jsonify({"msg": "Đã xảy ra lỗi", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Thiếu email hoặc password"}), 400

        # Tìm user trong CSDL
        user = User.query.filter_by(email=email).first()

        # Kiểm tra xem user có tồn tại VÀ mật khẩu có khớp không
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Nếu khớp, tạo ra một Token
            access_token = create_access_token(identity=str(user.id))
            return jsonify(access_token=access_token), 200
        else:
            # Nếu không khớp
            return jsonify({"msg": "Sai email hoặc mật khẩu"}), 401 # 401 = Unauthorized
            
    except Exception as e:
        return jsonify({"msg": "Đã xảy ra lỗi", "error": str(e)}), 500