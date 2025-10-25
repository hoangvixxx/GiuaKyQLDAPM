import os
from transformers import pipeline
import requests
from PIL import Image
import io

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

print("!!! AI LOCAL (Hugging Face): Đang tải mô hình... (Việc này chỉ xảy ra 1 lần khi server khởi động)")
try:
    classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
    print("!!! AI LOCAL (Hugging Face): Tải mô hình thành công! Server sẵn sàng.")
except Exception as e:
    print(f"!!! AI LOCAL (Hugging Face): LỖI KHI TẢI MODEL: {e}")
    classifier = None

def get_tags_from_image_url(image_url):
    if classifier is None:
        print("!!! AI LOCAL (Hugging Face): Model chưa được tải, trả về hack.")
        return ["demo hack", "model error"]
    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))

        print(f"!!! AI LOCAL (Hugging Face): Đang phân loại ảnh {image_url}...")
        predictions = classifier(img)
        
        tags = []
        # TĂNG SỐ LƯỢNG KẾT QUẢ ĐẦU RA LÊN 10 HOẶC 15
        for pred in predictions[:10]: 
            labels = pred['label'].split(', ')
            tags.extend(labels)
        
        tags = list(dict.fromkeys(tags)) 
        print(f"!!! AI LOCAL (Hugging Face): Phân loại xong! Tags: {tags}")
        return tags
    except Exception as e:
        print(f"!!! AI LOCAL (Hugging Face): Lỗi khi đang phân loại: {e}")
        return None