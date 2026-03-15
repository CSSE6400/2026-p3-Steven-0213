# app/models/analysis.py
import datetime
from . import db

class AnalysisJob(db.Model):
    """图像分析任务模型"""
    __tablename__ = 'analysis_jobs'
    
    # 任务ID (使用UUID)
    id = db.Column(db.String(36), primary_key=True)
    
    # 客户信息
    client_id = db.Column(db.String(80), nullable=False)
    urgent = db.Column(db.Boolean, nullable=False, default=False)
    
    # 图片信息
    image_path = db.Column(db.String(200), nullable=False)
    
    # 状态: pending, processing, completed, failed
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # 分析结果
    generation = db.Column(db.String(50), nullable=True)  # 代际群体
    confidence = db.Column(db.Float, nullable=True)       # 置信度
    age_approx = db.Column(db.Integer, nullable=True)     # 估算年龄
    
    # 时间戳
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)
    
    def to_dict(self):
        """转换为字典格式（用于API响应）"""
        result = {
            'id': self.id,
            'client_id': self.client_id,
            'urgent': self.urgent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        # 如果已完成，包含结果
        if self.status == 'completed':
            result.update({
                'generation': self.generation,
                'confidence': self.confidence,
                'age_approx': self.age_approx,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            })
        
        return result
    
    def __repr__(self):
        return f'<AnalysisJob {self.id} {self.status}>'