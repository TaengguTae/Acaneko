<script setup lang="ts">
import { ref } from 'vue'

interface Model {
  id: number
  name: string
  provider: string
  version: string
  status: 'active' | 'inactive'
  description: string
}

interface TestResult {
  id: number
  modelName: string
  testType: string
  input: string
  output: string
  latency: number
  timestamp: string
}

const models = ref<Model[]>([
  {
    id: 1,
    name: 'GPT-4',
    provider: 'OpenAI',
    version: 'gpt-4-turbo',
    status: 'active',
    description: '最先进的语言模型，适用于复杂任务'
  },
  {
    id: 2,
    name: 'Claude-3',
    provider: 'Anthropic',
    version: 'claude-3-opus',
    status: 'active',
    description: '强大的多模态模型，擅长推理和分析'
  },
  {
    id: 3,
    name: 'Qwen',
    provider: 'Alibaba',
    version: 'qwen-turbo',
    status: 'inactive',
    description: '高性能中文语言模型'
  }
])

const testResults = ref<TestResult[]>([
  {
    id: 1,
    modelName: 'GPT-4',
    testType: '问答测试',
    input: '什么是机器学习？',
    output: '机器学习是人工智能的一个分支...',
    latency: 1.2,
    timestamp: '2024-03-29 10:30:00'
  },
  {
    id: 2,
    modelName: 'Claude-3',
    testType: '摘要生成',
    input: '长文本内容...',
    output: '摘要内容...',
    latency: 0.8,
    timestamp: '2024-03-29 10:25:00'
  }
])

const selectedModel = ref<number>(1)
const testInput = ref('')
const testType = ref('问答测试')
const isTesting = ref(false)
const showResults = ref(true)

const testTypes = [
  '问答测试',
  '摘要生成',
  '文本分类',
  '情感分析',
  '代码生成'
]

const handleTest = async () => {
  if (!testInput.value.trim() || isTesting.value) return

  isTesting.value = true

  setTimeout(() => {
    const model = models.value.find(m => m.id === selectedModel.value)
    const newResult: TestResult = {
      id: Date.now(),
      modelName: model?.name || 'Unknown',
      testType: testType.value,
      input: testInput.value,
      output: `这是一个模拟的${testType.value}结果。在实际应用中，这里会调用模型API并返回真实结果。`,
      latency: Math.random() * 2 + 0.5,
      timestamp: new Date().toLocaleString()
    }

    testResults.value.unshift(newResult)
    testInput.value = ''
    isTesting.value = false
    showResults.value = true
  }, 1500)
}

const toggleModelStatus = (id: number) => {
  const model = models.value.find(m => m.id === id)
  if (model) {
    model.status = model.status === 'active' ? 'inactive' : 'active'
  }
}

const getLatencyColor = (latency: number) => {
  if (latency < 1) return '#4caf50'
  if (latency < 2) return '#ff9800'
  return '#f44336'
}
</script>

<template>
  <div class="model-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">🧪 模型测试</h1>
        <p class="page-subtitle">测试和评估不同AI模型的性能</p>
      </div>
    </div>

    <div class="model-grid">
      <div class="models-section">
        <div class="section-header">
          <h2 class="section-title">可用模型</h2>
          <span class="section-count">{{ models.length }} 个模型</span>
        </div>

        <div class="model-list">
          <div
            v-for="model in models"
            :key="model.id"
            class="model-card"
            :class="{ active: selectedModel === model.id, inactive: model.status === 'inactive' }"
            @click="selectedModel = model.id"
          >
            <div class="model-header">
              <div class="model-info">
                <h3 class="model-name">{{ model.name }}</h3>
                <span class="model-provider">{{ model.provider }}</span>
              </div>
              <div class="model-status" :class="model.status">
                {{ model.status === 'active' ? '启用' : '禁用' }}
              </div>
            </div>
            <p class="model-description">{{ model.description }}</p>
            <div class="model-footer">
              <span class="model-version">版本: {{ model.version }}</span>
              <button class="toggle-btn" @click.stop="toggleModelStatus(model.id)">
                {{ model.status === 'active' ? '禁用' : '启用' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="test-section">
        <div class="section-header">
          <h2 class="section-title">模型测试</h2>
        </div>

        <div class="test-form">
          <div class="form-group">
            <label class="form-label">选择模型</label>
            <select v-model="selectedModel" class="form-select">
              <option
                v-for="model in models.filter(m => m.status === 'active')"
                :key="model.id"
                :value="model.id"
              >
                {{ model.name }} - {{ model.version }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">测试类型</label>
            <select v-model="testType" class="form-select">
              <option v-for="type in testTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">测试输入</label>
            <textarea
              v-model="testInput"
              class="form-textarea"
              placeholder="请输入测试内容..."
              rows="4"
            ></textarea>
          </div>

          <button
            class="test-btn"
            :class="{ disabled: !testInput.trim() || isTesting }"
            @click="handleTest"
          >
            <span class="btn-icon">{{ isTesting ? '⏳' : '🚀' }}</span>
            <span class="btn-text">{{ isTesting ? '测试中...' : '开始测试' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="results-section">
      <div class="section-header">
        <h2 class="section-title">测试结果</h2>
        <button class="toggle-results-btn" @click="showResults = !showResults">
          {{ showResults ? '收起' : '展开' }}
        </button>
      </div>

      <div v-if="showResults" class="results-list">
        <div
          v-for="result in testResults"
          :key="result.id"
          class="result-card"
        >
          <div class="result-header">
            <div class="result-info">
              <span class="result-model">{{ result.modelName }}</span>
              <span class="result-type">{{ result.testType }}</span>
            </div>
            <div class="result-metrics">
              <span class="result-latency" :style="{ color: getLatencyColor(result.latency) }">
                ⏱️ {{ result.latency.toFixed(2) }}s
              </span>
              <span class="result-time">{{ result.timestamp }}</span>
            </div>
          </div>

          <div class="result-body">
            <div class="result-section">
              <div class="result-label">输入</div>
              <div class="result-content">{{ result.input }}</div>
            </div>
            <div class="result-section">
              <div class="result-label">输出</div>
              <div class="result-content">{{ result.output }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.model-page {
  width: 100%;
}

.page-header {
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

.model-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.models-section,
.test-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

.section-count {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.model-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.model-card {
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.model-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.model-card.active {
  border-color: #667eea;
  background: #f8f9ff;
}

.model-card.inactive {
  opacity: 0.6;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.model-info h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #333;
}

.model-provider {
  font-size: 13px;
  color: #999;
  font-weight: 500;
}

.model-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.model-status.active {
  background: #e8f5e9;
  color: #4caf50;
}

.model-status.inactive {
  background: #ffebee;
  color: #f44336;
}

.model-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.model-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-version {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.toggle-btn {
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  background: #fff;
  color: #666;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8f9ff;
}

.test-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.form-select,
.form-textarea {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.test-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
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

.test-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.test-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
}

.results-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.toggle-results-btn {
  padding: 8px 16px;
  border: 2px solid #e0e0e0;
  background: #fff;
  color: #666;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-results-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8f9ff;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.result-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9ff;
  border-bottom: 2px solid #e0e0e0;
}

.result-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.result-model {
  font-size: 15px;
  font-weight: 700;
  color: #333;
}

.result-type {
  padding: 4px 12px;
  background: #e8eaf6;
  color: #667eea;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.result-metrics {
  display: flex;
  gap: 16px;
  align-items: center;
}

.result-latency {
  font-size: 14px;
  font-weight: 600;
}

.result-time {
  font-size: 13px;
  color: #999;
}

.result-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-label {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #f8f9ff;
  padding: 12px;
  border-radius: 8px;
}

@media (max-width: 1024px) {
  .model-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 24px;
  }

  .model-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .result-metrics {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
