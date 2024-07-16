import pytest
from flask_application import app, client as production_client
from mongomock import MongoClient as MockClient

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = MockClient()
    app.config["SESSION_MONGODB_DB"] = "test_db"  # Use a test database for sessions
    app.config["SESSION_MONGODB_COLLECT"] = "test_sessions"  # Use a test collection for sessions
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def signup(client):
    db = app.config["SESSION_MONGODB"].db
    signup_data = {
        'username': 'test_user',
        'password': 'password123',
        'email': 'test@example.com',
        'phone_number': '1234567890'
    }
    db.users.insert_one(signup_data)
    return signup_data

def test_signup(client):
    inserted_data = signup(client)
    assert inserted_data['username'] == 'test_user'
    assert inserted_data['email'] == 'test@example.com'

def signin(client):
    db = app.config["SESSION_MONGODB"].db
    signin_data = {
        'username': 'test_user',
        'password': 'password123'
    }
    db.users.insert_one(signin_data)
    db.users.find_one(signin_data)
    return signin_data

def test_signin(client):
    return_data = signin(client)
    db = app.config["SESSION_MONGODB"].db

    user_doc = db.users.find_one({'username': 'test_user'})
    
    # Perform assertions to verify the test
    assert user_doc is not None, "User document should exist in the database"
    assert user_doc == return_data, "Inserted data should match retrieved data"

def add_products(client):
    db = app.config["SESSION_MONGODB"].db
    insert_data = {
        'name': 'Sample Product',
        'price': 19.99,
        'kind': 'Electronics'
    }
    db.products.insert_one(insert_data)
      # Replace with the actual username or user ID
    db.users.insert_one(
        {'username': 'test_user'},
        {'$push': {'products': insert_data}}
    )
    return insert_data

def add_product_to_products(product_data):
    db = app.config["SESSION_MONGODB"].db
    result = db.products.insert_one(product_data)
    inserted_id = result.inserted_id  # Get the ObjectId of the inserted product
    return inserted_id

def test_products(client):
    db = app.config["SESSION_MONGODB"].db
    product_data1 = {
        'name': 'Sample Product',
        'price': 19.99,
        'kind': 'Electronics'
    }
    product_data2 = {
        'name': 'Sampleyyyy',
        'price': 19.20,
        'kind': 'Electron'
    }  

    username = 'test_user' 
    insert_one = db.users.insert_one({'username': username})
    product_id1 = add_product_to_products(product_data1)
    product_id2 = add_product_to_products(product_data2)

    cart = [
        {'_id': product_id1, **product_data1},
        {'_id': product_id2, **product_data2}
    ]

    db.users.update_one(
        {'username': username},
        {'$set': {'products': cart}}
    )
    user = db.users.find_one({'username': username})

    # Assertions to verify the products were added correctly
    assert user is not None, f"User '{username}' not found in the database"
    assert 'products' in user, f"User '{username}' does not have a 'products' field"
    assert any(product['_id'] == product_id1 for product in user['products']), "Product 1 not found in user's products"
    assert any(product['_id'] == product_id2 for product in user['products']), "Product 2 not found in user's products"

    
    