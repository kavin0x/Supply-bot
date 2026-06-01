from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from datetime import datetime
import json
import pandas as pd
import numpy as np
from backend.ai.features import (
    HashEmbeddingModel,
    embedding_payload,
    text_from_fields,
    predict_demand as ai_predict_demand,
    search_inventory as ai_search_inventory,
    generate_inventory_report as ai_generate_inventory_report,
    process_data as ai_process_data,
    fine_tune_model as ai_fine_tune_model
)
import os
from dotenv import load_dotenv
import asyncio
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import tempfile
from pathlib import Path

load_dotenv()

app = Flask(__name__)
# Enable CORS for the React frontend, allowing credentials (cookies)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Important for CORS cookies
use_secure_cookies = os.getenv('SUPPLYBOT_USE_SECURE_COOKIES', '').lower() in {'1', 'true', 'yes'}
if use_secure_cookies:
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
embedding_model = HashEmbeddingModel()

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

# GPT model logic has been moved to backend.ai.features

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

def get_json_data():
    return request.get_json(silent=True) or {}

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category
        }

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'in' or 'out'
    date = db.Column(db.DateTime, default=datetime.utcnow)


class ProductEmbedding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)
    source_text = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_vector(self):
        return np.array(json.loads(self.embedding_json), dtype=np.float32)


def sync_product_embedding(product):
    source_text = text_from_fields(
        product.name,
        product.description,
        product.category,
        product.quantity,
        product.price,
    )
    vector_payload = embedding_payload(embedding_model.embed(source_text))
    embedding = ProductEmbedding.query.filter_by(product_id=product.id).first()
    if embedding is None:
        embedding = ProductEmbedding(
            product_id=product.id,
            source_text=source_text,
            embedding_json=json.dumps(vector_payload),
        )
        db.session.add(embedding)
    else:
        embedding.source_text = source_text
        embedding.embedding_json = json.dumps(vector_payload)
    return embedding

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- API Routes ---

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "username": current_user.username})
    return jsonify({"authenticated": False})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = get_json_data()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    user = User.query.filter_by(username=username).first()
    if user and (check_password_hash(user.password, password) or user.password == password):
        login_user(user)
        return jsonify({"success": True, "message": "Logged in successfully"})
    return jsonify({"success": False, "error": "Invalid username or password"}), 401

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = get_json_data()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": "Username already exists"}), 409

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({"success": True, "message": "Account created successfully", "username": user.username}), 201

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"success": True})

@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products', methods=['POST'])
@login_required
def add_product():
    data = request.json
    try:
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            quantity=int(data.get('quantity', 0)),
            price=float(data['price']),
            category=data['category']
        )
        db.session.add(product)
        db.session.commit()
        
        # Initial transaction
        transaction = InventoryTransaction(
            product_id=product.id,
            quantity=product.quantity,
            transaction_type='in'
        )
        db.session.add(transaction)
        db.session.commit()
        sync_product_embedding(product)
        db.session.commit()
        
        return jsonify({"success": True, "product": product.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<int:product_id>', methods=['POST'])
@login_required
def update_inventory(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json
    quantity_change = int(data['quantity'])
    transaction_type = data['type']
    
    if transaction_type == 'in':
        product.quantity += quantity_change
    else:
        if product.quantity < quantity_change:
            return jsonify({"success": False, "error": "Not enough stock available!"}), 400
        product.quantity -= quantity_change
    
    transaction = InventoryTransaction(
        product_id=product.id,
        quantity=quantity_change,
        transaction_type=transaction_type
    )
    db.session.add(transaction)
    db.session.commit()
    sync_product_embedding(product)
    db.session.commit()
    return jsonify({"success": True, "product": product.to_dict()})

@app.route('/api/ai/inject-context', methods=['POST'])
@login_required
@async_route
async def inject_context():
    try:
        success, message = await ai_fine_tune_model()
        return jsonify({"success": success, "message": message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ai/predict/<int:product_id>', methods=['GET'])
@login_required
@async_route
async def predict_demand(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = product.to_dict()
    
    # Get recent transactions for this product to provide context to the LLM
    transactions = InventoryTransaction.query.filter_by(product_id=product.id).order_by(InventoryTransaction.date.desc()).limit(10).all()
    tx_data = [{"date": t.date.strftime('%Y-%m-%d'), "transaction_type": t.transaction_type, "quantity": t.quantity} for t in transactions]
    
    prediction, error = await ai_predict_demand(product_data, tx_data)
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({'prediction': prediction})

@app.route('/api/ai/search', methods=['POST'])
@login_required
@async_route
async def search_inventory():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    # Provide all products as context to the LLM
    all_products = [p.to_dict() for p in Product.query.all()]
    stored_embeddings = {
        embedding.product_id: embedding.to_vector().tolist()
        for embedding in ProductEmbedding.query.all()
    }
    
    result, error = await ai_search_inventory(query, all_products, stored_embeddings=stored_embeddings)
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({'result': result})

@app.route('/api/ai/report', methods=['GET'])
@login_required
@async_route
async def generate_report():
    # Provide context to the LLM
    products = [p.to_dict() for p in Product.query.all()]
    transactions = InventoryTransaction.query.order_by(InventoryTransaction.date.desc()).limit(50).all()
    tx_data = [{"product_id": t.product_id, "transaction_type": t.transaction_type, "quantity": t.quantity, "date": t.date.strftime('%Y-%m-%d')} for t in transactions]
    
    report, error = await ai_generate_inventory_report(products, tx_data)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"report": report})

@app.route('/api/upload', methods=['POST'])
@login_required
@async_route
async def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        data_type = request.form.get('data_type')
        date_format = request.form.get('date_format', '%Y-%m-%d')
        
        result = await ai_process_data(file_path, data_type, date_format)
        os.unlink(file_path)
        
        if result.success:
            await ai_fine_tune_model()
            return jsonify({"success": True, "message": "Data processed and context injected"})
        else:
            return jsonify({"error": result.message}), 400
            
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
