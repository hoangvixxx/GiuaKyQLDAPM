from app import create_app

# Gọi hàm factory để tạo app
app = create_app()

if __name__ == '__main__':
    # Chạy app ở chế độ debug (tự khởi động lại khi code thay đổi)
    app.run(debug=True, port=5000)