<script setup lang="ts">
import { ref } from 'vue'
import SideBar from './SideBar.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

window.addEventListener('resize', checkMobile)
checkMobile()
</script>

<template>
  <div class="layout-container">
    <aside class="sidebar">
      <SideBar />
    </aside>
    <main class="main-content">
      <div class="content-wrapper">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar {
  width: 280px;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
  z-index: 100;
  transition: all 0.3s ease;
}

.main-content {
  flex: 1;
  height: 100%;
  overflow: hidden;
  padding: 24px;
  box-sizing: border-box;
}

.content-wrapper {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: auto;
  padding: 32px;
  box-sizing: border-box;
}

.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }

  .main-content {
    padding: 16px;
  }

  .content-wrapper {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }

  .main-content {
    padding: 12px;
  }

  .content-wrapper {
    padding: 20px;
    border-radius: 12px;
  }
}
</style>
