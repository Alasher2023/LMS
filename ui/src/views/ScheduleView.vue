<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { Select, Paper } from '@/assets/types'
import SelectComponent from '@/components/SelectComponent.vue'
import api from '@/utils/api'

const api_path = '/paper/'

// --- START: Static Options (copied from PaperView and extended) ---
const subjectOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '国语' },
  { value: '2', label: '算数' },
]
const gradeOptions: Select[] = [
  { value: '1', label: '一年级' },
  { value: '2', label: '二年级' },
]
const authorOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: 'Sapix' },
  { value: '2', label: '浜学園' },
  { value: '3', label: 'KUMON' },
]
const statusOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '未开始' },
  { value: '2', label: '进行中' },
  { value: '3', label: '已完成' },
  { value: '4', label: '未复习' },
  { value: '5', label: '复习中' },
]
// Extended typeOptions to include non-academic types
const typeOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '测验' },
  { value: '2', label: '练习题' },
  { value: '3', label: '考试' },
  { value: '4', label: '讲义' },
  { value: '5', label: '其他' },
  { value: '6', label: '个人安排' }, // New non-academic type
]
const academicTypes = ['1', '2', '3', '4', '5'];
// --- END: Static Options ---


// --- START: Calendar State ---
const currentDate = ref(new Date())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())
const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
const weekDays = ['日', '一', '二', '三', '四', '五', '六']
// --- END: Calendar State ---


// --- START: Modal and Dialog State ---
const itemDialog = ref<HTMLDialogElement | null>(null)
const dialogData = reactive<Partial<Paper>>({})
const isAcademicType = computed(() => dialogData.type ? academicTypes.includes(dialogData.type) : false)
// --- END: Modal and Dialog State ---


// --- START: Data ---
const allPapers = ref<Paper[]>([])
const error = ref<string | unknown>('')
// --- END: Data ---


// --- START: Calendar Logic ---
const daysInMonth = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const date = new Date(year, month, 1)
  const days = []

  // Pad with days from previous month
  const startDayOfWeek = date.getDay()
  const prevMonthLastDate = new Date(year, month, 0)
  for (let i = startDayOfWeek; i > 0; i--) {
    const prevDate = new Date(prevMonthLastDate)
    prevDate.setDate(prevMonthLastDate.getDate() - i + 1)
    days.push({ date: prevDate, isCurrentMonth: false, events: [] })
  }

  // Add days of the current month
  const daysInCurrentMonth = new Date(year, month + 1, 0).getDate()
  for (let i = 1; i <= daysInCurrentMonth; i++) {
    const fullDate = new Date(year, month, i)
    days.push({ date: fullDate, isCurrentMonth: true, events: getEventsForDate(fullDate) })
  }

  // Pad with days from next month
  const endDayOfWeek = new Date(year, month, daysInCurrentMonth).getDay()
  for (let i = 1; i < 7 - endDayOfWeek; i++) {
    const nextDate = new Date(year, month + 1, i)
    days.push({ date: nextDate, isCurrentMonth: false, events: [] })
  }

  return days
})

const getEventsForDate = (date: Date) => {
  const dateStr = date.toISOString().split('T')[0]
  return allPapers.value.filter(p => {
    const eventDateStr = p.due_date ? new Date(p.due_date).toISOString().split('T')[0] :
                         p.next_review_date ? new Date(p.next_review_date).toISOString().split('T')[0] : null
    return eventDateStr === dateStr
  })
}

const prevMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1)
  fetchPapersForMonth()
}

const nextMonth = () => {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1)
  fetchPapersForMonth()
}
// --- END: Calendar Logic ---


// --- START: API Calls ---
const fetchPapersForMonth = async () => {
  const year = currentYear.value
  const month = currentMonth.value
  const startDate = new Date(year, month, 1)
  const endDate = new Date(year, month + 1, 0)

  try {
    const res = await api.get(api_path, {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    })
    allPapers.value = res.data
  } catch (err) {
    error.value = err
  }
}

const handleCommit = async () => {
  if (!dialogData.title || !dialogData.type) {
    alert('标题和类型为必填项');
    return;
  }
  try {
    if (dialogData.id) {
      // Update existing paper
      await api.put(api_path, dialogData)
    } else {
      // Create new paper
      await api.post(api_path, dialogData)
    }
    await fetchPapersForMonth() // Refresh data
    closeItemDialog()
  } catch (err) {
    error.value = err
    alert('提交失败')
  }
}

const handleDelete = async (id: number | undefined) => {
  if (!id || !confirm('确定删除吗？')) return
  try {
    await api.delete(`${api_path}${id}/`)
    await fetchPapersForMonth() // Refresh data
    closeItemDialog()
  } catch (err) {
    error.value = err
    alert('删除失败')
  }
}

const handleStatusUpdate = async (paper: Paper, newStatus: string) => {
    try {
        await api.put(`${api_path}${paper.id}/status`, { status: newStatus });
        if (newStatus === '3') { // 已完成
            if (paper.last_reviewed_at) { // It has been reviewed before
                await api.post(`${api_path}${paper.id}/review`);
            } else { // First time completion
                await api.post(`${api_path}${paper.id}/complete`);
            }
        }
        await fetchPapersForMonth(); // Refresh data
    } catch (err) {
        error.value = err;
        alert('状态更新失败');
    }
};
// --- END: API Calls ---


// --- START: Dialog/Modal Handlers ---
const openItemDialog = (paper?: Paper, date?: Date) => {
  if (paper) {
    // Editing existing paper
    Object.assign(dialogData, paper)
  } else {
    // Creating new paper
    Object.assign(dialogData, {
      id: undefined,
      title: '',
      description: '',
      type: '6', // Default to personal
      status: '1', // Default to not started
      subject: '1',
      grade: '1',
      author: '1',
      path: '',
      memo: '',
      due_date: date ? date.toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
    })
  }
  itemDialog.value?.showModal()
}

const closeItemDialog = () => {
  itemDialog.value?.close()
}

const getStatusColorClass = (status: string | undefined) => {
  if (!status) return 'bg-transparent'
  return {
    '1': 'bg-gray-400',   // 未开始
    '2': 'bg-blue-500',   // 进行中
    '3': 'bg-green-500',  // 已完成
    '4': 'bg-yellow-500', // 未复习
    '5': 'bg-blue-500',   // 复习中
  }[status] || 'bg-gray-400'
}
// --- END: Dialog/Modal Handlers ---

onMounted(() => {
  fetchPapersForMonth()
})

</script>

<template>
  <div class="p-4 h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">{{ currentYear }} 年 {{ monthNames[currentMonth] }}</h2>
      <div class="flex items-center gap-2">
        <button class="btn btn-sm btn-outline" @click="prevMonth">上个月</button>
        <button class="btn btn-sm btn-outline" @click="nextMonth">下个月</button>
        <button class="btn btn-sm btn-primary" @click="openItemDialog(undefined, new Date())">新增日程</button>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7 gap-1 flex-grow">
      <!-- Weekday Headers -->
      <div v-for="day in weekDays" :key="day" class="text-center font-bold p-2 border-b">{{ day }}</div>
      
      <!-- Calendar Days -->
      <div 
        v-for="(day, index) in daysInMonth" 
        :key="index" 
        @click="openItemDialog(undefined, day.date)"
        class="border rounded-lg p-2 flex flex-col cursor-pointer hover:bg-base-200"
        :class="{ 'bg-base-300': !day.isCurrentMonth, 'bg-base-100': day.isCurrentMonth }"
      >
        <span :class="{ 'text-gray-500': !day.isCurrentMonth }">{{ day.date.getDate() }}</span>
        <div class="flex-grow mt-1 space-y-1 overflow-y-auto">
          <div 
            v-for="event in day.events" 
            :key="event.id"
            @click.stop="openItemDialog(event)"
            class="text-xs p-1 rounded-md text-white flex items-center gap-1.5"
            :class="{
              'bg-primary': event.type === '1' || event.type === '2',
              'bg-secondary': event.type === '3',
              'bg-accent': event.type === '4' || event.type === '5',
              'bg-info': event.type === '6',
            }"
          >
            <div class="w-2 h-2 rounded-full flex-shrink-0" :class="getStatusColorClass(event.status)"></div>
            <span class="truncate" :class="{ 'line-through': event.status === '3' }">{{ event.title }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Add/Edit Item Dialog -->
  <dialog ref="itemDialog" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg">{{ dialogData.id ? '编辑日程' : '新增日程' }}</h3>
      
      <div class="form-control w-full">
        <label class="label"><span class="label-text">标题*</span></label>
        <input type="text" v-model="dialogData.title" class="input input-bordered w-full" />
      </div>

      <div class="form-control w-full">
        <label class="label"><span class="label-text">类型*</span></label>
        <select-component v-model="dialogData.type" :options="typeOptions.filter(o => o.value !== '0')" class="w-full"></select-component>
      </div>

      <div v-if="isAcademicType">
        <div class="form-control w-full">
          <label class="label"><span class="label-text">年级</span></label>
          <select-component v-model="dialogData.grade" :options="gradeOptions" class="w-full"></select-component>
        </div>
        <div class="form-control w-full">
          <label class="label"><span class="label-text">科目</span></label>
          <select-component v-model="dialogData.subject" :options="subjectOptions.filter(o => o.value !== '0')" class="w-full"></select-component>
        </div>
        <div class="form-control w-full">
          <label class="label"><span class="label-text">机构</span></label>
          <select-component v-model="dialogData.author" :options="authorOptions.filter(o => o.value !== '0')" class="w-full"></select-component>
        </div>
        <div class="form-control w-full">
          <label class="label"><span class="label-text">网盘地址</span></label>
          <input type="text" v-model="dialogData.path" class="input input-bordered w-full" />
        </div>
      </div>

      <div class="form-control w-full">
        <label class="label"><span class="label-text">状态</span></label>
        <select-component v-model="dialogData.status" :options="statusOptions.filter(o => o.value !== '0')" class="w-full" @change="handleStatusUpdate(dialogData, $event.target.value)"></select-component>
      </div>

      <div class="form-control w-full">
        <label class="label"><span class="label-text">安排日期</span></label>
        <input type="date" v-model="dialogData.due_date" class="input input-bordered w-full" />
      </div>

      <div class="form-control w-full">
        <label class="label"><span class="label-text">备注</span></label>
        <textarea v-model="dialogData.memo" class="textarea textarea-bordered w-full"></textarea>
      </div>

      <div class="modal-action">
        <button class="btn btn-primary" @click="handleCommit">提交</button>
        <button v-if="dialogData.id" class="btn btn-error" @click="handleDelete(dialogData.id)">删除</button>
        <button class="btn" @click="closeItemDialog">关闭</button>
      </div>
    </div>
  </dialog>
</template>