Hệ thống Phân loại và Lưu trữ Hình ảnh Trực tuyến
Đây là dự án giữa kỳ môn Quản lý Dự án Phần mềm, xây dựng một hệ thống API backend bằng Python (Flask) cho phép người dùng upload, quản lý và phân loại ảnh.

Hệ thống sử dụng Cloudinary để lưu trữ file ảnh trực tuyến và sử dụng mô hình AI chạy tại chỗ (local) Hugging Face Transformers (dựa trên google/vit-base-patch16-224) để tự động phân loại và gắn thẻ (tag) cho ảnh.

Tính năng chính
Xác thực: Đăng ký và Đăng nhập người dùng (sử dụng JWT).

Lưu trữ: Upload ảnh lên dịch vụ đám mây Cloudinary.

Phân loại AI: Tự động phân loại ảnh bằng mô hình AI (Hugging Face Transformers) chạy ngay trên server.

Tìm kiếm: Lấy tất cả ảnh của người dùng hoặc tìm ảnh theo tag cụ thể.

Demo: Tích hợp 2 trang Đăng nhập & Demo để chạy trực tiếp trên trình duyệt.

Công nghệ sử dụng
Backend: Python 3 (Tương thích 3.12+), Flask

CSDL: Microsoft SQL Server

Lưu trữ: Cloudinary

Phân loại AI (Local): Hugging Face transformers, torch (PyTorch)

Xử lý ảnh (AI): pillow, requests

Giao tiếp CSDL: Flask-SQLAlchemy, pyodbc

Xác thực & Bảo mật: Flask-Bcrypt, Flask-JWT-Extended, Flask-CORS

Thư viện khác: python-dotenv

Hướng dẫn Cài đặt và Chạy
1. Chuẩn bị Môi trường
Clone (tải) project này về máy.

Mở thư mục dự án, mở một terminal mới gõ đường dẫn chứa project (vd:cd python-photo-system).

Tạo một môi trường ảo :

Sau khi vào được project tiếp tục gõ trong terminal

python -m venv venv

Kích hoạt môi trường ảo:
Trên Windows: .\venv\Scripts\activate

Trên macOS/Linux: source venv/bin/activate

2. Cài đặt Thư viện (Sẽ mất thời gian)
Chạy lệnh sau để cài đặt tất cả các thư viện cần thiết. Lưu ý: các thư viện AI (torch, transformers) rất nặng (có thể lên tới 1-2GB).
Bash
pip install -r requirements.txt

3. Cài đặt Cơ sở dữ liệu (SQL Server)
Mở SQL Server Management Studio (SSMS).

Tạo một Cơ sở dữ liệu (Database) mới. Tên mặc định trong code là PhotoStorageDB.

Quan trọng: Bạn không cần tạo bảng (table) bằng tay. Khi bạn chạy server lần đầu tiên, code SQLAlchemy (db.create_all()) sẽ tự động tạo 4 bảng: Users, Images, Tags, và Image_Tags.

4. Cấu hình Biến Môi trường (.env)
Tạo một file mới tên là .env trong thư mục gốc của dự án.

Điền các thông tin của bạn vào.

.env.example 
# Cấu hình CSDL SQL Server (Điền thông tin của bạn)
DB_USER=sa (tên người dùng)
DB_PASS=123 (mật khẩu)
DB_SERVER=TEN-SERVER-CUA-BAN (tên server SQL)
DB_NAME=PhotoStorageDB (tên cơ sở dữ liệu)

# Key bí mật cho JWT (Tự tạo một chuỗi ngẫu nhiên)
JWT_SECRET_KEY=chuoi-bi-mat-dai-nga-nhien-cua-ban

Để lấy key bí mật của riêng bạn, hãy chạy lệnh sau trong terminal hoặc cmd
python -c "import secrets; print(secrets.token_hex(32))"
Nó sẽ đưa ra một chuỗi kí tự hãy copy nó (vd: 7cfd72846757a952bfd9b74fbeba57fe9ab91c2ba92b63ca7fa0cf0a7d90daa8)

# Cấu hình Cloudinary (Lấy từ Dashboard của Cloudinary)
CLOUDINARY_CLOUD_NAME=ten-cloud-cua-ban
CLOUDINARY_API_KEY=key-api-cua-ban
CLOUDINARY_API_SECRET=key-bi-mat-cua-ban
Cách lấy 3 cái trên hãy làm từng bước sau
 Đăng nhập vào Bảng điều khiển (Dashboard): Truy cập https://cloudinary.com/console và đăng nhập vào tài khoản của bạn.
 
 Tìm phần Chi tiết Tài khoản (Account Details):Sau khi đăng nhập, bạn sẽ được đưa đến trang Dashboard. Tất cả 3 khóa cần thiết (Cloud Name, API Key, và API Secret) đều nằm ngay trong hộp Account Details (Chi tiết tài khoản) ở đầu trang.

 Lấy và Điền các Khóa: Bạ cần Copy 3 giá trị sau (Cloud name, API Key, API Secret) và dán vào file .env

Cách Chạy Demo

*Lưu ý!!!*
Hệ thống này chạy mô hình AI tại chỗ. Hãy KIÊN NHẪN!

Mở terminal tại dự án khi đã vào môi trường ảo, chạy python run.py (Chờ lần đầu): Lần đầu tiên bạn chạy server, nó sẽ mất 1-3 phút để tải mô hình AI (khoảng 300MB+) về máy. Terminal sẽ hiển thị Đang tải mô hình....

Upload ảnh (Chờ khi demo): Khi bạn upload một ảnh, server sẽ mất 5-10 giây để "suy nghĩ" (phân loại bằng CPU) trước khi trả về kết quả.

Bắt đầu Demo
Đảm bảo bạn đã kích hoạt môi trường ảo (.\venv\Scripts\activate).

Khởi động máy chủ Flask (và kiên nhẫn chờ nó tải mô hình):

Terminal

python run.py
Sau khi server báo sẵn sàng, mở trình duyệt (Chrome, Firefox, Edge...) và truy cập: http://127.0.0.1:5000/

Trang "Đăng nhập" sẽ xuất hiện. Bạn có thể thực hiện demo:

Bước 1: Đăng ký (nếu là lần đầu) và Đăng nhập.

Bước 2: Bạn sẽ được chuyển đến trang Demo. Chọn file ảnh và nhấn Upload (và chờ 5-10 giây).

Bước 3: Ảnh mới sẽ xuất hiện, và ô "Kết quả API" sẽ hiển thị các tag thật (ví dụ: ["tabby", "Egyptian_cat"]).

Bước 4: Gõ tag cat (hoặc tag AI vừa trả về) vào ô tìm kiếm và nhấn "Tìm theo Tag".