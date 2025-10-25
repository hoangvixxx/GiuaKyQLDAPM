import cloudinary
import cloudinary.uploader
import os

# Cấu hình Cloudinary
# Nó sẽ tự động đọc các biến môi trường nếu tên đúng
cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET') 
)

def upload_to_cloudinary(file, original_filename):
    """
    Tải file lên Cloudinary và trả về URL an toàn (secure_url)
    """
    try:
        # Tải file lên Cloudinary
        # 'folder' là tùy chọn, giúp bạn tổ chức ảnh
        upload_result = cloudinary.uploader.upload(
            file,
            folder="my_project_uploads", # Tạo thư mục trên Cloudinary
            public_id = original_filename # Dùng tên gốc làm ID
        )
        
        # Lấy URL an toàn (https://...)
        secure_url = upload_result.get('secure_url')
        return secure_url

    except Exception as e:
        print(f"Lỗi Cloudinary: {e}")
        return None