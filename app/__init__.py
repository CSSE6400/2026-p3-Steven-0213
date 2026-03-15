from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
 
# app/__init__.py
from flask import Flask
import os

def create_app(config_overrides=None):
    app = Flask(__name__)
    
    # 配置数据库 - 使用SQLite（第一阶段）
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ageoverflow.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 上传配置
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    if config_overrides:
        app.config.update(config_overrides)
    
    # 初始化数据库
    from app.models import db
    db.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # 注册蓝图
    from app.routes import api
    app.register_blueprint(api, url_prefix='/api/v1')
    
    return app