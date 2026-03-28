import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import ChatView from '../views/ChatView.vue'
import EvaluationView from '../views/EvaluationView.vue'
import ModelView from '../views/ModelView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          redirect: '/knowledge'
        },
        {
          path: 'knowledge',
          name: 'knowledge',
          component: KnowledgeView,
        },
        {
          path: 'chat',
          name: 'chat',
          component: ChatView,
        },
        {
          path: 'evaluation',
          name: 'evaluation',
          component: EvaluationView,
        },
        {
          path: 'model',
          name: 'model',
          component: ModelView,
        },
      ],
    },
  ],
})

export default router
