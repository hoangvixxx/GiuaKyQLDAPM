from .. import db # '..' có nghĩa là import biến 'db' từ file app/__init__.py

class User(db.Model):
    __tablename__ = 'Users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Mối quan hệ: Một User có nhiều Image
    images = db.relationship('Image', back_populates='user', lazy=True)