import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://ride_share_1pm4_user:LNDcV4qRiIXE7ins39VL3Ws3iuWZn5WQ@dpg-csdqigt6l47c73dfrmi0-a.oregon-postgres.render.com/ride_share_1pm4?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
