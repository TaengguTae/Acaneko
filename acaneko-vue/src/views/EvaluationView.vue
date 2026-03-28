<script setup lang="ts">
import { ref } from 'vue'

interface TestCase {
  id: number
  question: string
  expectedAnswer: string
  actualAnswer: string
  score: number
  status: 'pending' | 'passed' | 'failed'
}

const testCases = ref<TestCase[]>([
  {
    id: 1,
    question: '什么是RAG？',
    expectedAnswer: 'RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI技术',
    actualAnswer: 'RAG是一种结合检索和生成的AI技术，能够提高回答的准确性',
    score: 85,
    status: 'passed'
  },
  {
    id: 2,
    question: '如何优化知识库检索效果？',
    expectedAnswer: '通过改进向量嵌入、调整相似度阈值、优化文档分块等方式',
    actualAnswer: '可以通过改进向量嵌入和调整相似度阈值来优化检索效果',
    score: 72,
    status: 'passed'
  },
  {
    id: 3,
    question: '知识库支持哪些文档格式？',
    expectedAnswer: '支持PDF、Word、TXT、Markdown等多种格式',
    actualAnswer: '支持PDF和Word格式',
    score: 45,
    status: 'failed'
  },
  {
    id: 4,
    question: '如何评估模型性能？',
    expectedAnswer: '可以通过准确率、召回率、F1分数等指标进行评估',
    actualAnswer: '',
    score: 0,
    status: 'pending'
  }
])

const selectedTests = ref<number[]>([])
const isRunning = ref(false)
const overallScore = ref(67.3)

const toggleSelect = (id: number) => {
  const index = selectedTests.value.indexOf(id)
  if (index > -1) {
    selectedTests.value.splice(index, 1)
  } else {
    selectedTests.value.push(id)
  }
}

const runTests = () => {
  if (selectedTests.value.length === 0) return
  isRunning.value = true
  setTimeout(() => {
    isRunning.value = false
    overallScore.value = 75.6
  }, 2000)
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#4caf50'
  if (score >= 60) return '#ff9800'
  return '#f44336'
}

const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待测试',
    passed: '通过',
    failed: '未通过'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string) => {
  return status
}
</script>

<template>
  <div class="evaluation-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">📊 测试集评估</h1>
        <p class="page-subtitle">评估和测试RAG系统的性能表现</p>
      </div>
      <div class="header-actions">
        <div class="score-display">
          <span class="score-label">综合评分</span>
          <span class="score-value" :style="{ color: getScoreColor(overallScore) }">
            {{ overallScore.toFixed(1) }}
          </span>
        </div>
        <button
          class="run-btn"
          :class="{ disabled: selectedTests.length === 0 || isRunning }"
          @click="runTests"
        >
          <span class="btn-icon">{{ isRunning ? '⏳' : '▶️' }}</span>
          <span class="btn-text">{{ isRunning ? '运行中...' : '运行测试' }}</span>
        </button>
      </div>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <div class="stat-value">{{ testCases.length }}</div>
          <div class="stat-label">测试用例</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ testCases.filter(t => t.status === 'passed').length }}</div>
          <div class="stat-label">通过</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ testCases.filter(t => t.status === 'failed').length }}</div>
          <div class="stat-label">未通过</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-info">
          <div class="stat-value">{{ testCases.filter(t => t.status === 'pending').length }}</div>
          <div class="stat-label">待测试</div>
        </div>
      </div>
    </div>

    <div class="test-cards">
      <div
        v-for="test in testCases"
        :key="test.id"
        class="test-card"
        :class="{ selected: selectedTests.includes(test.id) }"
      >
        <div class="card-header">
          <div class="checkbox-wrapper">
            <input
              type="checkbox"
              :id="`test-${test.id}`"
              :checked="selectedTests.includes(test.id)"
              @change="toggleSelect(test.id)"
            />
            <label :for="`test-${test.id}`" class="checkbox-label"></label>
          </div>
          <div class="test-id">#{{ test.id }}</div>
          <div class="test-status" :class="getStatusClass(test.status)">
            {{ getStatusText(test.status) }}
          </div>
          <div class="test-score" :style="{ color: getScoreColor(test.score) }">
            {{ test.score > 0 ? test.score + '分' : '-' }}
          </div>
        </div>

        <div class="card-body">
          <div class="test-section">
            <div class="section-label">问题</div>
            <div class="section-content">{{ test.question }}</div>
          </div>

          <div class="test-section">
            <div class="section-label">期望答案</div>
            <div class="section-content">{{ test.expectedAnswer }}</div>
          </div>

          <div class="test-section">
            <div class="section-label">实际答案</div>
            <div class="section-content">{{ test.actualAnswer || '暂无' }}</div>
          </div>
        </div>

        <div class="card-footer">
          <button class="action-btn">查看详情</button>
          <button class="action-btn">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.evaluation-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.run-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.run-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.run-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #999;
  font-weight: 500;
}

.test-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.test-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  cursor: pointer;
}

.test-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.test-card.selected {
  border-color: #667eea;
  background: #f8f9ff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 2px solid #f0f0f0;
}

.checkbox-wrapper {
  position: relative;
}

.checkbox-wrapper input[type="checkbox"] {
  display: none;
}

.checkbox-label {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-label {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-label::after {
  content: '✓';
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.test-id {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.test-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-left: auto;
}

.test-status.passed {
  background: #e8f5e9;
  color: #4caf50;
}

.test-status.failed {
  background: #ffebee;
  color: #f44336;
}

.test-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.test-score {
  font-size: 16px;
  font-weight: 700;
}

.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #f8f9ff;
  padding: 12px;
  border-radius: 8px;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 2px solid #f0f0f0;
}

.action-btn {
  flex: 1;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  background: #fff;
  color: #666;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8f9ff;
}

@media (max-width: 1024px) {
  .test-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-content h1 {
    font-size: 24px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .run-btn {
    flex: 1;
    justify-content: center;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
