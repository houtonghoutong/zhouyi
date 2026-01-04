import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '周易占卜' }
  },
  {
    path: '/liuyao',
    name: 'LiuYao',
    component: () => import('@/views/LiuYao/IndexPage.vue'),
    meta: { title: '六爻占卜' },
    children: [
      {
        path: '',
        name: 'LiuYaoQuestion',
        component: () => import('@/views/LiuYao/QuestionPage.vue'),
        meta: { title: '问卦' }
      },
      {
        path: 'divine',
        name: 'LiuYaoDivine',
        component: () => import('@/views/LiuYao/DivinePage.vue'),
        meta: { title: '起卦' }
      },
      {
        path: 'result',
        name: 'LiuYaoResult',
        component: () => import('@/views/LiuYao/ResultPage.vue'),
        meta: { title: '卦象解读' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || '周易占卜'
  next()
})

export default router

