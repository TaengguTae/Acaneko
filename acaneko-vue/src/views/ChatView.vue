<script setup lang="ts">
import { ref, nextTick, computed, onMounted } from 'vue'
import { apiService, type KnowledgeBase, type ChatConfig, type QueryUnderstandingResult, type RetrievalResult } from '../services/api'

interface Message {
  id: number
  type: 'user' | 'assistant'
  content: string
  timestamp: string
}

const messages = ref<Message[]>([
  {
    id: 1,
    type: 'assistant',
    content: '您好！我是RAG测试平台的AI助手。我可以帮助您回答问题、检索知识库内容。请问有什么可以帮助您的？',
    timestamp: new Date().toLocaleTimeString()
  }
])

const inputMessage = ref('')
const chatContainer = ref<HTMLElement>()
const isLoading = ref(false)

const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedKnowledgeBase = ref<string>('')

const advancedQueryEnabled = ref(false)
const queryUnderstandingOptions = ref({
  keywordExtraction: false,
  slotExtraction: false,
  queryRewriting: false,
  hyde: false
})

const similarityThreshold = ref(0.65)
const rerankEnabled = ref(false)
const rerankModel = ref<string>('bge-reranker')
const rerankThreshold = ref(0.5)
const selectedLLM = ref<string>('gpt-4')

const configLocked = ref(false)
const showSuccessToast = ref(false)

const queryUnderstandingResult = ref<QueryUnderstanding | null>(null)
const retrievalResults = ref<RetrievalResult[]>([])
const expandedResultId = ref<string | null>(null)

const activeKnowledgeBases = computed(() => {
  return knowledgeBases.value.filter(kb => kb.status === 'active')
})

onMounted(async () => {
  await loadKnowledgeBases()
  if (activeKnowledgeBases.value.length > 0) {
    selectedKnowledgeBase.value = activeKnowledgeBases.value[0].id
  }
})

const loadKnowledgeBases = async () => {
  try {
    knowledgeBases.value = await apiService.getKnowledgeBases()
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  if (!selectedKnowledgeBase.value) {
    alert('请先选择知识库')
    return
  }

  const userMessage: Message = {
    id: Date.now(),
    type: 'user',
    content: inputMessage.value,
    timestamp: new Date().toLocaleTimeString()
  }

  messages.value.push(userMessage)
  const userQuery = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()

  isLoading.value = true

  try {
    const chatConfig: ChatConfig = {
      knowledgeBaseId: selectedKnowledgeBase.value,
      llmModel: selectedLLM.value,
      similarityThreshold: similarityThreshold.value,
      advancedQueryEnabled: advancedQueryEnabled.value,
      queryUnderstandingOptions: {
        keywordExtraction: queryUnderstandingOptions.value.keywordExtraction,
        slotExtraction: queryUnderstandingOptions.value.slotExtraction,
        queryRewriting: queryUnderstandingOptions.value.queryRewriting,
        hyde: queryUnderstandingOptions.value.hyde
      },
      rerankEnabled: rerankEnabled.value,
      rerankModel: rerankModel.value,
      rerankThreshold: rerankThreshold.value
    }

    const response = await apiService.chat({
      query: userQuery,
      config: chatConfig
    })

    const assistantMessage: Message = {
      id: Date.now(),
      type: 'assistant',
      content: response.message,
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(assistantMessage)
    
    if (response.queryUnderstanding) {
      queryUnderstandingResult.value = {
        keywords: response.queryUnderstanding.keywords,
        slots: response.queryUnderstanding.slots,
        rewrittenQuery: response.queryUnderstanding.rewrittenQuery,
        hyde: response.queryUnderstanding.hyde
      }
    }
    
    if (response.retrievalResults && response.retrievalResults.length > 0) {
      retrievalResults.value = response.retrievalResults
    }
    
    isLoading.value = false
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    const errorMessage: Message = {
      id: Date.now(),
      type: 'assistant',
      content: '抱歉，处理您的请求时出现了错误。请稍后重试。',
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(errorMessage)
    isLoading.value = false
    scrollToBottom()
  }
}

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const clearChat = () => {
  messages.value = [
    {
      id: Date.now(),
      type: 'assistant',
      content: '您好！我是RAG测试平台的AI助手。我可以帮助您回答问题、检索知识库内容。请问有什么可以帮助您的？',
      timestamp: new Date().toLocaleTimeString()
    }
  ]
  queryUnderstandingResult.value = null
  retrievalResults.value = []
  expandedResultId.value = null
}

const lockConfig = () => {
  configLocked.value = true
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 2000)
}

const unlockConfig = () => {
  configLocked.value = false
}

const toggleResultExpansion = (id: string) => {
  expandedResultId.value = expandedResultId.value === id ? null : id
}

const formatScore = (score: number) => {
  return (score * 100).toFixed(1)
}
</script>

<template>
  <div class="chat-page">
    <div class="chat-layout">
      <div class="left-panel">
        <div class="page-header">
          <div class="header-content">
            <h1 class="page-title">💬 Chat问答</h1>
            <p class="page-subtitle">与AI助手进行智能对话</p>
          </div>
          <button class="clear-btn" @click="clearChat">
            <span class="btn-icon">🗑️</span>
            <span class="btn-text">清空对话</span>
          </button>
        </div>

        <div class="chat-container" ref="chatContainer">
          <div class="messages-wrapper">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message"
              :class="message.type"
            >
              <div class="message-avatar">
                {{ message.type === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">
                    {{ message.type === 'user' ? '您' : 'AI助手' }}
                  </span>
                  <span class="message-time">{{ message.timestamp }}</span>
                </div>
                <div class="message-text">{{ message.content }}</div>
              </div>
            </div>

            <div v-if="isLoading" class="message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">AI助手</span>
                  <span class="message-time">正在输入...</span>
                </div>
                <div class="message-text loading">
                  <span class="loading-dot"></span>
                  <span class="loading-dot"></span>
                  <span class="loading-dot"></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              class="chat-input"
              placeholder="请输入您的问题..."
              rows="1"
              @keypress="handleKeyPress"
            ></textarea>
            <button
              class="send-btn"
              :class="{ disabled: !inputMessage.trim() || isLoading }"
              @click="handleSend"
            >
              <span class="send-icon">📤</span>
            </button>
          </div>
          <div class="input-tips">
            <span class="tip-text">💡 提示：按 Enter 发送，Shift + Enter 换行</span>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="config-section">
          <div class="config-card">
            <div class="config-grid">
              <div class="config-row">
                <div class="config-item">
                  <label class="config-label">知识库选择</label>
                  <select 
                    v-model="selectedKnowledgeBase" 
                    class="config-select"
                    :disabled="configLocked"
                  >
                    <option value="">请选择知识库</option>
                    <option
                      v-for="kb in activeKnowledgeBases"
                      :key="kb.id"
                      :value="kb.id"
                    >
                      {{ kb.name }}
                    </option>
                  </select>
                </div>

                <div class="config-item">
                  <label class="config-label">大模型选择</label>
                  <select 
                    v-model="selectedLLM" 
                    class="config-select"
                    :disabled="configLocked"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="qwen-72b">Qwen-72B</option>
                  </select>
                </div>

                <div class="config-item">
                  <label class="config-label">
                    相似度阈值
                    <span class="threshold-value">{{ similarityThreshold.toFixed(2) }}</span>
                  </label>
                  <input
                    type="range"
                    v-model.number="similarityThreshold"
                    min="0"
                    max="1"
                    step="0.01"
                    class="range-slider"
                    :disabled="configLocked"
                  />
                </div>
              </div>

              <div class="config-row">
                <div class="config-item">
                  <div class="toggle-header">
                    <label class="config-label">高级Query理解</label>
                    <div 
                      class="toggle-switch"
                      :class="{ active: advancedQueryEnabled }"
                      :disabled="configLocked"
                      @click="advancedQueryEnabled = !advancedQueryEnabled"
                    >
                      <div class="toggle-slider"></div>
                    </div>
                  </div>
                  <div v-if="advancedQueryEnabled" class="inline-options">
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="queryUnderstandingOptions.keywordExtraction"
                        :disabled="configLocked"
                      />
                      <span>关键词提取</span>
                    </label>
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="queryUnderstandingOptions.slotExtraction"
                        :disabled="configLocked"
                      />
                      <span>槽位提取</span>
                    </label>
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="queryUnderstandingOptions.queryRewriting"
                        :disabled="configLocked"
                      />
                      <span>Query改写</span>
                    </label>
                    <label class="checkbox-label">
                      <input 
                        type="checkbox" 
                        v-model="queryUnderstandingOptions.hyde"
                        :disabled="configLocked"
                      />
                      <span>HyDE</span>
                    </label>
                  </div>
                </div>

                <div class="config-item">
                  <div class="toggle-header">
                    <label class="config-label">Rerank功能</label>
                    <div 
                      class="toggle-switch"
                      :class="{ active: rerankEnabled }"
                      :disabled="configLocked"
                      @click="rerankEnabled = !rerankEnabled"
                    >
                      <div class="toggle-slider"></div>
                    </div>
                  </div>
                  <div v-if="rerankEnabled" class="inline-options">
                    <div class="inline-option">
                      <label class="config-label">Rerank模型</label>
                      <select 
                        v-model="rerankModel" 
                        class="config-select small"
                        :disabled="configLocked"
                      >
                        <option value="bge-reranker">BGE Reranker</option>
                        <option value="cross-encoder">Cross Encoder</option>
                        <option value="cohere-rerank">Cohere Rerank</option>
                      </select>
                    </div>
                    <div class="inline-option">
                      <label class="config-label">
                        Rerank分数阈值
                        <span class="threshold-value small">{{ rerankThreshold.toFixed(2) }}</span>
                      </label>
                      <input
                        type="range"
                        v-model.number="rerankThreshold"
                        min="0"
                        max="1"
                        step="0.01"
                        class="range-slider small"
                        :disabled="configLocked"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="action-buttons">
                <button 
                  class="action-btn secondary" 
                  @click="unlockConfig"
                >
                  修改配置
                </button>
                <button 
                  class="action-btn primary" 
                  :class="{ disabled: configLocked }"
                  @click="lockConfig"
                >
                  启用配置
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="results-section">
          <div class="results-layout">
            <div class="query-understanding-panel">
              <div v-if="queryUnderstandingResult" class="result-card">
                <div class="card-header">
                  <span class="card-title">Query理解结果</span>
                  <span class="card-icon">🧠</span>
                </div>
                <div class="card-content">
                  <div class="understanding-item">
                    <span class="item-label">关键词：</span>
                    <div class="item-tags">
                      <span 
                        v-for="keyword in queryUnderstandingResult.keywords" 
                        :key="keyword"
                        class="tag"
                      >
                        {{ keyword }}
                      </span>
                    </div>
                  </div>
                  <div class="understanding-item">
                    <span class="item-label">槽位：</span>
                    <div class="item-tags">
                      <span 
                        v-for="slot in queryUnderstandingResult.slots" 
                        :key="slot"
                        class="tag"
                      >
                        {{ slot }}
                      </span>
                    </div>
                  </div>
                  <div class="understanding-item">
                    <span class="item-label">重写Query：</span>
                    <span class="item-value">{{ queryUnderstandingResult.rewrittenQuery }}</span>
                  </div>
                  <div class="understanding-item">
                    <span class="item-label">HyDE：</span>
                    <span class="item-value">{{ queryUnderstandingResult.hyde }}</span>
                  </div>
                </div>
              </div>
              <div v-if="!queryUnderstandingResult" class="empty-state small">
                <div class="empty-icon">🧠</div>
                <p class="empty-text">暂无Query理解结果</p>
              </div>
            </div>

            <div class="retrieval-results-panel">
              <div v-if="retrievalResults.length > 0" class="result-card">
                <div class="card-header">
                  <span class="card-title">检索召回片段</span>
                  <span class="card-icon">📄</span>
                </div>
                <div class="card-content">
                  <div
                    v-for="result in retrievalResults"
                    :key="result.id"
                    class="retrieval-bubble"
                    :class="{ expanded: expandedResultId === result.id }"
                    @click="toggleResultExpansion(result.id)"
                  >
                    <div class="bubble-header">
                      <div class="bubble-summary">
                        <span class="bubble-icon">💬</span>
                        <span class="bubble-text">{{ result.content.substring(0, 50) }}...</span>
                      </div>
                      <div class="bubble-scores">
                        <div class="score-item">
                          <span class="score-label">相似度</span>
                          <span class="score-value similarity">{{ formatScore(result.similarity) }}%</span>
                        </div>
                        <div class="score-item">
                          <span class="score-label">Rank分数</span>
                          <span class="score-value rank">{{ formatScore(result.rankScore) }}%</span>
                        </div>
                      </div>
                    </div>
                    <div v-if="expandedResultId === result.id" class="bubble-details">
                      <div class="detail-content">
                        <p class="detail-text">{{ result.content }}</p>
                        <div class="detail-metadata">
                          <div class="metadata-item">
                            <span class="metadata-label">文件名：</span>
                            <span class="metadata-value">{{ result.fileName }}</span>
                          </div>
                          <div 
                            v-for="(value, key) in result.metadata" 
                            :key="key"
                            class="metadata-item"
                          >
                            <span class="metadata-label">{{ key }}：</span>
                            <span class="metadata-value">{{ value }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="retrievalResults.length === 0" class="empty-state small">
                <div class="empty-icon">🔍</div>
                <p class="empty-text">暂无检索结果</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSuccessToast" class="toast success-toast">
      <span class="toast-icon">✓</span>
      <span class="toast-message">启用成功</span>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  width: 100%;
  height: 100%;
  background: #f8f9ff;
  overflow: hidden;
}

.chat-layout {
  display: flex;
  height: 100%;
  gap: 24px;
  padding: 24px;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
  overflow: hidden;
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #e8eaf6;
}

.header-content h1 {
  font-size: 24px;
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

.clear-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f5f5f5;
  color: #666;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #ffebee;
  border-color: #f44336;
  color: #f44336;
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 16px;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 2px solid #e8eaf6;
}

.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-header {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.message-role {
  font-weight: 600;
  color: #667eea;
}

.message-text {
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  line-height: 1.6;
  font-size: 14px;
  color: #333;
  word-wrap: break-word;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 12px 12px 0 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.message.assistant .message-text {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8eaf6 100%);
  border-radius: 12px 12px 12px 0;
  border: 2px solid #e8eaf6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-text.loading {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: all 0.3s ease;
  max-height: 120px;
}

.chat-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.send-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  font-size: 20px;
}

.input-tips {
  text-align: center;
}

.tip-text {
  font-size: 12px;
  color: #999;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #333;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 0 0 auto;
  min-height: 0;
  overflow: hidden;
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.results-layout {
  display: flex;
  gap: 16px;
  height: 100%;
  min-height: 0;
}

.query-understanding-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.retrieval-results-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.query-understanding-panel .result-card,
.retrieval-results-panel .result-card {
  height: 100%;
  overflow-y: auto;
}

.result-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border: 2px solid #e8eaf6;
  overflow-y: auto;
  max-height: 100%;
}

.result-card::-webkit-scrollbar {
  width: 6px;
}

.result-card::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.result-card::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.result-card::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.config-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border: 2px solid #e8eaf6;
}

.config-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-row {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.config-row .config-item {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-icon {
  font-size: 20px;
}

.config-item {
  margin-bottom: 0;
}

.config-item:last-child {
  margin-bottom: 0;
}

.inline-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  padding: 12px;
  background: #f8f9ff;
  border-radius: 8px;
  animation: slideDown 0.3s ease;
  min-height: 80px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}

.inline-option {
  flex: 1;
  min-width: 200px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #f0f0f0;
}

.config-select.small,
.range-slider.small {
  font-size: 13px;
}

.threshold-value.small {
  font-size: 12px;
}

.config-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.threshold-value {
  float: right;
  color: #667eea;
  font-weight: 700;
}

.config-select {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  transition: all 0.3s ease;
}

.config-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.config-select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.toggle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.toggle-switch {
  position: relative;
  width: 48px;
  height: 26px;
  background: #e0e0e0;
  border-radius: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-switch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-switch.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.toggle-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch.active .toggle-slider {
  left: 25px;
}

.range-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  appearance: none;
  cursor: pointer;
}

.range-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  transition: all 0.2s ease;
}

.range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.range-slider:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s ease;
}

.checkbox-label:hover {
  color: #667eea;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #667eea;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.action-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: #f5f5f5;
  color: #666;
  border: 2px solid #e0e0e0;
}

.action-btn.secondary:hover:not(.disabled) {
  background: #e8eaf6;
  transform: translateY(-2px);
}

.action-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.card-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.understanding-item {
  margin-bottom: 12px;
}

.understanding-item:last-child {
  margin-bottom: 0;
}

.item-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  display: block;
}

.item-value {
  font-size: 14px;
  color: #333;
  padding: 8px 12px;
  background: #f8f9ff;
  border-radius: 6px;
  display: inline-block;
}

.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.retrieval-bubble {
  background: #f8f9ff;
  border: 2px solid #e8eaf6;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retrieval-bubble:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.bubble-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.bubble-icon {
  font-size: 18px;
}

.bubble-text {
  font-size: 14px;
  color: #333;
  flex: 1;
}

.bubble-scores {
  display: flex;
  gap: 12px;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.score-label {
  font-size: 11px;
  color: #999;
}

.score-value {
  font-size: 14px;
  font-weight: 700;
}

.score-value.similarity {
  color: #667eea;
}

.score-value.rank {
  color: #764ba2;
}

.bubble-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  animation: expandIn 0.3s ease;
}

@keyframes expandIn {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

.detail-content {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
}

.detail-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.detail-metadata {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metadata-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.metadata-label {
  color: #666;
  font-weight: 500;
}

.metadata-value {
  color: #333;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 16px;
  border: 2px dashed #e0e0e0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #666;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.empty-state.small {
  padding: 40px 16px;
}

.empty-state.small .empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.empty-state.small .empty-text {
  font-size: 14px;
}

.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  animation: slideInRight 0.3s ease;
  z-index: 1000;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.success-toast {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: #fff;
}

.toast-icon {
  font-size: 20px;
  font-weight: 700;
}

.toast-message {
  font-size: 15px;
  font-weight: 600;
}

@media (max-width: 1200px) {
  .chat-layout {
    flex-direction: column;
    padding: 16px;
    overflow-y: auto;
  }

  .left-panel,
  .right-panel {
    flex: none;
    width: 100%;
    overflow: visible;
  }

  .right-panel {
    order: -1;
    max-height: none;
  }

  .config-row {
    flex-direction: column;
  }

  .results-layout {
    flex-direction: column;
  }

  .query-understanding-panel,
  .retrieval-results-panel {
    flex: none;
    max-height: 300px;
  }

  .results-section {
    flex: none;
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .chat-layout {
    padding: 12px;
    gap: 16px;
  }

  .header-content h1 {
    font-size: 20px;
  }

  .config-card,
  .result-card {
    padding: 12px;
  }

  .bubble-scores {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-btn {
    width: 100%;
  }

  .toast {
    top: 12px;
    right: 12px;
    padding: 12px 16px;
  }

  .toast-message {
    font-size: 14px;
  }

  .inline-options {
    flex-direction: column;
  }

  .inline-option {
    min-width: 100%;
  }
}
</style>
