import cloudinary
import cloudinary.uploader
import os
import re 

# Cấu hình Cloudinary (Giữ nguyên)
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
    api_key = os.getenv('CLOUDINARY_API_KEY'), 
    api_secret = os.getenv('CLOUDINARY_API_SECRET') 
)

def upload_to_cloudinary(file, original_filename):
    """
    Tải file lên Cloudinary và trả về URL an toàn (secure_url).
    """
    try:
        # Dùng tên file gốc (không có đuôi) làm public_id để dễ quản lý
        base_name = os.path.splitext(original_filename)[0] 
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder="my_project_uploads", # Tạo thư mục trên Cloudinary
            public_id = base_name # DÙNG TÊN GỐC (KHÔNG ĐỔI)
        )
        
        secure_url = upload_result.get('secure_url')
        return secure_url # CHỈ TRẢ VỀ URL
        
    except Exception as e:
        print(f"Lỗi Cloudinary Upload: {e}")
        return None

def delete_from_cloudinary(image_url):
    """
    Xóa một tài nguyên (ảnh) khỏi Cloudinary.
    Nhận vào FULL URL và trích xuất public_id an toàn.
    """
    try:
        # 1. TRÍCH XUẤT PUBLIC_ID AN TOÀN TỪ URL (my_project_uploads/ten_file)
        # Regex để tìm chuỗi nằm sau timestamp và loại bỏ đuôi file
        match = re.search(r'v\d+/([^/]+/[^.]+)', image_url)
        if not match:
             # Nếu URL không khớp, lấy phần cuối cùng của URL
             public_id_with_folder = os.path.splitext(image_url.split('/')[-1])[0]
        else:
             public_id_with_folder = match.group(1)

        # 2. Lệnh destroy() sẽ xóa file
        result = cloudinary.uploader.destroy(public_id_with_folder)
        
        # 3. LOGIC XỬ LÝ LỖI
        if result.get('result') == 'not found':
             print(f"Cloudinary WARNING: Public ID {public_id_with_folder} not found on cloud. Continuing deletion from DB.")
             return True # Coi là thành công
             
        if result.get('result') != 'ok':
             raise Exception(f"Cloudinary deletion failed: {result.get('result')}")
        
        return True

    except Exception as e:
        print(f"Cloudinary DELETE error: {e}")
        raise