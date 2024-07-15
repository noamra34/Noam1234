from flask import Flask, request, jsonify, render_template, redirect,url_for, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pymongo import MongoClient
from os import environ 
import bcrypt
from dotenv import load_dotenv
import datetime
#
app = Flask(__name__)
load_dotenv()
DB_USR = environ.get('DB_USR')
DB_PSW = environ.get('DB_PSW')
DB_HOST = environ.get('DB_HOST')

MONGO_URI = (f"mongodb://{DB_USR}:{DB_PSW}@{DB_HOST}:27017/supermarket")
client = MongoClient(MONGO_URI)
db = client.supermarket

#config the session to the db
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = client
app.config["SESSION_MONGODB_DB"] = "supermarket"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"
Session(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invalid')
def invalid():
    return render_template('invalide.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        selected_products = []
        if (not (username and password and email)) and selected_products is None:
            return render_template('signup.html', message="all fields are required")
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        db.users.insert_one({'username': username, 'password': hashed_password, 'email': email})
        
        #store the user in session
        session["username"] = username
        return redirect(url_for('products'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.users.find_one({'username': username})
        if user is not None:
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                print("connected successfully")
                session['username'] = username
                return redirect(url_for('products'))
            else:
                return redirect('/invalid')
        return redirect('/signup')
    return render_template('/login.html')

@app.route('/products', methods=['GET'])
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    products_cursor = db.products.find({}, {"product_name": 1,'price': 1,"category": 1, "_id": 0})  # Fetch only product_name field
    products_list = [product for product in products_cursor]
    print("Fetched products:", products_list)
    return render_template('products.html', products=products_list, user=username)

@app.route('/add_products', methods=['POST'])
def add_products():
    if 'username' not in session:
        return redirect(url_for('login'))
    current_user = session['username']
    selected_products = request.form.getlist('selected_products')

    if not selected_products:
        return jsonify({"error": "No products selected"}), 400
    
    user = db.users.find_one({'username': current_user})
    if user: 
        total_amount = 0
        product_details = []
        for product_name in selected_products:
            product = db.products.find_one({"product_name": product_name}, {"product_name":1, "price":1, "_id":0})
            if product:
                product_details.append(product)
                total_amount += product['price']
    

# @app.route('/submit', methods=['POST'])
# @jwt_required()
# def submit():
#     current_user_id = get_jwt_identity()
#     selected_product_ids = request.form.getlist('selected_products')
    
#     # Retrieve user document from MongoDB
#     user = db.users.find_one({'_id': ObjectId(current_user_id)})
    
#     if not user:
#         return jsonify({'msg': 'User not found'}), 404
    
#     selected_products = []
#     total_price = 0.0
    
#     # Fetch details of selected products from MongoDB
#     for product_id in selected_product_ids:
#         product = db.products.find_one({'_id': ObjectId(product_id)})
#         if product:
#             selected_products.append({
#                 'product_name': product.get('product_name'),
#                 'price': product.get('price'),
#                 'category': product.get('category')
#             })
#             total_price += float(product.get('price', 0.0))
    
#     # Update selected_products field in user document
#     db.users.update_one({'_id': ObjectId(current_user_id)}, {'$set': {'selected_products': selected_products}})
    
#     return render_template('submit.html', selected_products=selected_products, total_price=total_price)



    
if __name__ == '__main__':
    app.run(debug=True)

