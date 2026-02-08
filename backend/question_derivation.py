"""题目衍生引擎 - 基于历年真题生成练习题"""
import json
import re
import jieba
import random
from typing import List, Dict, Any
from models import Question


class QuestionDerivationEngine:
    """题目衍生引擎"""
    
    def __init__(self):
        """初始化"""
        # 行政执法相关关键词库
        self.law_entities = {
            '行政机关': ['执法部门', '政府部门', '行政主体', '执法机构'],
            '行政处罚': ['警告', '罚款', '吊销许可证', '责令停产停业'],
            '行政强制': ['行政强制执行', '行政强制措施', '强制拆除'],
            '行政许可': ['审批', '核准', '登记', '行政批准'],
            '行政复议': ['行政诉讼', '行政申诉', '行政救济'],
            '公民': ['当事人', '相对人', '行政相对人', '管理相对人'],
            '期限': ['时限', '时间', '期间', '日期']
        }
        
        # 场景库
        self.scenarios = [
            '食品安全监管', '环境保护执法', '交通管理', '市场监管',
            '安全生产监管', '城市管理', '消防监管', '卫生监督'
        ]
        
        # 数字替换范围
        self.number_ranges = {
            '期限': (3, 60),  # 天数
            '金额': (1000, 100000),  # 罚款金额
            '人数': (1, 50)
        }
    
    def derive_questions(self, original_question: Question, count: int = 3) -> List[Dict[str, Any]]:
        """
        从原始题目衍生新题目
        
        Args:
            original_question: 原始题目
            count: 衍生题目数量
            
        Returns:
            衍生题目列表
        """
        derived = []
        
        # 策略1: 关键词替换
        if len(derived) < count:
            q = self._keyword_replacement(original_question)
            if q:
                derived.append(q)
        
        # 策略2: 数字替换
        if len(derived) < count:
            q = self._number_replacement(original_question)
            if q:
                derived.append(q)
        
        # 策略3: 逻辑反转
        if len(derived) < count:
            q = self._logic_inversion(original_question)
            if q:
                derived.append(q)
        
        # 策略4: 场景迁移
        while len(derived) < count:
            q = self._scenario_transfer(original_question)
            if q:
                derived.append(q)
            else:
                break
        
        return derived[:count]
    
    def _keyword_replacement(self, question: Question) -> Dict[str, Any]:
        """关键词替换策略"""
        new_question = question.question
        new_options = json.loads(question.options) if question.options else None
        new_explanation = question.explanation
        
        # 替换题目中的关键词
        for entity_type, replacements in self.law_entities.items():
            for original in [entity_type] + replacements:
                if original in new_question:
                    replacement = random.choice([r for r in replacements if r != original])
                    new_question = new_question.replace(original, replacement, 1)
                    if new_explanation:
                        new_explanation = new_explanation.replace(original, replacement)
                    break
        
        # 替换选项中的关键词
        if new_options:
            new_options = [self._replace_keywords_in_text(opt) for opt in new_options]
        
        if new_question != question.question:
            return {
                'type': question.type,
                'category': question.category,
                'subcategory': question.subcategory,
                'difficulty': question.difficulty,
                'question': new_question,
                'options': json.dumps(new_options, ensure_ascii=False) if new_options else None,
                'answer': question.answer,
                'explanation': new_explanation,
                'is_historical': False,
                'year': None,
                'source_question_id': question.id,
                'derivation_method': 'keyword_replacement'
            }
        return None
    
    def _number_replacement(self, question: Question) -> Dict[str, Any]:
        """数字替换策略"""
        new_question = question.question
        new_explanation = question.explanation
        
        # 查找题目中的数字
        numbers = re.findall(r'\d+', new_question)
        if numbers:
            for num_str in numbers:
                num = int(num_str)
                # 根据数字大小选择替换范围
                if num < 100:  # 可能是天数
                    new_num = random.randint(max(1, num - 10), num + 10)
                elif num < 1000:  # 可能是金额（元）
                    new_num = random.randint(max(100, num - 200), num + 200)
                else:  # 大额金额
                    new_num = int(num * random.uniform(0.8, 1.2))
                
                new_question = new_question.replace(num_str, str(new_num), 1)
                if new_explanation:
                    new_explanation = new_explanation.replace(num_str, str(new_num), 1)
                break  # 只替换第一个数字
        
        if new_question != question.question:
            new_options = json.loads(question.options) if question.options else None
            return {
                'type': question.type,
                'category': question.category,
                'subcategory': question.subcategory,
                'difficulty': question.difficulty,
                'question': new_question,
                'options': json.dumps(new_options, ensure_ascii=False) if new_options else None,
                'answer': question.answer,
                'explanation': new_explanation,
                'is_historical': False,
                'year': None,
                'source_question_id': question.id,
                'derivation_method': 'number_replacement'
            }
        return None
    
    def _logic_inversion(self, question: Question) -> Dict[str, Any]:
        """逻辑反转策略"""
        new_question = question.question
        
        # 简单的逻辑反转词替换
        inversions = {
            '正确': '错误',
            '合法': '违法',
            '应当': '不应当',
            '可以': '不可以',
            '必须': '禁止',
            '符合': '违反'
        }
        
        for original, inverted in inversions.items():
            if original in new_question:
                new_question = new_question.replace(original, inverted, 1)
                break
        
        if new_question != question.question:
            # 如果是判断题，答案也要反转
            new_answer = question.answer
            if question.type == 'true_false':
                new_answer = '错误' if question.answer == '正确' else '正确'
            
            new_options = json.loads(question.options) if question.options else None
            return {
                'type': question.type,
                'category': question.category,
                'subcategory': question.subcategory,
                'difficulty': question.difficulty,
                'question': new_question,
                'options': json.dumps(new_options, ensure_ascii=False) if new_options else None,
                'answer': new_answer,
                'explanation': question.explanation,
                'is_historical': False,
                'year': None,
                'source_question_id': question.id,
                'derivation_method': 'logic_inversion'
            }
        return None
    
    def _scenario_transfer(self, question: Question) -> Dict[str, Any]:
        """场景迁移策略"""
        new_question = question.question
        
        # 尝试替换场景关键词
        for scenario in self.scenarios:
            scenario_words = scenario.split('、')
            for word in scenario_words:
                if len(word) > 2 and word in new_question:
                    # 选择不同的场景
                    new_scenario = random.choice([s for s in self.scenarios if s != scenario])
                    new_question = new_question.replace(word, new_scenario.split('、')[0], 1)
                    break
        
        if new_question != question.question:
            new_options = json.loads(question.options) if question.options else None
            return {
                'type': question.type,
                'category': question.category,
                'subcategory': question.subcategory,
                'difficulty': question.difficulty,
                'question': new_question,
                'options': json.dumps(new_options, ensure_ascii=False) if new_options else None,
                'answer': question.answer,
                'explanation': question.explanation,
                'is_historical': False,
                'year': None,
                'source_question_id': question.id,
                'derivation_method': 'scenario_transfer'
            }
        return None
    
    def _replace_keywords_in_text(self, text: str) -> str:
        """替换文本中的关键词"""
        for entity_type, replacements in self.law_entities.items():
            for original in [entity_type] + replacements:
                if original in text:
                    replacement = random.choice([r for r in replacements if r != original])
                    text = text.replace(original, replacement, 1)
                    break
        return text
