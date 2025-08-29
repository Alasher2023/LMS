<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import type { Select } from '@/assets/types';
import SelectComponent from '@/components/SelectComponent.vue';
import ActivityChart from '@/components/ActivityChart.vue';
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

const chartData = ref([
    { date: '2025-08-25', count: 3 },
    { date: '2025-08-26', count: 5 },
    { date: '2025-08-27', count: 2 },
]);

const storagePath = ref('');

const showAddModal = ref(false);

const newQuestion = reactive({
  subject: '',
  chapter: '',
  question_type: '',
  difficulty: '',
  tags: '',
  review_at: '',
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
    await api.post('/wrong_question_book/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    showAddModal.value = false;
    handleFilter(); // Refresh the list
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
  } catch (err) {
    console.error('Failed to delete question:', err);
    alert('删除失败!');
  }
};

const handleView = (questionId: number, type: 'question' | 'answer') => {
  const url = `${api.defaults.baseURL}/wrong_question_book/file/${questionId}?type=${type}`;
  window.open(url, '_blank');
};

// --- Lifecycle Hooks ---
onMounted(() => {
  handleFilter();
  loadStoragePath();
});

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
    <div class="mb-4 flex justify-between">
      <button class="btn btn-primary btn-sm" @click="showAddModal = true">录入新错题</button>
      <button class="btn btn-secondary btn-sm">生成错题本PDF</button>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
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
            <h2 class="text-xl font-bold mb-4">统计分析</h2>
            <div class="p-4 bg-base-200 rounded-lg h-64">
                <ActivityChart v-if="chartData.length" :activity-data="chartData" />
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

  </div>
</template>
