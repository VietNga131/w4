import os
from flask import Flask, jsonify, request, redirect
from flasgger import Swagger

app = Flask(__name__)

app.config['SWAGGER'] = {
    'openapi': '3.0.0'
}

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(current_dir, '..', 'swagger.yaml')
swagger = Swagger(app, template_file=yaml_path)

@app.route('/')
def home():
    # Đưa người dùng sang trang tài liệu API
    return redirect('/apidocs/')

# --- MOCK DATA ---
books = [
    {"id": 1, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie"},
    {"id": 2, "title": "Nhà Giả Kim", "author": "Paulo Coelho"}
]

# --- HÀM CHUẨN HÓA FORMAT PHẢN HỒI ---
def api_response(success, data=None, message="", status_code=200):
    """Đảm bảo mọi API đều trả về format: { success, message, data/error }"""
    response = {"success": success, "message": message}
    if success:
        response["data"] = data
    else:
        response["error"] = data # Chứa chi tiết lỗi nếu có
    return jsonify(response), status_code

# --- API ENDPOINTS ---

# Endpoint để phục vụ file swagger.yaml từ thư mục hiện tại ('.')
@app.route('/swagger.yaml')
def serve_swagger():
    return send_from_directory('.', 'swagger.yaml')

# 1. GET /books
@app.route('/books', methods=['GET'])
def get_books():
    return api_response(True, data=books, message="Lay danh sach thanh cong", status_code=200)

# 2. GET /books/{id}
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return api_response(False, message="Khong tim thay sach", status_code=404)
    
    return api_response(True, data=book, message="Lay thong tin thanh cong", status_code=200)

# 3. POST /books
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("author"):
        return api_response(False, message="Thieu title hoac author", status_code=400)
    new_book = {
        "id": max([b['id'] for b in books] + [0]) + 1,
        "title": data.get("title"),
        "author": data.get("author")
    }
    books.append(new_book)
    return api_response(True, data=new_book, message="Them sach thanh cong", status_code=201)

# 4. PUT /books/{id}
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return api_response(False, message="Khong tim thay sach nay", status_code=404)
    
    data = request.get_json()
    book.update({
        "title": data.get("title", book["title"]),
        "author": data.get("author", book["author"])
    })
    return api_response(True, data=book, message="Cap nhat sach thanh cong", status_code=200)

# 5. DELETE /books/{id}
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return api_response(False, message="Khong tim thay sach nay", status_code=404)
    
    books = [b for b in books if b["id"] != book_id]
    return api_response(True, data={"id": book_id}, message="Xoa sach thanh cong", status_code=200)
 