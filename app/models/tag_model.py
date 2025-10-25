from .. import db

# Đây là bảng trung gian Nhiều-Nhiều
image_tags_table = db.Table('Image_Tags',
    db.Column('image_id', db.Integer, db.ForeignKey('Images.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('Tags.id'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'Tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)