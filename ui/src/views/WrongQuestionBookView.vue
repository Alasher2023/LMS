<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import type { Select } from '@/assets/types';
import SelectComponent from '@/components/SelectComponent.vue';
import QuestionTypePieChart from '@/components/QuestionTypePieChart.vue';
import api from '@/utils/api';

// --- Interfaces ---
interface WrongQuestion {
  id: number;
  subject: string;
  chapter: string | null;
  question_type: string | null;
  difficulty: string | null;
  tags: string | null;
  question_path: string | null;
  answer_path: string | null;
  review_at: string | null;
  created_at: string;
  updated_at: string;
}

interface PieChartData {
  name: string;
  value: number;
}

// --- Template Refs ---
const questionFileInput = ref<HTMLInputElement | null>(null);
const answerFileInput = ref<HTMLInputElement | null>(null);

// --- Mock data for demonstration ---
const subjectOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '算数' },
  { value: '2', label: '国语' },
  // { value: '3', label: '英语' },
];

const difficultyOptions: Select[] = [
  { value: '0', label: '全部' },
  { value: '1', label: '★' },
  { value: '2', label: '★★' },
  { value: '3', label: '★★★' },
  { value: '4', label: '★★★★' },
  { value: '5', label: '★★★★★' },
];

// --- Reactive State ---
const filter = reactive({
  subject: '0',
  tag: '',
  difficulty: '0',
});

const wrongQuestions = ref<WrongQuestion[]>([]);
const selectedQuestions = ref<number[]>([]);
const pieChartData = ref<PieChartData[]>([]);
const chartSubjectFilter = ref('0');

const storagePath = ref('');

const showAddModal = ref(false);
const showEditModal = ref(false);
const editingQuestion = ref<WrongQuestion | null>(null);


const newQuestion = reactive({
  subject: '',
  chapter: '',
  question_type: '',
  difficulty: '',
  tags: '',
  review_at: '',
});

// ---
const isAllSelected = computed(() => {
  return wrongQuestions.value.length > 0 && selectedQuestions.value.length === wrongQuestions.value.length;
});

// --- Functions ---
const handleFilter = async () => {
  try {
    const res = await api.get('/wrong_question_book/', {
      params: filter,
    });
    wrongQuestions.value = res.data;
  } catch (err) {
    console.error('Failed to fetch wrong questions:', err);
  }
};

const fetchPieChartData = async () => {
  try {
    const res = await api.get('/wrong_question_book/stats', {
      params: {
        subject: chartSubjectFilter.value,
      },
    });
    pieChartData.value = res.data;
  } catch (err) {
    console.error('Failed to fetch chart data:', err);
  }
};

const loadStoragePath = async () => {
  try {
    const res = await api.get('/settings/wrong_question_path');
    if (res.data.path) {
      storagePath.value = res.data.path;
    }
  } catch (err) {
    console.error('Failed to load storage path:', err);
  }
};

const saveStoragePath = async () => {
  try {
    await api.post('/settings/wrong_question_path', {
      wrong_question_storage_path: storagePath.value,
    });
    alert('路径已保存!');
  } catch (err) {
    console.error('Failed to save storage path:', err);
    alert('路径保存失败!');
  }
};

const openEditModal = (question: WrongQuestion) => {
  const subjectOption = subjectOptions.find(opt => opt.label === question.subject);
  const difficultyValue = difficultyOptions.find(opt => opt.label === question.difficulty)?.value || question.difficulty;

  editingQuestion.value = JSON.parse(JSON.stringify(question)); // Deep copy to avoid modifying original object

  if (editingQuestion.value) {
    editingQuestion.value.subject = subjectOption ? subjectOption.value : '';
    editingQuestion.value.difficulty = difficultyValue;
    if (editingQuestion.value.review_at) {
      editingQuestion.value.review_at = editingQuestion.value.review_at.split('T')[0];
    }
  }
  
  showEditModal.value = true;
};

const handleUpdateQuestion = async () => {
  if (!editingQuestion.value) return;

  const { id, subject, chapter, question_type, difficulty, tags, review_at } = editingQuestion.value;

  const payload = {
    subject,
    chapter,
    question_type,
    difficulty,
    tags,
    review_at,
  };

  try {
    await api.put(`/wrong_question_book/${id}`, payload);
    showEditModal.value = false;
    handleFilter(); // Refresh the list
    fetchPieChartData(); // Refresh chart
  } catch (err) {
    console.error('Failed to update question:', err);
    alert('更新失败!');
  }
};

const handleAddQuestion = async () => {
  const formData = new FormData();

  Object.entries(newQuestion).forEach(([key, value]) => {
    if (value) {
      formData.append(key, value as string);
    }
  });

  if (questionFileInput.value?.files?.[0]) {
    formData.append('question_file', questionFileInput.value.files[0]);
  }
  if (answerFileInput.value?.files?.[0]) {
    formData.append('answer_file', answerFileInput.value.files[0]);
  }

  try {
    await api.post('/wrong_question_book', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    showAddModal.value = false;
    handleFilter(); // Refresh the list
    fetchPieChartData(); // Refresh chart
  } catch (err) {
    console.error('Failed to add new question:', err);
    alert('添加失败!');
  }
};

const handleDelete = async (id: number) => {
  if (!confirm('确定要删除这个错题吗?')) {
    return;
  }
  try {
    await api.delete(`/wrong_question_book/${id}`);
    wrongQuestions.value = wrongQuestions.value.filter(q => q.id !== id);
    fetchPieChartData(); // Refresh chart
  } catch (err) {
    console.error('Failed to delete question:', err);
    alert('删除失败!');
  }
};

const handleView = (questionId: number, type: 'question' | 'answer') => {
  const url = `${api.defaults.baseURL}/wrong_question_book/file/${questionId}?type=${type}`;
  window.open(url, '_blank');
};

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedQuestions.value = [];
  } else {
    selectedQuestions.value = wrongQuestions.value.map(q => q.id);
  }
};

const handleGeneratePdf = async () => {
  if (selectedQuestions.value.length === 0) {
    alert('请先选择要生成的错题!');
    return;
  }
  try {
    const res = await api.post('/wrong_question_book/generate_pdf', {
      question_ids: selectedQuestions.value,
    }, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'wrong_question_book.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Failed to generate PDF:', err);
    alert('PDF生成失败!');
  }
};

// --- Lifecycle Hooks ---
onMounted(() => {
  handleFilter();
  loadStoragePath();
  fetchPieChartData();
});

watch(chartSubjectFilter, fetchPieChartData);
watch(() => filter.subject, handleFilter);
watch(() => filter.difficulty, handleFilter);

</script>

<template>
  <div class="p-4 md:p-6">
    <h1 class="text-2xl font-bold mb-4">错题本</h1>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4 mb-4 p-4 bg-base-200 rounded-lg">
      <div class="form-control">
        <label class="label">
          <span class="label-text">学科</span>
        </label>
        <select-component v-model="filter.subject" :options="subjectOptions" />
      </div>
      <div class="form-control">
        <label class="label">
          <span class="label-text">标签</span>
        </label>
        <input type="text" v-model="filter.tag" placeholder="输入标签..." class="input input-bordered input-sm" />
      </div>
      <div class="form-control">
        <label class="label">
          <span class="label-text">难度</span>
        </label>
        <select-component v-model="filter.difficulty" :options="difficultyOptions" />
      </div>
      <div class="form-control self-end">
        <button class="btn btn-primary btn-sm" @click="handleFilter">筛选</button>
      </div>
    </div>

    <!-- Actions -->
    <div class="mb-4 flex justify-between items-center">
      <div>
        <button class="btn btn-primary btn-sm" @click="showAddModal = true">录入新错题</button>
        <button class="btn btn-secondary btn-sm ml-2" @click="handleGeneratePdf" :disabled="selectedQuestions.length === 0">生成错题本PDF</button>
      </div>
      <div>
        <button class="btn btn-ghost btn-sm" @click="toggleSelectAll">{{ isAllSelected ? '全部取消' : '全部选择' }}</button>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th><input type="checkbox" class="checkbox checkbox-sm" :checked="isAllSelected" @change="toggleSelectAll" /></th>
            <th>学科</th>
            <th>章节</th>
            <th>题型</th>
            <th>难度</th>
            <th>标签</th>
            <th>复习日期</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in wrongQuestions" :key="item.id">
            <td><input type="checkbox" class="checkbox checkbox-sm" :value="item.id" v-model="selectedQuestions" /></td>
            <td>{{ item.subject }}</td>
            <td>{{ item.chapter }}</td>
            <td>{{ item.question_type }}</td>
            <td>{{ item.difficulty }}</td>
            <td>
              <span v-for="tag in item.tags?.split(',').filter(t => t)" :key="tag" class="badge badge-ghost mr-1">{{ tag }}</span>
            </td>
            <td>{{ item.review_at }}</td>
            <td class="flex gap-2">
              <button class="btn btn-xs btn-outline btn-info" @click="handleView(item.id, 'question')" :disabled="!item.question_path">查看题目</button>
              <button class="btn btn-xs btn-outline btn-success" @click="handleView(item.id, 'answer')" :disabled="!item.answer_path">查看答案</button>
              <button class="btn btn-xs btn-outline btn-accent" @click="openEditModal(item)">编辑</button>
              <button class="btn btn-xs btn-outline btn-warning" @click="handleDelete(item.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Stats and Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <!-- Stats -->
        <div>
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold">统计分析</h2>
              <div class="form-control">
                <select-component v-model="chartSubjectFilter" :options="subjectOptions" />
              </div>
            </div>
            <div class="p-4 bg-base-200 rounded-lg h-64">
                <QuestionTypePieChart v-if="pieChartData.length" :pie-chart-data="pieChartData" />
                <div v-else class="flex items-center justify-center h-full">
                  <p>没有数据显示</p>
                </div>
            </div>
        </div>
        <!-- Settings -->
        <div>
            <h2 class="text-xl font-bold mb-4">设置</h2>
            <div class="p-4 bg-base-200 rounded-lg">
                <div class="form-control">
                    <label class="label">
                    <span class="label-text">错题存储路径</span>
                    </label>
                    <input type="text" v-model="storagePath" class="input input-bordered input-sm" />
                </div>
                <button class="btn btn-primary btn-sm mt-4" @click="saveStoragePath">保存路径</button>
            </div>
        </div>
    </div>


    <!-- Add/Edit Modal -->
    <dialog class="modal" :class="{ 'modal-open': showAddModal }">
      <div class="modal-box w-11/12 max-w-3xl">
        <h3 class="font-bold text-lg">录入错题</h3>

        <div class="form-control">
          <label class="label"><span class="label-text">题目来源 (PDF)</span></label>
          <input type="file" ref="questionFileInput" class="file-input file-input-bordered w-full file-input-sm" />
          <p class="text-xs text-gray-500 mt-1">导入后可进行裁切</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div class="form-control">
                <label class="label"><span class="label-text">学科</span></label>
                <select-component v-model="newQuestion.subject" :options="subjectOptions.filter(o => o.value !== '0')" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">章节</span></label>
                <input type="text" v-model="newQuestion.chapter" class="input input-bordered input-sm" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">题型</span></label>
                <input type="text" v-model="newQuestion.question_type" class="input input-bordered input-sm" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">难度</span></label>
                <select-component v-model="newQuestion.difficulty" :options="difficultyOptions.filter(o => o.value !== '0')" />
            </div>
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">标签 (逗号分隔)</span></label>
            <input type="text" v-model="newQuestion.tags" class="input input-bordered input-sm" />
        </div>

        <div class="form-control mt-4">
          <label class="label"><span class="label-text">解答/答案 (PDF)</span></label>
          <input type="file" ref="answerFileInput" class="file-input file-input-bordered w-full file-input-sm" />
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">复习提醒日期</span></label>
            <input type="date" v-model="newQuestion.review_at" class="input input-bordered input-sm" />
        </div>

        <div class="modal-action">
          <button class="btn btn-primary" @click="handleAddQuestion">保存</button>
          <button class="btn" @click="showAddModal = false">取消</button>
        </div>
      </div>
    </dialog>
    
    <!-- Edit Modal -->
    <dialog class="modal" :class="{ 'modal-open': showEditModal }">
      <div class="modal-box w-11/12 max-w-3xl" v-if="editingQuestion">
        <h3 class="font-bold text-lg">编辑错题</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div class="form-control">
                <label class="label"><span class="label-text">学科</span></label>
                <select-component v-model="editingQuestion.subject" :options="subjectOptions.filter(o => o.value !== '0')" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">章节</span></label>
                <input type="text" v-model="editingQuestion.chapter" class="input input-bordered input-sm" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">题型</span></label>
                <input type="text" v-model="editingQuestion.question_type" class="input input-bordered input-sm" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">难度</span></label>
                <select-component v-model="editingQuestion.difficulty" :options="difficultyOptions.filter(o => o.value !== '0')" />
            </div>
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">标签 (逗号分隔)</span></label>
            <input type="text" v-model="editingQuestion.tags" class="input input-bordered input-sm" />
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">复习提醒日期</span></label>
            <input type="date" v-model="editingQuestion.review_at" class="input input-bordered input-sm" />
        </div>

        <div class="modal-action">
          <button class="btn btn-primary" @click="handleUpdateQuestion">保存</button>
          <button class="btn" @click="showEditModal = false">取消</button>
        </div>
      </div>
    </dialog>

  </div>
</template>