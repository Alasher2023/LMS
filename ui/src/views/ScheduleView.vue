<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { Select, Paper } from '@/assets/types'
import SelectComponent from '@/components/SelectComponent.vue'
import api from '@/utils/api'

const api_path = '/paper/'

// --- START: Static Options ---
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
const typeOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '测验' },
  { value: '2', label: '练习题' },
  { value: '3', label: '考试' },
  { value: '4', label: '讲义' },
  { value: '5', label: '其他' },
  { value: '6', label: '个人安排' },
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
const dayEventsDialog = ref<HTMLDialogElement | null>(null)
const selectPaperDialog = ref<HTMLDialogElement | null>(null)
const dialogData = reactive<Partial<Paper>>({})
const selectedDay = ref<{ date: Date, events: Paper[] } | null>(null)
const isAcademicType = computed(() => dialogData.type ? academicTypes.includes(dialogData.type) : false)
// --- END: Modal and Dialog State ---


// --- START: Data ---
const allPapers = ref<Paper[]>([]) // Papers on the calendar
const paperLibrary = ref<Paper[]>([]) // All available papers for selection
const searchQuery = ref('')
const error = ref<string | unknown>('')

const filteredPaperLibrary = computed(() => {
  if (!searchQuery.value) {
    return paperLibrary.value
  }
  return paperLibrary.value.filter(p => 
    p.title?.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
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
    days.push({ date: prevDate, isCurrentMonth: false, events: getEventsForDate(prevDate) })
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
    days.push({ date: nextDate, isCurrentMonth: false, events: getEventsForDate(nextDate) })
  }

  return days
})

const getEventsForDate = (date: Date) => {
  const localDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const localDateTimestamp = localDate.getTime();

  return allPapers.value.filter(p => {
    if (p.next_review_date) {
      const reviewDate = new Date(p.next_review_date);
      const localReviewDate = new Date(reviewDate.getFullYear(), reviewDate.getMonth(), reviewDate.getDate());
      if (localReviewDate.getTime() === localDateTimestamp) {
        return true;
      }
    }

    if (p.start_date) {
      const startDate = new Date(p.start_date);
      const localStartDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      
      const endDate = p.end_date ? new Date(p.end_date) : startDate;
      const localEndDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());

      return localDateTimestamp >= localStartDate.getTime() && localDateTimestamp <= localEndDate.getTime();
    }
    
    return false;
  });
};

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
  const startDate = new Date(year, month - 1, 15)
  const endDate = new Date(year, month + 1, 15)

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

const fetchPaperLibrary = async () => {
  try {
    const res = await api.get(api_path, { params: { academic_only: true } })
    // Filter out papers that are already scheduled
    paperLibrary.value = res.data.filter((p: Paper) => !p.start_date)
  } catch (err) {
    error.value = err
    alert('题库加载失败')
  }
}

const handleCommit = async () => {
  if (!dialogData.title || !dialogData.type) {
    alert('标题和类型为必填项');
    return;
  }
  try {
    if (dialogData.id) {
      await api.put(api_path, dialogData)
    } else {
      await api.post(api_path, dialogData)
    }
    await fetchPapersForMonth()
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
    await fetchPapersForMonth()
    closeItemDialog()
    closeDayEventsDialog()
  } catch (err) {
    error.value = err
    alert('删除失败')
  }
}

const handleStatusUpdate = async (paper: Paper, newStatus: string) => {
    try {
        await api.put(`${api_path}${paper.id}/status`, { status: newStatus });
        if (newStatus === '3') { 
            if (paper.last_reviewed_at) {
                await api.post(`${api_path}${paper.id}/review`);
            } else { 
                await api.post(`${api_path}${paper.id}/complete`);
            }
        }
        await fetchPapersForMonth();
    } catch (err) {
        error.value = err;
        alert('状态更新失败');
    }
};
// --- END: API Calls ---


// --- START: Dialog/Modal Handlers ---
const openDayEventsDialog = (day: { date: Date, events: Paper[] }) => {
  selectedDay.value = day;
  dayEventsDialog.value?.showModal();
}

const closeDayEventsDialog = () => {
  dayEventsDialog.value?.close();
  selectedDay.value = null;
}

const openSelectPaperDialog = async () => {
  await fetchPaperLibrary();
  selectPaperDialog.value?.showModal();
}

const closeSelectPaperDialog = () => {
  selectPaperDialog.value?.close();
}

const handleSelectPaper = (paper: Paper) => {
  closeSelectPaperDialog();
  openItemDialog(paper, new Date());
}

const openItemDialog = (paper?: Paper, date?: Date) => {
  // Helper to format a Date object to a 'YYYY-MM-DD' string consistently
  const formatDate = (d: Date) => {
    const year = d.getFullYear();
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  const initialDate = date ? formatDate(date) : formatDate(new Date());

  if (paper) {
    Object.assign(dialogData, paper);
    // FIX: Directly use the date string part from the backend data (which is ISO 8601 format).
    // This avoids creating a new Date() object from a string, which is the source of the timezone bug.
    dialogData.start_date = paper.start_date ? paper.start_date.split('T')[0] : initialDate;
    dialogData.end_date = paper.end_date ? paper.end_date.split('T')[0] : dialogData.start_date;

  } else {
    // This logic is for creating a brand new, unsaved paper entry
    Object.assign(dialogData, {
      id: undefined,
      title: '',
      description: '',
      type: '6',
      status: '1',
      subject: '1',
      grade: '1',
      author: '1',
      path: '',
      memo: '',
      start_date: initialDate,
      end_date: initialDate,
    })
  }
  dayEventsDialog.value?.close();
  itemDialog.value?.showModal()
}

const closeItemDialog = () => {
  itemDialog.value?.close()
}

const getStatusColorClass = (status: string | undefined) => {
  if (!status) return 'bg-transparent'
  return {
    '1': 'bg-gray-400',
    '2': 'bg-blue-500',
    '3': 'bg-green-500',
    '4': 'bg-yellow-500',
    '5': 'bg-blue-500',
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
        <button class="btn btn-sm btn-secondary" @click="openSelectPaperDialog">从题库选择</button>
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
        @click="openDayEventsDialog(day)"
        class="border rounded-lg p-2 flex flex-col cursor-pointer hover:bg-base-200"
        :class="{ 'bg-base-300': !day.isCurrentMonth, 'bg-base-100': day.isCurrentMonth }"
      >
        <span :class="{ 'text-gray-500': !day.isCurrentMonth }">{{ day.date.getDate() }}</span>
        <div class="flex-grow mt-1 space-y-1 overflow-y-auto">
          <div 
            v-for="event in day.events" 
            :key="event.id"
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

  <!-- Select Paper Dialog -->
  <dialog ref="selectPaperDialog" class="modal">
    <div class="modal-box w-11/12 max-w-3xl">
      <h3 class="font-bold text-lg">从题库选择试卷</h3>
      <div class="form-control w-full py-4">
        <input type="text" v-model="searchQuery" placeholder="搜索试卷标题..." class="input input-bordered w-full" />
      </div>
      <div class="overflow-y-auto h-96">
        <table class="table table-zebra w-full">
          <thead>
            <tr>
              <th>标题</th>
              <th>类型</th>
              <th>年级</th>
              <th>科目</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="paper in filteredPaperLibrary" :key="paper.id">
              <td>{{ paper.title }}</td>
              <td>{{ typeOptions.find(t => t.value === paper.type)?.label }}</td>
              <td>{{ gradeOptions.find(g => g.value === paper.grade)?.label }}</td>
              <td>{{ subjectOptions.find(s => s.value === paper.subject)?.label }}</td>
              <td>
                <button class="btn btn-sm btn-primary" @click="handleSelectPaper(paper)">选择</button>
              </td>
            </tr>
            <tr v-if="filteredPaperLibrary.length === 0">
              <td colspan="5" class="text-center">没有找到未安排的试卷</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="modal-action">
        <button class="btn" @click="closeSelectPaperDialog">关闭</button>
      </div>
    </div>
  </dialog>

  <!-- Day Events List Dialog -->
  <dialog ref="dayEventsDialog" class="modal">
    <div class="modal-box" v-if="selectedDay">
      <h3 class="font-bold text-lg">{{ selectedDay.date.toLocaleDateString('ja-JP') }} の予定</h3>
      <div class="py-4">
        <p v-if="selectedDay.events.length === 0" class="text-center text-gray-500">该日没有安排。</p>
        <ul v-else class="space-y-2">
          <li 
            v-for="event in selectedDay.events" 
            :key="event.id"
            @click="openItemDialog(event)"
            class="p-2 rounded-md flex items-center gap-2 cursor-pointer hover:bg-base-200"
          >
            <div class="w-3 h-3 rounded-full flex-shrink-0" :class="getStatusColorClass(event.status)"></div>
            <span class="flex-grow" :class="{ 'line-through': event.status === '3' }">{{ event.title }}</span>
            <span class="text-xs text-gray-400">{{ typeOptions.find(t => t.value === event.type)?.label }}</span>
          </li>
        </ul>
      </div>
      <div class="modal-action">
        <button class="btn btn-primary" @click="openItemDialog(undefined, selectedDay.date)">新增日程</button>
        <button class="btn" @click="closeDayEventsDialog">关闭</button>
      </div>
    </div>
  </dialog>

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

      <div class="grid grid-cols-2 gap-4">
        <div class="form-control w-full">
          <label class="label"><span class="label-text">开始日期</span></label>
          <input type="date" v-model="dialogData.start_date" class="input input-bordered w-full" />
        </div>
        <div class="form-control w-full">
          <label class="label"><span class="label-text">结束日期</span></label>
          <input type="date" v-model="dialogData.end_date" class="input input-bordered w-full" />
        </div>
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