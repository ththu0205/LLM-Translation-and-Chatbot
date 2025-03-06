import os
import time
import pickle
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
  
app = Flask(__name__)
CORS(app)  

# Tải biến môi trường từ file .env và lấy API key từ biến môi trường
load_dotenv()
GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GENAI_API_KEY không được thiết lập trong biến môi trường.")

# Cấu hình Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ======== 1. Load dữ liệu đã indexing sẵn ========
with open("Interface/indexed_data.pkl", "rb") as f:
    indexed_data = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")  
header_embeddings_array = np.vstack([model.encode([d["header"]]) for d in indexed_data])
content_embeddings_array = np.vstack([d["embedding"] for d in indexed_data])
chunks_list = indexed_data

# ======== 2. Hàm find_best_chunks (retrieval) ========
def find_best_chunks(question, header_weight=2.0, content_weight=1.0, k=2):
    """
    Lấy các chunk liên quan nhất cho câu hỏi của người dùng
    bằng cách ưu tiên sự tương đồng với tiêu đề.
    """
    question_embedding = model.encode([question])
    header_similarities = cosine_similarity(question_embedding, header_embeddings_array)[0]
    content_similarities = cosine_similarity(question_embedding, content_embeddings_array)[0]

    combined_scores = (header_weight * header_similarities) + (content_weight * content_similarities)
    sorted_indices = np.argsort(combined_scores)[::-1]
    top_indices = sorted_indices[:k]
    return [chunks_list[i] for i in top_indices]

# ======== 3. Hàm generate_answer: gọi Gemini ========
def generate_answer(question, chunks):
    """
    Kết hợp các chunk và gửi đến Gemini để tạo câu trả lời.
    """
    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)
    prompt = f"""
        You are an AI assistant. Use the provided context to answer the user's question in English.

        Context:
        {context}

        User's Question:
        {question}

        Answer in natural language:
    """
    start_time = time.time()
    chat_session = genai.GenerativeModel(model_name="gemini-2.0-flash-exp").start_chat()
    response = chat_session.send_message(prompt)
    end_time = time.time()
    return response.text.strip(), end_time - start_time

# ======== 4. Endpoint Flask ========
@app.route("/", methods=["GET"])
def home():
    return "Server is running. Try POST /ask"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")
    best_chunks = find_best_chunks(user_question, k=2)
    answer, response_time = generate_answer(user_question, best_chunks)
    return jsonify({"answer": answer, "response_time": response_time})

if __name__ == "__main__":
    # genai.configure(api_key=GEMINI_API_KEY)  
    app.run(host="0.0.0.0", port=8000, debug=True)
