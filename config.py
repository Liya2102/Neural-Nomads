import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, "instance")

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'alumni.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"

