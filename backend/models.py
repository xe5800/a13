"""数据模型定义"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Question(Base):
    """题目模型"""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)  # single_choice, multiple_choice, true_false, essay
    category = Column(String(100), nullable=False)  # 行政法、刑法、民法等
    subcategory = Column(String(100))  # 子分类
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    question = Column(Text, nullable=False)  # 题目内容
    options = Column(Text)  # JSON格式的选项
    answer = Column(String(200), nullable=False)  # 答案
    explanation = Column(Text)  # 答案解析
    is_historical = Column(Boolean, default=False)  # 是否历年真题
    year = Column(Integer)  # 年份
    source_question_id = Column(Integer, ForeignKey('questions.id'))  # 衍生题的原题ID
    derivation_method = Column(String(50))  # 衍生方法
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    derived_questions = relationship('Question', backref='source_question', remote_side=[id])
    practice_records = relationship('PracticeRecord', back_populates='question')
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'subcategory': self.subcategory,
            'difficulty': self.difficulty,
            'question': self.question,
            'options': json.loads(self.options) if self.options else None,
            'answer': self.answer,
            'explanation': self.explanation,
            'is_historical': self.is_historical,
            'year': self.year,
            'source_question_id': self.source_question_id,
            'derivation_method': self.derivation_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PracticeRecord(Base):
    """练习记录模型"""
    __tablename__ = 'practice_records'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    user_answer = Column(String(200))  # 用户答案
    is_correct = Column(Boolean)  # 是否正确
    time_spent = Column(Integer)  # 用时（秒）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    question = relationship('Question', back_populates='practice_records')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category(Base):
    """题目分类模型"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    question_count = Column(Integer, default=0)
    
    # 关系
    subcategories = relationship('Category', backref='parent', remote_side=[id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'question_count': self.question_count
        }
