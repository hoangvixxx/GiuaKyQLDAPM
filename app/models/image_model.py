from .. import db
import datetime
# THÊM DÒNG NÀY:
from .tag_model import image_tags_table # Import bảng trung gian

class Image(db.Model):
    __tablename__ = 'Images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    image_url = db.Column(db.String(1024), nullable=False)
    original_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', back_populates='images')

    # --- THÊM MỐI QUAN HỆ NÀY (Đây chính là phần bị thiếu) ---
    # Báo cho SQLAlchemy biết 'Image' có thể có nhiều 'Tag'
    # thông qua bảng trung gian 'image_tags_table'
    tags = db.relationship('Tag', secondary=image_tags_table, lazy='subquery',
                           backref=db.backref('images', lazy=True))
    # --------------------------------------------------------