from flask import Flask, render_template # Đảm bảo có render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .config import Config
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) 
    CORS(app) 

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # --- SỬA ROUTES ---
    @app.route('/')
    def home():
        """Trang chủ bây giờ là trang Đăng nhập"""
        return render_template('login.html')

    @app.route('/demo')
    def demo_page():
        """Trang Demo (chỉ vào sau khi đăng nhập)"""
        return render_template('demo.html')
    # -------------------

    # --- Đăng ký các API routes (Giữ nguyên) ---
    from .routes.auth_routes import auth_bp 
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from .routes.image_routes import image_bp
    app.register_blueprint(image_bp, url_prefix='/api/images')
    # -----------------------------------------------

    with app.app_context():
        from .models import user_model, image_model, tag_model 
        db.create_all()
        
    return app