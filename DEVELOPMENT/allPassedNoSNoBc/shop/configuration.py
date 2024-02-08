from datetime import timedelta
import os

# os.environ['DATABASE_URL']
class Configuration(): #{os.environ["DATABASE_URL"]}
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@localhost:3307/shop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'JWT_SECRET_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes = 60)
    #JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)