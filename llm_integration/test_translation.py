import unittest
from translation import TranslationService  
from tabulate import tabulate

class TestTranslationService(unittest.TestCase):
    def setUp(self):
        """Tạo đối tượng TranslationService để sử dụng trong các test case."""
        self.api_key = "AIzaSyABCZhAO_mMrZJUntMpHC9IbveKwdEuJsM" 
        self.translation_service = TranslationService(self.api_key)

    def test_translate_single_text(self):
        """Kiểm thử việc dịch một văn bản."""
        text = "How are you?"
        translated_text = self.translation_service.translate_single_text(text, dest_language='vi')
        self.assertEqual(translated_text, "Bạn khỏe không?") 

    def test_translate_multiple_texts(self):
        """Kiểm thử việc dịch nhiều văn bản."""
        texts = ["Hello", "I am learning Python", "Tôi đang học lập trình"]
        expected_translations = ["Xin chào", "Tôi đang học Python", "Tôi đang học lập trình"]
        translated_texts = self.translation_service.translate_multiple_texts(texts, dest_language='vi')
        self.assertEqual(translated_texts, expected_translations)

    def test_translate_same_language(self):
        """Kiểm thử trường hợp văn bản đã ở ngôn ngữ đích."""
        text = "Tôi là sinh viên"
        translated_text = self.translation_service.translate_single_text(text, dest_language='vi')
        self.assertEqual(translated_text, text)  # Kết quả phải trả về chính xác văn bản gốc

    def test_mixed_language_translation(self):
        """Kiểm thử trường hợp văn bản có cả tiếng Anh và tiếng Việt."""
        text = "I am a student, tôi study lập trình."
        translated_text = self.translation_service.translate_single_text(text, dest_language='vi')
        self.assertEqual(translated_text, "Tôi là sinh viên, tôi học lập trình.")  

# Sửa lỗi trong phần in kết quả
if __name__ == "__main__":
    # Chạy tất cả các test case và lấy kết quả
    runner = unittest.TextTestRunner()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTranslationService)
    result = runner.run(suite)

    # Chuẩn bị kết quả để in ra bảng
    table = []
    for test, outcome in result.failures + result.errors:  # Duyệt qua failures và errors thay vì testsRun
        test_name = test._testMethodName
        status = 'FAIL' if outcome else 'PASS'
        table.append([test_name, status, outcome])

    # In kết quả ra bảng
    headers = ["Test Case", "Output", "Expected Output"]
    print(tabulate(table, headers, tablefmt="grid"))

