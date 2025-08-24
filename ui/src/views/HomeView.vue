<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import ActivityChart from '@/components/ActivityChart.vue'
import type { Paper } from '@/assets/types'

interface StatsCards {
  pending_review_count: number
  in_progress_count: number
  completed_this_week_count: number
}

interface ActivityData {
  date: string
  count: number
}

const router = useRouter()

const tasksDueToday = ref<Paper[]>([])
const tasksToReview = ref<Paper[]>([])
const statsCards = ref<StatsCards>({ pending_review_count: 0, in_progress_count: 0, completed_this_week_count: 0 })
const activityChartData = ref<ActivityData[]>([])

const loading = ref(true)
const error = ref<string | null>(null)

const fetchData = async () => {
  try {
    loading.value = true
    const res = await api.get('/dashboard/stats')
    tasksDueToday.value = res.data.tasks_due_today
    tasksToReview.value = res.data.tasks_to_review
    statsCards.value = res.data.stats_cards
    activityChartData.value = res.data.activity_chart
  } catch (err) {
    error.value = 'Failed to load dashboard data.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const navigateTo = (path: string) => {
  router.push(path)
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="p-4 md:p-6">
    <div v-if="loading" class="text-center">
      <span class="loading loading-lg loading-spinner"></span>
    </div>
    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
    </div>
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Left Column: Task Lists -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Today's Agenda -->
        <div>
          <h2 class="text-2xl font-bold mb-4">今日待办</h2>
          <div v-if="tasksDueToday.length > 0" class="space-y-3">
            <div v-for="task in tasksDueToday" :key="task.id" class="card bg-base-200 shadow-sm">
              <div class="card-body p-4">
                <h3 class="card-title text-base">{{ task.title }}</h3>
                <div class="card-actions justify-end">
                  <button class="btn btn-sm btn-primary" @click="navigateTo('/schedule')">查看</button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center p-4 bg-base-200 rounded-lg">
            <p>今天没有安排的任务。</p>
          </div>
        </div>

        <!-- To Review List -->
        <div>
          <h2 class="text-2xl font-bold mb-4">待复习</h2>
          <div v-if="tasksToReview.length > 0" class="space-y-3">
            <div v-for="task in tasksToReview" :key="task.id" class="card bg-base-200 shadow-sm">
              <div class="card-body p-4">
                <h3 class="card-title text-base">{{ task.title }}</h3>
                 <div class="card-actions justify-end">
                  <button class="btn btn-sm btn-secondary" @click="navigateTo('/schedule')">开始复习</button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center p-4 bg-base-200 rounded-lg">
            <p>没有需要复习的项目。</p>
          </div>
        </div>
      </div>

      <!-- Right Column: Stats and Actions -->
      <div class="space-y-6">
        <!-- Stats Cards -->
        <div>
          <h2 class="text-2xl font-bold mb-4">数据一览</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-1 gap-4">
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">待复习</div>
              <div class="stat-value text-warning">{{ statsCards.pending_review_count }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">进行中</div>
              <div class="stat-value text-info">{{ statsCards.in_progress_count }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">本周已完成</div>
              <div class="stat-value text-success">{{ statsCards.completed_this_week_count }}</div>
            </div>
          </div>
        </div>

        <!-- Activity Chart -->
        <div>
          <h2 class="text-2xl font-bold mb-4">学习活动</h2>
          <div class="p-4 bg-base-200 rounded-lg h-64">
            <ActivityChart v-if="activityChartData.length" :activity-data="activityChartData" />
          </div>
        </div>

        <!-- Quick Actions -->
        <div>
          <h2 class="text-2xl font-bold mb-4">快捷操作</h2>
          <div class="flex flex-col gap-3">
            <button class="btn btn-primary" @click="navigateTo('/paper')">添加新试卷</button>
            <button class="btn btn-secondary" @click="navigateTo('/schedule')">查看日历</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>