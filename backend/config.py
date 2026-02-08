"""配置文件"""
import os

class Config:
    """应用配置"""
    
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///qinghai_law_practice.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS 配置
    CORS_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080']
    
    # 题目衍生配置
    DERIVATION_CONFIG = {
        'min_similarity': 0.7,  # 衍生题目最小相似度
        'max_derivations': 5,   # 每个题目最多衍生数量
        'difficulty_range': 1    # 难度调整范围
    }
