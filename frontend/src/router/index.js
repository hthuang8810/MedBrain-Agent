import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Chat from '@/views/Chat.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: Login,
  },
  {
    path: '/chat',
    name: 'chat',
    component: Chat,
    meta: { requireAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('userId')
  if (to.meta.requireAuth && !userId) {
    next('/')
  } else {
    next()
  }
})

export default router
