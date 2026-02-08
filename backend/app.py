"""Flask 主应用"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database import init_db, get_session, close_session
from models import Question, PracticeRecord, Category
from question_derivation import QuestionDerivationEngine
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# 初始化题目衍生引擎
derivation_engine = QuestionDerivationEngine()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """请求结束后关闭会话"""
    close_session()


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': '青海省行政执法公务员练习系统 API',
        'version': '1.0.0'
    })


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """获取题目列表"""
    session = get_session()
    try:
        # 获取查询参数
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        is_historical = request.args.get('is_historical')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 构建查询
        query = session.query(Question)
        
        if category:
            query = query.filter(Question.category == category)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if is_historical is not None:
            is_hist_bool = is_historical.lower() == 'true'
            query = query.filter(Question.is_historical == is_hist_bool)
        
        # 分页
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': {
                'questions': [q.to_dict() for q in questions],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """获取单个题目"""
    session = get_session()
    try:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': question.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@app.route('/api/questions/<int:question_id>/derive', methods=['POST'])
def derive_question(question_id):
    """衍生题目"""
    session = get_session()
    try:
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        # 获取衍生数量
        count = int(request.json.get('count', 3))
        
        # 生成衍生题目
        derived_questions_data = derivation_engine.derive_questions(question, count)
        
        # 保存到数据库
        saved_questions = []
        for q_data in derived_questions_data:
            new_question = Question(**q_data)
            session.add(new_question)
            session.flush()
            saved_questions.append(new_question.to_dict())
        
        session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'derived_questions': saved_questions
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取题目分类"""
    session = get_session()
    try:
        categories = session.query(Category).all()
        
        # 如果没有分类，返回默认分类
        if not categories:
            default_categories = [
                {'name': '行政法', 'description': '行政法律法规相关题目'},
                {'name': '刑法', 'description': '刑法相关题目'},
                {'name': '民法', 'description': '民法相关题目'},
                {'name': '行政处罚法', 'description': '行政处罚相关法律'},
                {'name': '行政强制法', 'description': '行政强制相关法律'},
                {'name': '行政许可法', 'description': '行政许可相关法律'},
                {'name': '综合知识', 'description': '综合法律知识'}
            ]
            return jsonify({
                'success': True,
                'data': default_categories
            })
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in categories]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@app.route('/api/practice/submit', methods=['POST'])
def submit_answer():
    """提交答案"""
    session = get_session()
    try:
        data = request.json
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        time_spent = data.get('time_spent', 0)
        
        if not question_id or not user_answer:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        # 获取题目
        question = session.query(Question).filter(Question.id == question_id).first()
        if not question:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404
        
        # 判断答案是否正确
        is_correct = user_answer.strip().upper() == question.answer.strip().upper()
        
        # 保存练习记录
        record = PracticeRecord(
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent=time_spent
        )
        session.add(record)
        session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'is_correct': is_correct,
                'correct_answer': question.answer,
                'explanation': question.explanation,
                'record_id': record.id
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取练习统计"""
    session = get_session()
    try:
        # 总题目数
        total_questions = session.query(Question).count()
        
        # 历年真题数
        historical_questions = session.query(Question).filter(
            Question.is_historical == True
        ).count()
        
        # 练习记录数
        total_practices = session.query(PracticeRecord).count()
        
        # 正确率
        if total_practices > 0:
            correct_practices = session.query(PracticeRecord).filter(
                PracticeRecord.is_correct == True
            ).count()
            accuracy = round(correct_practices / total_practices * 100, 2)
        else:
            accuracy = 0
        
        # 按分类统计
        categories_stat = {}
        questions = session.query(Question).all()
        for q in questions:
            if q.category not in categories_stat:
                categories_stat[q.category] = {
                    'total': 0,
                    'historical': 0,
                    'derived': 0
                }
            categories_stat[q.category]['total'] += 1
            if q.is_historical:
                categories_stat[q.category]['historical'] += 1
            else:
                categories_stat[q.category]['derived'] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_questions': total_questions,
                'historical_questions': historical_questions,
                'derived_questions': total_questions - historical_questions,
                'total_practices': total_practices,
                'accuracy': accuracy,
                'categories': categories_stat
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
