from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pandas as pd
import numpy as np
from gpt_model import GPTInventoryModel
import os
from dotenv import load_dotenv
import asyncio
from functools import wraps
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize GPT model
gpt_model = GPTInventoryModel()

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

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

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'in' or 'out'
    date = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('transactions', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # In production, use proper password hashing
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = int(request.form.get('quantity'))
        price = float(request.form.get('price'))
        category = request.form.get('category')
        
        product = Product(
            name=name,
            description=description,
            quantity=quantity,
            price=price,
            category=category
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Record the initial inventory transaction
        transaction = InventoryTransaction(
            product_id=product.id,
            quantity=quantity,
            transaction_type='in'
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash('Product added successfully!')
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/update_inventory/<int:product_id>', methods=['POST'])
@login_required
def update_inventory(product_id):
    product = Product.query.get_or_404(product_id)
    quantity_change = int(request.form.get('quantity'))
    transaction_type = request.form.get('type')
    
    if transaction_type == 'in':
        product.quantity += quantity_change
    else:
        if product.quantity < quantity_change:
            flash('Not enough stock available!')
            return redirect(url_for('index'))
        product.quantity -= quantity_change
    
    transaction = InventoryTransaction(
        product_id=product.id,
        quantity=quantity_change,
        transaction_type=transaction_type
    )
    
    db.session.add(transaction)
    db.session.commit()
    flash('Inventory updated successfully!')
    return redirect(url_for('index'))

@app.route('/fine_tune_model', methods=['POST'])
@login_required
@async_route
async def fine_tune_model():
    try:
        # Get all transactions
        transactions = InventoryTransaction.query.all()
        
        # Prepare training data
        training_data = await gpt_model.prepare_training_data(transactions)
        
        # Fine-tune the model
        success, message = await gpt_model.fine_tune_model(training_data)
        
        if success:
            flash('Model fine-tuning started successfully!')
        else:
            flash(f'Error during fine-tuning: {message}')
            
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/predict_demand/<int:product_id>')
@login_required
@async_route
async def predict_demand(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Prepare product data
    product_data = {
        'name': product.name,
        'category': product.category,
        'quantity': product.quantity,
        'price': product.price
    }
    
    # Get prediction from fine-tuned model
    prediction, error = await gpt_model.predict_demand(product_data)
    
    if error:
        return jsonify({'error': error})
    
    return jsonify({
        'prediction': prediction
    })

@app.route('/search_inventory', methods=['POST'])
@login_required
@async_route
async def search_inventory():
    query = request.form.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'})
    
    result, error = await gpt_model.search_inventory(query)
    
    if error:
        return jsonify({'error': error})
    
    return jsonify({
        'result': result
    })

@app.route('/generate_report')
@login_required
@async_route
async def generate_report():
    try:
        report, error = await gpt_model.generate_inventory_report()
        
        if error:
            flash(f'Error generating report: {error}')
            return redirect(url_for('index'))
        
        return render_template('report.html', report=report)
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/upload_data', methods=['GET', 'POST'])
@login_required
@async_route
async def upload_data():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            data_type = request.form.get('data_type')
            date_format = request.form.get('date_format')
            
            # Process the uploaded file
            success, result = await gpt_model.process_uploaded_data(file_path, data_type, date_format)
            
            if success:
                # Start fine-tuning with the processed data
                fine_tune_success, fine_tune_message = await gpt_model.fine_tune_model(result)
                
                if fine_tune_success:
                    flash('Data uploaded and fine-tuning started successfully')
                else:
                    flash(f'Data uploaded but fine-tuning failed: {fine_tune_message}')
            else:
                flash(f'Error processing data: {result}')
            
            # Clean up the uploaded file
            os.unlink(file_path)
            
            return redirect(url_for('index'))
    
    return render_template('upload_data.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

