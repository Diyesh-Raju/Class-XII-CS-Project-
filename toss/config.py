import os

class Config:
    # 1. Instructs Flask to automatically create your local database inside a database/ folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'database', 
        'mileage_wars.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. Cryptographic encryption signature token to guard incoming JWT session strings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'mileage-wars-super-secret-key-4488')
    