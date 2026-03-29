<script setup lang="ts">
import { ref, computed } from 'vue'

interface Model {
  id: number
  name: string
  provider: string
  version: string
  type: 'embedding' | 'rerank'
  description: string
}

interface DocInput {
  id: number
  content: string
}

interface ModelResult {
  modelId: number
  modelName: string
  docScores: Array<{
    docId: number
    docContent: string
    score: number
  }>
}

const activeTab = ref<'embedding' | 'rerank'>('embedding')

const embeddingModels = ref<Model[]>([
  {
    id: 1,
    name: 'OpenAI Embedding-3',
    provider: 'OpenAI',
    version: 'text-embedding-3-small',
    type: 'embedding',
    description: '最新的OpenAI嵌入模型，支持多语言'
  },
  {
    id: 2,
    name: 'BGE-Large',
    provider: 'BAAI',
    version: 'bge-large-zh-v1.5',
    type: 'embedding',
    description: '强大的中文嵌入模型，适合中文场景'
  },
  {
    id: 3,
    name: 'Cohere Embed',
    provider: 'Cohere',
    version: 'embed-multilingual-v3.0',
    type: 'embedding',
    description: '多语言嵌入模型，支持100+语言'
  },
  {
    id: 4,
    name: 'E5-Large',
    provider: 'Intfloat',
    version: 'e5-large-v2',
    type: 'embedding',
    description: '高性能嵌入模型，支持长文本'
  }
])

const rerankModels = ref<Model[]>([
  {
    id: 5,
    name: 'BGE Reranker',
    provider: 'BAAI',
    version: 'bge-reranker-v2-m3',
    type: 'rerank',
    description: '高效的中文重排序模型'
  },
  {
    id: 6,
    name: 'Cohere Rerank',
    provider: 'Cohere',
    version: 'rerank-v3.5',
    type: 'rerank',
    description: '多语言重排序模型，性能优异'
  },
  {
    id: 7,
    name: 'Cross Encoder',
    provider: 'Microsoft',
    version: 'cross-encoder-ms-marco',
    type: 'rerank',
    description: '经典的重排序模型，稳定可靠'
  }
])

const queryInput = ref('')
const docInputs = ref<DocInput[]>([
  { id: 1, content: '' }
])
const selectedModelIds = ref<number[]>([])
const isRunning = ref(false)
const testResults = ref<ModelResult[]>([])
const docIdCounter = ref(2)

const currentModels = computed(() => {
  return activeTab.value === 'embedding' ? embeddingModels.value : rerankModels.value
})

const canRunTest = computed(() => {
  return queryInput.value.trim() !== '' &&
         docInputs.value.some(doc => doc.content.trim() !== '') &&
         selectedModelIds.value.length >= 1 &&
         selectedModelIds.value.length <= 3
})

const addDocInput = () => {
  if (docInputs.value.length < 10) {
    docInputs.value.push({
      id: docIdCounter.value++,
      content: ''
    })
  }
}

const removeDocInput = (id: number) => {
  if (docInputs.value.length > 1) {
    docInputs.value = docInputs.value.filter(doc => doc.id !== id)
  }
}

const toggleModelSelection = (modelId: number) => {
  const index = selectedModelIds.value.indexOf(modelId)
  if (index > -1) {
    selectedModelIds.value.splice(index, 1)
  } else if (selectedModelIds.value.length < 3) {
    selectedModelIds.value.push(modelId)
  }
}

const runTest = async () => {
  if (!canRunTest.value || isRunning.value) return

  isRunning.value = true
  testResults.value = []

  await new Promise(resolve => setTimeout(resolve, 2000))

  selectedModelIds.value.forEach(modelId => {
    const model = currentModels.value.find(m => m.id === modelId)
    if (model) {
      const docScores = docInputs.value
        .filter(doc => doc.content.trim() !== '')
        .map(doc => ({
          docId: doc.id,
          docContent: doc.content,
          score: Math.random() * 0.5 + 0.5
        }))
        .sort((a, b) => b.score - a.score)

      testResults.value.push({
        modelId: modelId,
        modelName: model.name,
        docScores
      })
    }
  })

  isRunning.value = false
}

const getScoreColor = (score: number) => {
  if (score >= 0.8) return '#4caf50'
  if (score >= 0.6) return '#2196f3'
  if (score >= 0.4) return '#ff9800'
  return '#f44336'
}

const getScoreLabel = (score: number) => {
  if (score >= 0.8) return '优秀'
  if (score >= 0.6) return '良好'
  if (score >= 0.4) return '一般'
  return '较差'
}

const clearResults = () => {
  testResults.value = []
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

    <div class="tab-navigation">
      <div
        class="tab-item"
        :class="{ active: activeTab === 'embedding' }"
        @click="activeTab = 'embedding'"
      >
        <span class="tab-icon">📊</span>
        <span class="tab-label">Embedding模型</span>
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'rerank' }"
        @click="activeTab = 'rerank'"
      >
        <span class="tab-icon">🔄</span>
        <span class="tab-label">Rerank模型</span>
      </div>
    </div>

    <div class="content-grid">
      <div class="input-section">
        <div class="section-header">
          <h2 class="section-title">输入配置</h2>
        </div>

        <div class="input-form">
          <div class="form-group">
            <label class="form-label">
              <span class="label-text">Query</span>
              <span class="label-required">*</span>
            </label>
            <input
              v-model="queryInput"
              class="form-input"
              placeholder="请输入查询内容..."
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span class="label-text">文档</span>
              <span class="label-required">*</span>
            </label>
            <div class="doc-inputs-container">
              <div
                v-for="doc in docInputs"
                :key="doc.id"
                class="doc-input-wrapper"
              >
                <input
                  v-model="doc.content"
                  class="form-input doc-input"
                  placeholder="输入doc内容"
                />
                <button
                  v-if="docInputs.length > 1"
                  class="remove-doc-btn"
                  @click="removeDocInput(doc.id)"
                  title="删除此文档"
                >
                  ✕
                </button>
              </div>

              <button
                v-if="docInputs.length < 10"
                class="add-doc-btn"
                @click="addDocInput"
                title="添加新文档"
              >
                <span class="add-icon">+</span>
                <span class="add-text">添加文档</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="model-section">
        <div class="section-header">
          <h2 class="section-title">模型选择</h2>
          <span class="selection-info">
            已选 {{ selectedModelIds.length }}/3
          </span>
        </div>

        <div class="model-grid">
          <div
            v-for="model in currentModels"
            :key="model.id"
            class="model-card"
            :class="{ selected: selectedModelIds.includes(model.id) }"
            @click="toggleModelSelection(model.id)"
          >
            <div class="model-checkbox">
              <div class="checkbox-indicator">
                <span v-if="selectedModelIds.includes(model.id)">✓</span>
              </div>
            </div>
            <div class="model-info">
              <h3 class="model-name">{{ model.name }}</h3>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button
            class="run-btn"
            :class="{ disabled: !canRunTest || isRunning }"
            @click="runTest"
          >
            <span class="btn-icon">{{ isRunning ? '⏳' : '🚀' }}</span>
            <span class="btn-text">{{ isRunning ? '测试中...' : '运行测试' }}</span>
          </button>

          <button
            v-if="testResults.length > 0"
            class="clear-btn"
            @click="clearResults"
          >
            <span class="btn-icon">🗑️</span>
            <span class="btn-text">清除结果</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="testResults.length > 0" class="results-section">
      <div class="section-header">
        <h2 class="section-title">测试结果</h2>
        <span class="result-count">{{ testResults.length }} 个模型</span>
      </div>

      <div class="results-grid">
        <div
          v-for="result in testResults"
          :key="result.modelId"
          class="result-card"
        >
          <div class="result-header">
            <h3 class="result-model-name">{{ result.modelName }}</h3>
            <span class="result-type">{{ activeTab === 'embedding' ? 'Embedding' : 'Rerank' }}</span>
          </div>

          <div class="result-body">
            <div
              v-for="(docScore, index) in result.docScores"
              :key="docScore.docId"
              class="doc-bubble"
            >
              <div class="bubble-content">
                <span class="doc-index">{{ index + 1 }}.</span>
                <span class="doc-text">{{ docScore.docContent }}</span>
                <div class="bubble-score" :style="{ backgroundColor: getScoreColor(docScore.score) }">
                  <span class="score-value">{{ (docScore.score * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <div v-if="result.docScores.length === 0" class="empty-result">
              <span class="empty-icon">📭</span>
              <p class="empty-text">暂无测试结果</p>
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

.tab-navigation {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  padding: 8px;
  background: transparent;
  border-radius: 12px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: #666;
  background: #f8f9fa;
}

.tab-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.tab-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.tab-icon {
  font-size: 20px;
}

.tab-label {
  font-size: 15px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.input-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.input-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.input-section .section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

.input-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.label-text {
  font-size: 13px;
}

.label-required {
  color: #f44336;
  font-size: 15px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.doc-input {
  padding-right: 40px;
}

.doc-inputs-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.remove-doc-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border: none;
  background: #ffebee;
  color: #f44336;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-doc-btn:hover {
  background: #f44336;
  color: #fff;
  transform: scale(1.1);
}

.add-doc-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: 2px dashed #667eea;
  background: #f8f9ff;
  color: #667eea;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-doc-btn:hover {
  background: #667eea;
  color: #fff;
  transform: translateY(-2px);
}

.add-icon {
  font-size: 20px;
  font-weight: 700;
}

.add-text {
  font-size: 14px;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.model-card {
  display: flex;
  gap: 10px;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.model-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.model-card.selected {
  border-color: #667eea;
  background: #f8f9ff;
}

.model-checkbox {
  flex-shrink: 0;
}

.checkbox-indicator {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #667eea;
  font-weight: 700;
  transition: all 0.3s ease;
}

.model-card.selected .checkbox-indicator {
  background: #667eea;
  border-color: #667eea;
  color: #fff;
}

.model-info {
  flex: 1;
  display: flex;
  align-items: center;
}

.model-name {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 2px solid #f0f0f0;
}

.run-btn,
.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.run-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
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

.clear-btn {
  background: #fff;
  color: #666;
  border: 2px solid #e0e0e0;
}

.clear-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8f9ff;
}

.btn-icon {
  font-size: 18px;
}

.btn-text {
  font-size: 15px;
}

.model-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.model-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-section .section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

.model-section .selection-info {
  font-size: 13px;
  color: #667eea;
  font-weight: 600;
  background: #f8f9ff;
  padding: 4px 10px;
  border-radius: 10px;
}

.result-count {
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
  background: #f8f9ff;
  padding: 6px 12px;
  border-radius: 12px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.result-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.result-card:nth-child(1) {
  border-color: #667eea;
}

.result-card:nth-child(2) {
  border-color: #26a69a;
}

.result-card:nth-child(3) {
  border-color: #ffa726;
}

.result-card:hover {
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

.result-model-name {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
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

.result-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-bubble {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.doc-bubble:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.bubble-content {
  padding: 8px 12px;
  font-size: 13px;
  color: #333;
  line-height: 1.4;
  background: #fff;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.doc-index {
  font-size: 12px;
  font-weight: 700;
  color: #667eea;
  flex-shrink: 0;
}

.doc-text {
  flex: 1;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bubble-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 5px;
  min-width: 60px;
  height: 28px;
  flex-shrink: 0;
}

.score-value {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.empty-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  margin: 0;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content h1 {
    font-size: 24px;
  }

  .tab-navigation {
    flex-direction: column;
  }

  .tab-item {
    width: 100%;
    justify-content: center;
  }

  .model-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>