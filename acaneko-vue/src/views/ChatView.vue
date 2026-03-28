<script setup lang="ts">
import { ref, nextTick } from 'vue'

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

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

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

  setTimeout(() => {
    const assistantMessage: Message = {
      id: Date.now(),
      type: 'assistant',
      content: `这是一个模拟的AI回复。您的问题是："${userQuery}"。在实际应用中，这里会调用后端API进行RAG检索和生成回答。`,
      timestamp: new Date().toLocaleTimeString()
    }
    messages.value.push(assistantMessage)
    isLoading.value = false
    scrollToBottom()
  }, 1000)
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
}
</script>

<template>
  <div class="chat-page">
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
</template>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
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
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9ff;
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
}

.message.assistant .message-text {
  border-radius: 12px 12px 12px 0;
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-content h1 {
    font-size: 24px;
  }

  .clear-btn {
    width: 100%;
    justify-content: center;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-input {
    font-size: 16px;
  }
}
</style>
