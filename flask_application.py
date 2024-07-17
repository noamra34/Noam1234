from flask import Flask, request, jsonify, render_template, redirect,url_for, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from pymongo import MongoClient
from os import environ 
import bcrypt
from dotenv import load_dotenv
import datetime
from bson.objectid import ObjectId
import mongomock
#
load_dotenv()
DB_USR = environ.get('DB_USR')
DB_PSW = environ.get('DB_PSW')
DB_HOST = environ.get('DB_HOST')
DB_NAME = environ.get('DB_NAME')
SESSION_KEY = environ.get('SESSION_KEY')
MONGO_URI = (f"mongodb://{DB_USR}:{DB_PSW}@{DB_HOST}:27017/supermarket")
client = MongoClient(MONGO_URI)
db = client.supermarket
app = Flask(__name__)
is_testing = True
if is_testing:
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = client
    app.config["SESSION_MONGODB_DB"] = DB_NAME
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"
    Session(app)     
#config the session to the db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invalid')
def invalid():
    return render_template('invalide.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        if not (username and password and email):
            return render_template('signup.html', message="All fields are required")
        
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            return render_template('signup.html', message="Email already registered. Please use a different email.")
        
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        user_id = db.users.insert_one({'username': username, 'password': hashed_password, 'email': email, 'phone_number': phone_number, 'cart': []})
        
        # Store the user in session
        session["user_id"] = str(user_id.inserted_id)
        session["username"] = username
        
        # Redirect to the 'products' endpoint
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
                session['user_id'] = str(user['_id'])
                session['username'] = username
                return redirect(url_for('products'))
            else:
                return redirect('invalid')
        return redirect('signup')
    return render_template('login.html')

#products
@app.route('/products', methods=['GET'])
def products():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    products_cursor = db.products.find({}, {"name": 1,'price': 1,"kind": 1, "_id": 1})  # Fetch only product_name field
    products_list = [product for product in products_cursor]
    print("Fetched products:", products_list)

    return render_template('products.html', products=products_list, user=username)

@app.route('/add_products', methods=['POST'])
def add_products():
    if 'username' not in session:
        return redirect(url_for('login'))
    

    current_user_id = session['user_id']
    cart = []
    products_added = None
    alist = request.form.items()
    for product_id, quantity  in alist:
        if product_id.startswith('quantity_') and int(quantity) > 0:
            product_id = product_id.replace('quantity_','')
            product = db.products.find_one({"_id": ObjectId(product_id)})           
            if product:
                product_price = product.get('price', 1)
                product['quantity'] = int(quantity)
                cart.append({"product_id": product_id, "quantity": product['quantity'], "price": product_price})
                products_added = True
    
    if not products_added:
        return jsonify({"error": "No products selected"}), 400
        
    #update the cart collection:
    db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$set': {'cart':cart}},
        upsert=True
    )
    return redirect(url_for('cash_register'))


@app.route('/cash_register')
def cash_register():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_user_id = session['user_id']
    
    # Fetch cart details from the database
    user_cart = db.users.find_one({'_id': ObjectId(current_user_id)})
    if not user_cart or 'cart' not in user_cart:
        return render_template('cash_register.html', products=[], total_amount=0)
    
    cart_products = user_cart['cart']
    products_details = []
    total_amount = 0
    
    # Retrieve details for each product in the cart
    for item in cart_products:
        product_id = item['product_id']
        quantity = item.get('quantity', 1)  # Default to 1 if quantity is not specified
        
        # Fetch product details from the products collection
        product_details = db.products.find_one({"_id": ObjectId(product_id)})
        if product_details:
            product_name = product_details.get('name', 'Unknown Product')
            product_price = product_details.get('price', 0)
            total_amount += product_price * quantity
            
            # Add product details to the list
            products_details.append({
                'product_id': product_id,
                'name': product_name,
                'price': product_price,
                'quantity': quantity
            })
    
    return render_template('cash_register.html', products=products_details, total_amount=total_amount)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session variables
    return redirect(('/'))

            
                    
            

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
    app.run(host="0.0.0.0", port="5000", debug=True)

