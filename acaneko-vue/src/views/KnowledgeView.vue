<script setup lang="ts">
import { ref } from 'vue'

interface KnowledgeBase {
  id: number
  name: string
  description: string
  documentCount: number
  createdAt: string
  status: 'active' | 'inactive'
  chunkSize: number
  overlapSize: number
  vectorModel: string
  language: string
}

interface Document {
  id: number
  name: string
  size: number
  uploadTime: string
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  chunks: number
}

const vectorModels = [
  { value: 'openai-ada-002', label: 'OpenAI Ada-002' },
  { value: 'openai-3-small', label: 'OpenAI Embedding-3 Small' },
  { value: 'openai-3-large', label: 'OpenAI Embedding-3 Large' },
  { value: 'bge-small', label: 'BGE-Small' },
  { value: 'bge-large', label: 'BGE-Large' }
]

const languages = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-TW', label: '繁体中文' },
  { value: 'en', label: '英语' },
  { value: 'ms', label: '马来语' },
  { value: 'es', label: '西班牙语' }
]

const knowledgeBases = ref<KnowledgeBase[]>([
  {
    id: 1,
    name: '技术文档库',
    description: '包含公司所有技术文档和API文档',
    documentCount: 156,
    createdAt: '2024-01-15',
    status: 'active',
    chunkSize: 500,
    overlapSize: 50,
    vectorModel: 'openai-3-small',
    language: 'zh-CN'
  },
  {
    id: 2,
    name: '产品手册库',
    description: '产品使用手册和用户指南',
    documentCount: 89,
    createdAt: '2024-02-20',
    status: 'active',
    chunkSize: 400,
    overlapSize: 40,
    vectorModel: 'bge-small',
    language: 'zh-CN'
  },
  {
    id: 3,
    name: '培训资料库',
    description: '员工培训和学习资料',
    documentCount: 234,
    createdAt: '2024-03-10',
    status: 'inactive',
    chunkSize: 600,
    overlapSize: 60,
    vectorModel: 'openai-ada-002',
    language: 'en'
  }
])

const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedKnowledgeBase = ref<KnowledgeBase | null>(null)
const newKnowledgeBase = ref({
  name: '',
  description: '',
  chunkSize: 500,
  overlapSize: 50,
  vectorModel: 'openai-3-small',
  language: 'zh-CN'
})

const documents = ref<Document[]>([
  {
    id: 1,
    name: 'API开发指南.pdf',
    size: 2456789,
    uploadTime: '2024-03-29 10:30:00',
    status: 'completed',
    chunks: 156
  },
  {
    id: 2,
    name: '系统架构设计.docx',
    size: 1234567,
    uploadTime: '2024-03-29 11:15:00',
    status: 'completed',
    chunks: 89
  },
  {
    id: 3,
    name: '用户手册.pdf',
    size: 3456789,
    uploadTime: '2024-03-29 14:20:00',
    status: 'parsing',
    chunks: 0
  },
  {
    id: 4,
    name: '常见问题解答.md',
    size: 567890,
    uploadTime: '2024-03-29 15:45:00',
    status: 'pending',
    chunks: 0
  }
])

const selectedDocuments = ref<number[]>([])
const isParsing = ref(false)
const uploadProgress = ref(0)
const isUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const handleCreate = () => {
  const newId = Math.max(...knowledgeBases.value.map(kb => kb.id)) + 1
  knowledgeBases.value.unshift({
    id: newId,
    name: newKnowledgeBase.value.name,
    description: newKnowledgeBase.value.description,
    documentCount: 0,
    createdAt: new Date().toISOString().split('T')[0],
    status: 'active',
    chunkSize: newKnowledgeBase.value.chunkSize,
    overlapSize: newKnowledgeBase.value.overlapSize,
    vectorModel: newKnowledgeBase.value.vectorModel,
    language: newKnowledgeBase.value.language
  })
  newKnowledgeBase.value = {
    name: '',
    description: '',
    chunkSize: 500,
    overlapSize: 50,
    vectorModel: 'openai-3-small',
    language: 'zh-CN'
  }
  showCreateModal.value = false
}

const handleDelete = (id: number) => {
  knowledgeBases.value = knowledgeBases.value.filter(kb => kb.id !== id)
}

const toggleStatus = (id: number) => {
  const kb = knowledgeBases.value.find(kb => kb.id === id)
  if (kb) {
    kb.status = kb.status === 'active' ? 'inactive' : 'active'
  }
}

const openDetailModal = (kb: KnowledgeBase) => {
  selectedKnowledgeBase.value = kb
  showDetailModal.value = true
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待解析',
    parsing: '解析中',
    completed: '已完成',
    failed: '解析失败'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string) => {
  return status
}

const toggleDocumentSelection = (id: number) => {
  const index = selectedDocuments.value.indexOf(id)
  if (index > -1) {
    selectedDocuments.value.splice(index, 1)
  } else {
    selectedDocuments.value.push(id)
  }
}

const handleUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (!files || files.length === 0) return
  
  isUploading.value = true
  uploadProgress.value = 0
  
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      isUploading.value = false
      uploadProgress.value = 0
      
      Array.from(files).forEach(file => {
        const newDoc: Document = {
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          uploadTime: new Date().toLocaleString(),
          status: 'pending',
          chunks: 0
        }
        documents.value.unshift(newDoc)
      })
      
      if (selectedKnowledgeBase.value) {
        selectedKnowledgeBase.value.documentCount += files.length
      }
      
      if (target) {
        target.value = ''
      }
    }
  }, 200)
}

const handleBatchDelete = () => {
  if (selectedDocuments.value.length === 0) return
  
  documents.value = documents.value.filter(doc => !selectedDocuments.value.includes(doc.id))
  selectedDocuments.value = []
  
  if (selectedKnowledgeBase.value) {
    selectedKnowledgeBase.value.documentCount = documents.value.length
  }
}

const handleStartParsing = () => {
  isParsing.value = true
  
  documents.value.forEach(doc => {
    if (doc.status === 'pending') {
      doc.status = 'parsing'
    }
  })
  
  setTimeout(() => {
    documents.value.forEach(doc => {
      if (doc.status === 'parsing') {
        doc.status = 'completed'
        doc.chunks = Math.floor(Math.random() * 200) + 50
      }
    })
    isParsing.value = false
  }, 3000)
}
</script>

<template>
  <div class="knowledge-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">📚 知识库管理</h1>
        <p class="page-subtitle">管理和维护您的知识库资源</p>
      </div>
      <button class="create-btn" @click="showCreateModal = true">
        <span class="btn-icon">+</span>
        <span class="btn-text">创建知识库</span>
      </button>
    </div>

    <div class="knowledge-grid">
      <div
        v-for="kb in knowledgeBases"
        :key="kb.id"
        class="knowledge-card"
        @click="openDetailModal(kb)"
      >
        <div class="card-header">
          <div class="card-icon">📁</div>
          <div class="card-status" :class="kb.status">
            {{ kb.status === 'active' ? '启用' : '禁用' }}
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title">{{ kb.name }}</h3>
          <div class="config-tag">
            {{ languages.find(l => l.value === kb.language)?.label }} | {{ vectorModels.find(m => m.value === kb.vectorModel)?.label }} | {{ kb.chunkSize }}-{{ kb.overlapSize }}
          </div>
          <p class="card-description">{{ kb.description }}</p>
          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-label">文档数量</span>
              <span class="stat-value">{{ kb.documentCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">创建时间</span>
              <span class="stat-value">{{ kb.createdAt }}</span>
            </div>
          </div>
        </div>
        <div class="card-footer" @click.stop>
          <button class="action-btn" @click="toggleStatus(kb.id)">
            {{ kb.status === 'active' ? '禁用' : '启用' }}
          </button>
          <button class="action-btn delete" @click="handleDelete(kb.id)">
            删除
          </button>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">创建新知识库</h2>
        <div class="form-group">
          <label class="form-label">知识库名称</label>
          <input
            v-model="newKnowledgeBase.name"
            class="form-input"
            placeholder="请输入知识库名称"
          />
        </div>
        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea
            v-model="newKnowledgeBase.description"
            class="form-textarea"
            placeholder="请输入知识库描述"
            rows="3"
          ></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">分块大小</label>
            <input
              v-model.number="newKnowledgeBase.chunkSize"
              type="number"
              class="form-input"
              placeholder="500"
              min="100"
              max="2000"
            />
          </div>
          <div class="form-group">
            <label class="form-label">切片重叠大小</label>
            <input
              v-model.number="newKnowledgeBase.overlapSize"
              type="number"
              class="form-input"
              placeholder="50"
              min="0"
              max="500"
            />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">向量模型</label>
            <select v-model="newKnowledgeBase.vectorModel" class="form-select">
              <option
                v-for="model in vectorModels"
                :key="model.value"
                :value="model.value"
              >
                {{ model.label }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">知识库语言</label>
            <select v-model="newKnowledgeBase.language" class="form-select">
              <option
                v-for="lang in languages"
                :key="lang.value"
                :value="lang.value"
              >
                {{ lang.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="showCreateModal = false">
            取消
          </button>
          <button class="modal-btn confirm" @click="handleCreate">
            创建
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDetailModal" class="modal-overlay large" @click="showDetailModal = false">
      <div class="modal-content large" @click.stop>
        <div class="detail-header">
          <div class="detail-info">
            <h2 class="detail-title">{{ selectedKnowledgeBase?.name }}</h2>
            <p class="detail-description">{{ selectedKnowledgeBase?.description }}</p>
          </div>
          <button class="close-btn" @click="showDetailModal = false">✕</button>
        </div>

        <div class="detail-config">
          <div class="config-item">
            <span class="config-label">分块大小</span>
            <span class="config-value">{{ selectedKnowledgeBase?.chunkSize }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">重叠大小</span>
            <span class="config-value">{{ selectedKnowledgeBase?.overlapSize }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">向量模型</span>
            <span class="config-value">{{ vectorModels.find(m => m.value === selectedKnowledgeBase?.vectorModel)?.label }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">语言</span>
            <span class="config-value">{{ languages.find(l => l.value === selectedKnowledgeBase?.language)?.label }}</span>
          </div>
        </div>

        <input
          ref="fileInputRef"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md"
          style="display: none"
          @change="handleFileChange"
        />

        <div class="detail-actions">
          <button
            class="action-btn primary"
            :class="{ disabled: isUploading }"
            @click="handleUpload"
          >
            <span class="btn-icon">{{ isUploading ? '⏳' : '📤' }}</span>
            <span class="btn-text">{{ isUploading ? `上传中 ${uploadProgress}%` : '上传文档' }}</span>
          </button>
          <button
            class="action-btn danger"
            :class="{ disabled: selectedDocuments.length === 0 }"
            @click="handleBatchDelete"
          >
            <span class="btn-icon">🗑️</span>
            <span class="btn-text">批量删除 ({{ selectedDocuments.length }})</span>
          </button>
          <button
            class="action-btn success"
            :class="{ disabled: isParsing }"
            @click="handleStartParsing"
          >
            <span class="btn-icon">{{ isParsing ? '⏳' : '🚀' }}</span>
            <span class="btn-text">{{ isParsing ? '解析中...' : '开始解析' }}</span>
          </button>
        </div>

        <div class="documents-list">
          <div class="list-header">
            <div class="header-checkbox">
              <input
                type="checkbox"
                id="select-all"
                :checked="selectedDocuments.length === documents.length && documents.length > 0"
                @change="selectedDocuments = $event.target.checked ? documents.map(d => d.id) : []"
              />
              <label for="select-all" class="checkbox-label"></label>
            </div>
            <span class="header-title">文档列表</span>
            <span class="header-count">{{ documents.length }} 个文档</span>
          </div>

          <div class="documents-container">
            <div
              v-for="doc in documents"
              :key="doc.id"
              class="document-item"
              :class="{ selected: selectedDocuments.includes(doc.id) }"
            >
              <div class="doc-checkbox">
                <input
                  type="checkbox"
                  :id="`doc-${doc.id}`"
                  :checked="selectedDocuments.includes(doc.id)"
                  @change="toggleDocumentSelection(doc.id)"
                />
                <label :for="`doc-${doc.id}`" class="checkbox-label"></label>
              </div>
              <div class="doc-icon">📄</div>
              <div class="doc-info">
                <div class="doc-name">{{ doc.name }}</div>
                <div class="doc-meta">
                  <span class="doc-size">{{ formatFileSize(doc.size) }}</span>
                  <span class="doc-time">{{ doc.uploadTime }}</span>
                </div>
              </div>
              <div class="doc-status" :class="getStatusClass(doc.status)">
                <span class="status-text">{{ getStatusText(doc.status) }}</span>
                <span v-if="doc.chunks > 0" class="status-chunks">{{ doc.chunks }} 个分块</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-page {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
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

.create-btn {
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

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-icon {
  font-size: 20px;
  font-weight: 700;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.knowledge-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 32px;
}

.card-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.card-status.active {
  background: #e8f5e9;
  color: #4caf50;
}

.card-status.inactive {
  background: #ffebee;
  color: #f44336;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #333;
}

.config-tag {
  display: inline-block;
  padding: 6px 14px;
  background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
  color: #7b1fa2;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(123, 31, 162, 0.15);
  transition: all 0.3s ease;
}

.config-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(123, 31, 162, 0.25);
}

.card-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.card-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding-top: 16px;
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

.action-btn.delete:hover {
  border-color: #f44336;
  color: #f44336;
  background: #ffebee;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 24px 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: #fff;
  cursor: pointer;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.modal-btn.cancel:hover {
  background: #e0e0e0;
}

.modal-btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.modal-btn.confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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

  .create-btn {
    width: 100%;
    justify-content: center;
  }

  .knowledge-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    padding: 24px;
  }
}

.modal-overlay.large {
  z-index: 1001;
}

.modal-content.large {
  width: 95%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.detail-info h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #333;
}

.detail-description {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.6;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: 2px solid #e0e0e0;
  background: #fff;
  color: #666;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  border-color: #f44336;
  color: #f44336;
  background: #ffebee;
  transform: rotate(90deg);
}

.detail-config {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9ff;
  border-radius: 12px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  font-size: 12px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-value {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.detail-actions .action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  white-space: nowrap;
}

.detail-actions .action-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.detail-actions .action-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.detail-actions .action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.detail-actions .action-btn.danger {
  background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
  color: #fff;
}

.detail-actions .action-btn.success {
  background: linear-gradient(135deg, #4caf50 0%, #43a047 100%);
  color: #fff;
}

.documents-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #f8f9ff;
  border-radius: 10px;
  margin-bottom: 16px;
}

.header-checkbox {
  position: relative;
}

.header-checkbox input[type="checkbox"] {
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

.header-checkbox input[type="checkbox"]:checked + .checkbox-label,
.doc-checkbox input[type="checkbox"]:checked + .checkbox-label {
  background: #667eea;
  border-color: #667eea;
}

.header-checkbox input[type="checkbox"]:checked + .checkbox-label::after,
.doc-checkbox input[type="checkbox"]:checked + .checkbox-label::after {
  content: '✓';
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  flex: 1;
}

.header-count {
  font-size: 13px;
  color: #999;
  font-weight: 500;
}

.documents-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.documents-container::-webkit-scrollbar {
  width: 6px;
}

.documents-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.documents-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.documents-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.document-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.document-item.selected {
  border-color: #667eea;
  background: #f8f9ff;
}

.doc-checkbox {
  position: relative;
}

.doc-icon {
  font-size: 24px;
}

.doc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doc-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.doc-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
}

.doc-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  min-width: 100px;
}

.doc-status.pending {
  background: #fff3e0;
  color: #ff9800;
}

.doc-status.parsing {
  background: #e3f2fd;
  color: #2196f3;
}

.doc-status.completed {
  background: #e8f5e9;
  color: #4caf50;
}

.doc-status.failed {
  background: #ffebee;
  color: #f44336;
}

.status-text {
  font-size: 13px;
  font-weight: 600;
}

.status-chunks {
  font-size: 11px;
  color: #666;
}

@media (max-width: 1024px) {
  .detail-config {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .modal-content.large {
    width: 100%;
    max-height: 95vh;
    border-radius: 12px;
  }

  .detail-config {
    grid-template-columns: 1fr;
  }

  .detail-actions {
    flex-direction: column;
  }

  .document-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .doc-status {
    width: 100%;
    align-items: flex-start;
  }
}
</style>
