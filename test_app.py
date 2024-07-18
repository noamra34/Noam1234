# import pytest
# from flask import Flask
# from flask.testing import FlaskClient
# from pymongo import MongoClient
# from bson import ObjectId
# import mongomock
# import app


# @pytest.fixture
# def client(monkeypatch):
#     mock_client = mongomock.MongoClient()
#     mock_db = mock_client.supermarket
#     app.users_collection = mock_db.users
#     app.products_collection = mock_db.products
    
#     monkeypatch.setattr(app, "client", mock_client)

#     with app.app.test_client() as client:
#         yield client

# def test_signin(client):
#     post = {
#         'username': 'test_user',
#         'password': '123',
#         'email': 'm@gmail.com',
#         'phone_number': '1234567891'
#     }
#     result = app.users_collection.insert_one(post)

#     response = client.get('/login')
#     assert response.status_code == 200
#     app.users_collection.delete_one({'_id': result.inserted_id})



# # def signup(client):
# #     db = app.config["SESSION_MONGODB"].db
# #     signup_data = {
# #         'username': 'test_user',
# #         'password': 'password123',
# #         'email': 'test@example.com',
# #         'phone_number': '1234567890'
# #     }
# #     db.users.insert_one(signup_data)
# #     return signup_data

# # def test_signup(client):
# #     inserted_data = signup(client)
# #     assert inserted_data['username'] == 'test_user'
# #     assert inserted_data['email'] == 'test@example.com'

# # def signin(client):
# #     db = app.config["SESSION_MONGODB"].db
# #     signin_data = {
# #         'username': 'test_user',
# #         'password': 'password123'
# #     }
# #     db.users.insert_one(signin_data)
# #     db.users.find_one(signin_data)
# #     return signin_data

# # def test_signin(client):
# #     return_data = signin(client)
# #     db = app.config["SESSION_MONGODB"].db

# #     user_doc = db.users.find_one({'username': 'test_user'})
    
# #     # Perform assertions to verify the test
# #     assert user_doc is not None, "User document should exist in the database"
# #     assert user_doc == return_data, "Inserted data should match retrieved data"

# # def add_products(client):
# #     db = app.config["SESSION_MONGODB"].db
# #     insert_data = {
# #         'name': 'Sample Product',
# #         'price': 19.99,
# #         'kind': 'Electronics'
# #     }
# #     db.products.insert_one(insert_data)
# #       # Replace with the actual username or user ID
# #     db.users.insert_one(
# #         {'username': 'test_user'},
# #         {'$push': {'products': insert_data}}
# #     )
# #     return insert_data

# # def add_product_to_products(product_data):
# #     db = app.config["SESSION_MONGODB"].db
# #     result = db.products.insert_one(product_data)
# #     inserted_id = result.inserted_id  # Get the ObjectId of the inserted product
# #     return inserted_id

# # def test_products(client):
# #     db = app.config["SESSION_MONGODB"].db
# #     product_data1 = {
# #         'name': 'Sample Product',
# #         'price': 19.99,
# #         'kind': 'Electronics'
# #     }
# #     product_data2 = {
# #         'name': 'Sampleyyyy',
# #         'price': 19.20,
# #         'kind': 'Electron'
# #     }  

# #     username = 'test_user' 
# #     insert_one = db.users.insert_one({'username': username})
# #     product_id1 = add_product_to_products(product_data1)
# #     product_id2 = add_product_to_products(product_data2)

# #     cart = [
# #         {'_id': product_id1, **product_data1},
# #         {'_id': product_id2, **product_data2}
# #     ]

# #     db.users.update_one(
# #         {'username': username},
# #         {'$set': {'products': cart}}
# #     )
# #     user = db.users.find_one({'username': username})

# #     # Assertions to verify the products were added correctly
# #     assert user is not None, f"User '{username}' not found in the database"
# #     assert 'products' in user, f"User '{username}' does not have a 'products' field"
# #     assert any(product['_id'] == product_id1 for product in user['products']), "Product 1 not found in user's products"
# #     assert any(product['_id'] == product_id2 for product in user['products']), "Product 2 not found in user's products"

    
    
import pytest
from flask import session
from app import start_app  # Make sure to adjust the import based on your actual file structure
import mongomock
from bson.objectid import ObjectId
import bcrypt

@pytest.fixture
def client(monkeypatch):
    # Setup: initialize app with mongomock client
    mock_client = mongomock.MongoClient()

    def mock_start_app(if_testing=None):
        if if_testing is None:
            if_testing = {}
        if_testing['MONGO_CLIENT'] = mock_client  # Set the mongomock client
        return start_app(if_testing=if_testing)

    monkeypatch.setattr('app.start_app', mock_start_app)
    
    # Initialize the app with the mock_start_app function
    app = mock_start_app({'MONGO_CLIENT': mock_client})
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            # Create collections and insert initial data for testing
            db = app.db
            db.users.insert_one({
                '_id': ObjectId('60f6e7d7b1d41c5f2cae8b79'),
                'username': 'testuser',
                'password': bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()),
                'email': 'testuser@example.com',
                'cart': []
            })
            db.products.insert_many([
                {'_id': ObjectId('60f6e7d7b1d41c5f2cae8b80'), 'name': 'Product1', 'price': 10, 'kind': 'type1'},
                {'_id': ObjectId('60f6e7d7b1d41c5f2cae8b81'), 'name': 'Product2', 'price': 20, 'kind': 'type2'}
            ])
        yield client
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data  # Adjust this assertion based on your actual index.html content

if __name__ == "__main__":
    pytest.main()