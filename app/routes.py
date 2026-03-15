# app/routes.py
from flask import Blueprint, request, jsonify, current_app
from app.models import db
from app.models.analysis import AnalysisJob
import uuid
import datetime
import os
import base64
import threading
import random
import time

api = Blueprint('api', __name__)

# 模拟的代际群体数据
GENERATIONS = [
    ("Silent Generation", 77, 95),
    ("Baby Boomer", 58, 76),
    ("Generation X", 43, 57),
    ("Millennial", 27, 42),
    ("Generation Z", 11, 26),
    ("Generation Alpha", 0, 10)
]

def analyze_image_async(job_id, image_path):
    """后台处理图像 - 模拟ML分析"""
    with current_app.app_context():
        try:
            # 获取任务
            job = db.session.get(AnalysisJob, job_id)
            if not job:
                return
            
            # 更新状态为处理中
            job.status = 'processing'
            job.started_at = datetime.datetime.now()
            db.session.commit()
            
            # 模拟处理时间（随机1-3秒）
            time.sleep(random.uniform(1, 3))
            
            # 随机生成结果（模拟ML输出）
            generation_idx = random.randint(0, len(GENERATIONS) - 1)
            generation, min_age, max_age = GENERATIONS[generation_idx]
            
            # 生成模拟年龄和置信度
            age_approx = random.randint(min_age, max_age)
            confidence = random.uniform(0.7, 0.99)
            
            # 更新结果
            job.status = 'completed'
            job.generation = generation
            job.confidence = round(confidence, 2)
            job.age_approx = age_approx
            job.completed_at = datetime.datetime.now()
            db.session.commit()
            
            print(f"✅ Job {job_id} completed: {generation} ({confidence:.2f})")
            
        except Exception as e:
            print(f"❌ Error processing job {job_id}: {e}")
            job.status = 'failed'
            db.session.commit()

@api.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

@api.route('/analyse', methods=['POST'])
def create_analysis():
    """提交新的分析任务"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'Missing image data'}), 400
        
        # 生成唯一ID
        job_id = str(uuid.uuid4())
        
        # 解码base64图片
        try:
            image_data = base64.b64decode(data['image'])
        except:
            return jsonify({'error': 'Invalid base64 image'}), 400
        
        # 保存图片到文件系统
        filename = f"{job_id}.jpg"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # 创建分析任务记录
        job = AnalysisJob(
            id=job_id,
            client_id=data.get('client_id', 'unknown'),
            urgent=data.get('urgent', False),
            image_path=filepath,
            status='pending'
        )
        
        db.session.add(job)
        db.session.commit()
        
        # 启动后台线程处理图片
        thread = threading.Thread(
            target=analyze_image_async,
            args=(job_id, filepath)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'id': job_id,
            'status': 'pending',
            'message': 'Analysis started'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """获取分析结果"""
    job = db.session.get(AnalysisJob, job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict())

@api.route('/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    # 总任务数
    total = AnalysisJob.query.count()
    
    # 按状态统计
    pending = AnalysisJob.query.filter_by(status='pending').count()
    processing = AnalysisJob.query.filter_by(status='processing').count()
    completed = AnalysisJob.query.filter_by(status='completed').count()
    failed = AnalysisJob.query.filter_by(status='failed').count()
    
    # 平均置信度
    avg_conf = db.session.query(
        db.func.avg(AnalysisJob.confidence)
    ).filter(AnalysisJob.status == 'completed').scalar() or 0
    
    # 按代际群体统计
    generation_stats = db.session.query(
        AnalysisJob.generation,
        db.func.count(AnalysisJob.generation)
    ).filter(
        AnalysisJob.status == 'completed',
        AnalysisJob.generation.isnot(None)
    ).group_by(AnalysisJob.generation).all()
    
    breakdown = {gen: count for gen, count in generation_stats}
    
    return jsonify({
        'total_analyses': total,
        'pending_analyses': pending,
        'processing_analyses': processing,
        'completed_analyses': completed,
        'failed_analyses': failed,
        'average_confidence': round(float(avg_conf), 2),
        'generation_breakdown': breakdown
    })

@api.route('/results', methods=['GET'])
def get_results():
    """批量查询结果 - 支持过滤"""
    query = AnalysisJob.query
    
    # 按client_id过滤
    client_id = request.args.get('client_id')
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    # 按状态过滤
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # 按紧急程度过滤
    urgent = request.args.get('urgent')
    if urgent is not None:
        is_urgent = urgent.lower() == 'true'
        query = query.filter_by(urgent=is_urgent)
    
    # 排序和限制
    limit = request.args.get('limit', 100, type=int)
    jobs = query.order_by(AnalysisJob.created_at.desc()).limit(limit).all()
    
    return jsonify([job.to_dict() for job in jobs])