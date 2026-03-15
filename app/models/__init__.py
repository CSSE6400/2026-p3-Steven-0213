# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入模型，方便其他地方使用
from .analysis import AnalysisJob
 
