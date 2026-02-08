"""初始化数据库并导入示例数据"""
import json
import os
from database import init_db, get_session
from models import Question, Category

def load_sample_questions():
    """加载示例题目"""
    session = get_session()
    try:
        # 检查数据是否已存在
        if session.query(Question).count() > 0:
            print("数据库已包含题目，跳过导入")
            return
        
        # 读取示例题目
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_questions.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            # 导入题目
            for q_data in questions_data:
                question = Question(**q_data)
                session.add(question)
            
            session.commit()
            print(f"成功导入 {len(questions_data)} 道题目")
        else:
            print(f"示例数据文件不存在: {data_file}")
    except Exception as e:
        session.rollback()
        print(f"导入数据失败: {e}")
    finally:
        session.close()


def create_default_categories():
    """创建默认分类"""
    session = get_session()
    try:
        # 检查是否已有分类
        if session.query(Category).count() > 0:
            print("分类已存在，跳过创建")
            return
        
        categories = [
            {'name': '行政法', 'description': '行政法律法规相关题目'},
            {'name': '刑法', 'description': '刑法相关题目'},
            {'name': '民法', 'description': '民法相关题目'},
            {'name': '行政处罚法', 'description': '行政处罚相关法律'},
            {'name': '行政强制法', 'description': '行政强制相关法律'},
            {'name': '行政许可法', 'description': '行政许可相关法律'},
            {'name': '综合知识', 'description': '综合法律知识'}
        ]
        
        for cat_data in categories:
            category = Category(**cat_data)
            session.add(category)
        
        session.commit()
        print(f"成功创建 {len(categories)} 个分类")
    except Exception as e:
        session.rollback()
        print(f"创建分类失败: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    print("开始初始化数据库...")
    init_db()
    print("创建默认分类...")
    create_default_categories()
    print("导入示例题目...")
    load_sample_questions()
    print("数据库初始化完成！")
