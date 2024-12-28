
# Thanh Thư API KEY: AIzaSyABCZhAO_mMrZJUntMpHC9IbveKwdEuJsM

import os
import requests
from langdetect import detect
import google.generativeai as genai

# Class để xử lý việc dịch văn bản sử dụng API Gemini
class GeminiTranslationModel:
    def __init__(self, api_key):
        self.api_key = api_key  # Lưu API key vào đối tượng
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"  # URL endpoint của Gemini API
    
    def translate_text(self, text, dest_language='vi'):
        """Dịch một văn bản sử dụng API Gemini"""
        if not isinstance(text, str):
            raise TypeError("The text must be a string")  # Kiểm tra nếu đầu vào không phải là chuỗi
        
        # Kiểm tra ngôn ngữ của văn bản đã là ngôn ngữ đích hay chưa
        try:
            if detect(text) == dest_language:
                return text  # Nếu văn bản đã là ngôn ngữ đích, trả về nguyên bản
        except:
            pass
        
        # Tạo payload cho API yêu cầu dịch
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Translate the following text to {dest_language}: {text}"
                }]
            }]
        }
        
        # Cấu hình headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gửi request đến API Gemini
        try:
            response = requests.post(
                f"{self.url}?key={self.api_key}",  # API key được truyền qua URL
                json=payload,  # Dữ liệu payload được gửi dưới dạng JSON
                headers=headers
            )
            response.raise_for_status()  # Kiểm tra nếu có lỗi trong phản hồi
            translation = response.json()['candidates'][0]['content']['parts'][0]['text']  # Lấy kết quả dịch
            return translation.strip()  # Trả về kết quả dịch sau khi loại bỏ khoảng trắng thừa
        
        except Exception as e:
            print(f"Translation error: {e}")  # In lỗi nếu có
            return text  # Nếu có lỗi, trả về văn bản gốc

# Class để xử lý việc dịch văn bản sử dụng mô hình Gemini Generative
class GeminiGenerativeTranslationModel:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)  # Cấu hình API key cho Google Gemini
        
        # Cấu hình cho việc sinh nội dung (text generation)
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        # Khởi tạo mô hình với các thông số cấu hình
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",  # Mô hình sử dụng
            generation_config=generation_config,
            system_instruction="Translate the given text into Vietnamese. If the text is already in Vietnamese, return it unchanged. If the text contains a mix of English and Vietnamese, translate the entire text into Vietnamese. Make sure to preserve the meaning and context, and adjust sentence structure if necessary for a natural flow in Vietnamese.\n",  # Hướng dẫn hệ thống
        )

    def translate_text(self, text):
        """Dịch văn bản sử dụng mô hình Gemini Generative"""
        chat_session = self.model.start_chat(
            history=[]  # Lịch sử chat bắt đầu trống
        )
        
        response = chat_session.send_message(text)  # Gửi tin nhắn và nhận phản hồi
        return response.text.strip()  # Trả về văn bản dịch

# Lớp dịch tổng hợp, sử dụng cả hai mô hình Gemini Translation và Gemini Generative Translation
class TranslationService:
    def __init__(self, gemini_api_key):
        # Khởi tạo các mô hình dịch
        self.gemini_model = GeminiGenerativeTranslationModel(gemini_api_key)
        self.requests_model = GeminiTranslationModel(gemini_api_key)

    def translate_single_text(self, text, dest_language='vi'):
        """Dịch một văn bản, sử dụng mô hình Gemini hoặc mô hình Requests"""
        try:
            # Thử sử dụng mô hình Gemini Generative để dịch
            return self.gemini_model.translate_text(text)
        except Exception as e:
            print(f"Error using generative model: {e}, switching to requests-based model")
            return self.requests_model.translate_text(text, dest_language)  # Nếu gặp lỗi, sử dụng mô hình Requests

    def translate_multiple_texts(self, texts, dest_language='vi'):
        """Dịch nhiều văn bản"""
        return [self.translate_single_text(text, dest_language) for text in texts]


if __name__ == "__main__":
    API_KEY = "AIzaSyABCZhAO_mMrZJUntMpHC9IbveKwdEuJsM"  # Thay thế bằng API key của bạn
    translation_service = TranslationService(API_KEY)

    # Dịch một văn bản
    json_1 = {
        'text': 'How old are you?',
        'dest_language': 'vi'
    }
    print("Translate single text:", translation_service.translate_single_text(json_1['text']))  # Dịch văn bản duy nhất

    # Dịch nhiều văn bản
    json_2 = {
        'text': ['Xin chào', 'I am Peter', 'Tôi là student'],
        'dest_language': 'vi'
    }
    print("Translate multiple texts:", translation_service.translate_multiple_texts(json_2['text']))  # Dịch nhiều văn bản
