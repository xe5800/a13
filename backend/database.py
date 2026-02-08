"""数据库管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
from config import Config

# 创建引擎
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=Config.DEBUG)

# 创建会话
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)
    print("数据库初始化完成！")


def get_session():
    """获取数据库会话"""
    return Session()


def close_session():
    """关闭会话"""
    Session.remove()
