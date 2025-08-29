import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/schedule',
    name: 'schedule',
    component: () => import('@/views/ScheduleView.vue'),
  },
  {
    path: '/paper',
    name: 'paper',
    component: () => import('@/views/PaperView.vue'),
  },
  {
    path: '/pdf-generator',
    name: 'pdf-generator',
    component: () => import('@/views/PdfGeneratorView.vue'),
    meta: { title: 'PDF Generator' },
  },
  {
    path: '/wrong-question-book',
    name: 'wrong-question-book',
    component: () => import('@/views/WrongQuestionBookView.vue'),
    meta: { title: 'Wrong Question Book' },
  },
]

export default routes
