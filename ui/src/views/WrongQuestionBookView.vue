<script setup lang="ts">
import { ref, reactive } from 'vue';
import type { Select } from '@/assets/types';
import SelectComponent from '@/components/SelectComponent.vue';
import ActivityChart from '@/components/ActivityChart.vue';

// Mock data for demonstration
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

const filter = reactive({
  subject: '0',
  tag: '',
  difficulty: '0',
});

const wrongQuestions = ref([
  { id: 1, subject: '数学', chapter: '第一章', type: '选择题', difficulty: '★★★', tags: ['代数', '方程'], review_at: '2025-09-15' },
  { id: 2, subject: '语文', chapter: '第三单元', type: '阅读理解', difficulty: '★★★★', tags: ['现代文'], review_at: '2025-09-20' },
]);

const chartData = ref([
    { date: '2025-08-25', count: 3 },
    { date: '2025-08-26', count: 5 },
    { date: '2025-08-27', count: 2 },
]);

const storagePath = ref('/var/data/wrong_questions');

const showAddModal = ref(false);

const newQuestion = reactive({
  subject: '',
  chapter: '',
  type: '',
  difficulty: '',
  tags: '',
  questionFile: null,
  answerFile: null,
  review_at: '',
});

const handleAddQuestion = () => {
  // Logic to save the new question
  showAddModal.value = false;
};

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
        <button class="btn btn-primary btn-sm">筛选</button>
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
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in wrongQuestions" :key="item.id">
            <td>{{ item.subject }}</td>
            <td>{{ item.chapter }}</td>
            <td>{{ item.type }}</td>
            <td>{{ item.difficulty }}</td>
            <td>
              <span v-for="tag in item.tags" :key="tag" class="badge badge-ghost mr-1">{{ tag }}</span>
            </td>
            <td>{{ item.review_at }}</td>
            <td class="flex gap-2">
              <button class="btn btn-xs btn-outline btn-info">查看</button>
              <button class="btn btn-xs btn-outline btn-warning">删除</button>
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
                <button class="btn btn-primary btn-sm mt-4">保存路径</button>
            </div>
        </div>
    </div>


    <!-- Add/Edit Modal -->
    <dialog class="modal" :class="{ 'modal-open': showAddModal }">
      <div class="modal-box w-11/12 max-w-3xl">
        <h3 class="font-bold text-lg">录入错题</h3>

        <div class="form-control">
          <label class="label"><span class="label-text">题目来源 (PDF)</span></label>
          <input type="file" class="file-input file-input-bordered w-full" />
          <p class="text-xs text-gray-500 mt-1">导入后可进行裁切</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div class="form-control">
                <label class="label"><span class="label-text">学科</span></label>
                <select-component v-model="newQuestion.subject" :options="subjectOptions.filter(o => o.value !== '0')" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">章节</span></label>
                <input type="text" v-model="newQuestion.chapter" class="input input-bordered" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">题型</span></label>
                <input type="text" v-model="newQuestion.type" class="input input-bordered" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text">难度</span></label>
                <select-component v-model="newQuestion.difficulty" :options="difficultyOptions.filter(o => o.value !== '0')" />
            </div>
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">标签 (逗号分隔)</span></label>
            <input type="text" v-model="newQuestion.tags" class="input input-bordered" />
        </div>

        <div class="form-control mt-4">
          <label class="label"><span class="label-text">解答/答案 (PDF)</span></label>
          <input type="file" class="file-input file-input-bordered w-full" />
        </div>

        <div class="form-control mt-4">
            <label class="label"><span class="label-text">复习提醒日期</span></label>
            <input type="date" v-model="newQuestion.review_at" class="input input-bordered" />
        </div>

        <div class="modal-action">
          <button class="btn btn-primary" @click="handleAddQuestion">保存</button>
          <button class="btn" @click="showAddModal = false">取消</button>
        </div>
      </div>
    </dialog>

  </div>
</template>
