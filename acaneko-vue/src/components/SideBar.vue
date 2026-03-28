<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

interface NavItem {
  id: string
  name: string
  path: string
  icon: string
}

const navItems = ref<NavItem[]>([
  {
    id: 'knowledge',
    name: '知识库管理',
    path: '/knowledge',
    icon: '📚'
  },
  {
    id: 'chat',
    name: 'chat问答',
    path: '/chat',
    icon: '💬'
  },
  {
    id: 'evaluation',
    name: '测试集评估',
    path: '/evaluation',
    icon: '📊'
  },
  {
    id: 'model',
    name: '模型测试',
    path: '/model',
    icon: '🧪'
  }
])

const activeItem = computed(() => route.path)

const handleNavClick = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="sidebar-container">
    <div class="logo-section">
      <div class="logo-icon">🚀</div>
      <h1 class="logo-text">RAG测试平台</h1>
    </div>

    <nav class="nav-menu">
      <div
        v-for="item in navItems"
        :key="item.id"
        class="nav-item"
        :class="{ active: activeItem === item.path }"
        @click="handleNavClick(item.path)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-text">{{ item.name }}</span>
        <div class="nav-indicator"></div>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="footer-info">
        <p class="version">v1.0.0</p>
        <p class="copyright">© 2024 Acaneko</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  box-sizing: border-box;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  margin-bottom: 32px;
  border-bottom: 2px solid #f0f0f0;
}

.logo-icon {
  font-size: 32px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 0.5px;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  background: transparent;
  border: 2px solid transparent;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
}

.nav-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.nav-item:hover::before {
  opacity: 0.1;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  transform: translateX(4px);
}

.nav-item.active::before {
  opacity: 1;
}

.nav-icon {
  font-size: 20px;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-item.active .nav-icon {
  transform: scale(1.15);
}

.nav-text {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.nav-item:hover .nav-text {
  color: #667eea;
}

.nav-item.active .nav-text {
  color: #fff;
}

.nav-indicator {
  position: absolute;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s ease;
}

.nav-item.active .nav-indicator {
  opacity: 1;
  transform: scale(1);
  background: #fff;
}

.sidebar-footer {
  padding-top: 24px;
  border-top: 2px solid #f0f0f0;
}

.footer-info {
  text-align: center;
}

.version {
  font-size: 12px;
  color: #999;
  margin: 0 0 4px 0;
  font-weight: 500;
}

.copyright {
  font-size: 11px;
  color: #bbb;
  margin: 0;
}

@media (max-width: 1024px) {
  .sidebar-container {
    padding: 20px;
  }

  .logo-section {
    margin-bottom: 24px;
  }

  .logo-icon {
    font-size: 28px;
  }

  .logo-text {
    font-size: 18px;
  }

  .nav-item {
    padding: 12px 16px;
  }

  .nav-text {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .sidebar-container {
    padding: 16px;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    height: auto;
  }

  .logo-section {
    margin-bottom: 0;
    border-bottom: none;
    padding: 8px 0;
  }

  .logo-icon {
    font-size: 24px;
  }

  .logo-text {
    font-size: 16px;
  }

  .nav-menu {
    flex-direction: row;
    gap: 4px;
    flex: 0;
  }

  .nav-item {
    padding: 10px 14px;
  }

  .nav-text {
    display: none;
  }

  .nav-icon {
    font-size: 18px;
  }

  .sidebar-footer {
    display: none;
  }

  .nav-item:hover {
    transform: translateY(-2px);
  }

  .nav-item.active {
    transform: translateY(-2px);
  }
}
</style>
