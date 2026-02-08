const { createApp } = Vue;

createApp({
    data() {
        return {
            currentView: 'practice',
            questions: [],
            currentQuestion: null,
            selectedAnswer: null,
            answerSubmitted: false,
            isCorrect: false,
            statistics: {
                total_questions: 0,
                historical_questions: 0,
                derived_questions: 0,
                total_practices: 0,
                accuracy: 0,
                categories: {}
            },
            filters: {
                category: '',
                difficulty: '',
                is_historical: ''
            },
            pagination: {
                page: 1,
                per_page: 20,
                total: 0,
                total_pages: 0
            },
            apiBaseUrl: 'http://localhost:5000/api'
        };
    },
    mounted() {
        this.loadQuestions();
        this.loadStatistics();
    },
    methods: {
        async loadQuestions() {
            try {
                const params = new URLSearchParams({
                    page: this.pagination.page,
                    per_page: this.pagination.per_page
                });
                
                if (this.filters.category) params.append('category', this.filters.category);
                if (this.filters.difficulty) params.append('difficulty', this.filters.difficulty);
                if (this.filters.is_historical) params.append('is_historical', this.filters.is_historical);
                
                const response = await axios.get(`${this.apiBaseUrl}/questions?${params}`);
                
                if (response.data.success) {
                    this.questions = response.data.data.questions;
                    this.pagination = {
                        page: response.data.data.page,
                        per_page: response.data.data.per_page,
                        total: response.data.data.total,
                        total_pages: response.data.data.total_pages
                    };
                }
            } catch (error) {
                console.error('加载题目失败:', error);
                alert('加载题目失败，请检查后端服务是否启动（http://localhost:5000）');
            }
        },
        async loadStatistics() {
            try {
                const response = await axios.get(`${this.apiBaseUrl}/statistics`);
                if (response.data.success) {
                    this.statistics = response.data.data;
                }
            } catch (error) {
                console.error('加载统计失败:', error);
            }
        },
        selectQuestion(question) {
            this.currentQuestion = question;
            this.selectedAnswer = null;
            this.answerSubmitted = false;
            this.isCorrect = false;
        },
        selectAnswer(option) {
            if (!this.answerSubmitted) {
                this.selectedAnswer = option;
            }
        },
        async submitAnswer() {
            if (!this.selectedAnswer) return;
            
            try {
                // 提取答案字母（A, B, C, D等）
                const answerLetter = this.selectedAnswer.charAt(0);
                
                const response = await axios.post(`${this.apiBaseUrl}/practice/submit`, {
                    question_id: this.currentQuestion.id,
                    user_answer: answerLetter,
                    time_spent: 0
                });
                
                if (response.data.success) {
                    this.answerSubmitted = true;
                    this.isCorrect = response.data.data.is_correct;
                    this.currentQuestion.answer = response.data.data.correct_answer;
                    this.currentQuestion.explanation = response.data.data.explanation;
                    
                    // 刷新统计
                    this.loadStatistics();
                }
            } catch (error) {
                console.error('提交答案失败:', error);
                alert('提交答案失败，请重试');
            }
        },
        async deriveQuestions() {
            try {
                const response = await axios.post(
                    `${this.apiBaseUrl}/questions/${this.currentQuestion.id}/derive`,
                    { count: 3 }
                );
                
                if (response.data.success) {
                    alert(`成功生成 ${response.data.data.derived_questions.length} 道衍生题目！`);
                    this.loadQuestions();
                    this.backToList();
                }
            } catch (error) {
                console.error('生成衍生题失败:', error);
                alert('生成衍生题失败，请重试');
            }
        },
        backToList() {
            this.currentQuestion = null;
            this.selectedAnswer = null;
            this.answerSubmitted = false;
            this.isCorrect = false;
        },
        changePage(page) {
            if (page >= 1 && page <= this.pagination.total_pages) {
                this.pagination.page = page;
                this.loadQuestions();
            }
        },
        getDifficultyText(difficulty) {
            const map = {
                'easy': '简单',
                'medium': '中等',
                'hard': '困难'
            };
            return map[difficulty] || difficulty;
        },
        getOptionClass(option) {
            if (!this.answerSubmitted) {
                return this.selectedAnswer === option ? 'selected' : '';
            }
            
            const answerLetter = option.charAt(0);
            if (answerLetter === this.currentQuestion.answer) {
                return 'correct';
            }
            if (option === this.selectedAnswer && !this.isCorrect) {
                return 'incorrect';
            }
            return '';
        }
    }
}).mount('#app');
