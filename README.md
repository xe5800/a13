# 青海省行政执法公务员练习系统

一个专门为青海省行政执法类公务员考试设计的在线练习平台，包含历年真题和智能衍生练习题。

## 功能特点

- 📝 **历年真题库**：收录历年行政执法类公务员考试真题
- 🤖 **智能题目衍生**：基于历年真题深度分析，自动生成相似练习题
- 📊 **练习统计**：记录练习进度和正确率
- 🎯 **分类练习**：按知识点、难度、题型分类练习
- 💯 **模拟考试**：模拟真实考试环境

## 技术栈

- **后端**: Python Flask + SQLite
- **前端**: Vue.js 3 + Tailwind CSS
- **数据库**: SQLite

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
cd backend
python init_db.py
```

### 3. 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:5000` 启动

### 4. 访问前端

在浏览器中打开 `frontend/index.html` 或使用 HTTP 服务器：

```bash
cd frontend
python -m http.server 8080
```

然后访问 `http://localhost:8080`

## 项目结构

```
a13/
├── backend/              # 后端 API
│   ├── app.py           # Flask 主应用
│   ├── models.py        # 数据模型
│   ├── config.py        # 配置文件
│   ├── database.py      # 数据库管理
│   ├── question_derivation.py  # 题目衍生引擎
│   ├── init_db.py       # 数据库初始化
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端界面
│   ├── index.html      # 主页面
│   ├── css/
│   │   └── style.css   # 样式
│   └── js/
│       └── app.js      # Vue.js 应用
├── data/               # 数据文件
│   └── sample_questions.json  # 示例题目
└── README.md           # 项目说明
```

## 题目数据格式

题目以 JSON 格式存储：

```json
{
  "id": 1,
  "type": "single_choice",
  "category": "行政法",
  "difficulty": "medium",
  "question": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "answer": "A",
  "explanation": "答案解析",
  "is_historical": true,
  "year": 2023
}
```

## API 接口

- `GET /api/questions` - 获取题目列表
- `GET /api/questions/<id>` - 获取单个题目
- `GET /api/categories` - 获取题目分类
- `POST /api/practice/submit` - 提交答案
- `GET /api/statistics` - 获取练习统计

## 题目衍生算法

系统使用以下策略生成衍生题目：

1. **关键词替换**：替换题目中的关键实体和数据
2. **逻辑变换**：改变题目逻辑关系（正向/反向）
3. **场景迁移**：将同一法律原理应用到不同场景
4. **难度调整**：增加或减少题目复杂度

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
