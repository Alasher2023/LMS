<template>
  <div class="pdf-generator-view p-4">
    <h1 class="text-2xl font-bold mb-4">PDF 生成器</h1>
    <p class="mb-6">请选择参数，然后点击“生成PDF”来创建练习题。</p>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Problem Type Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="题目类型" :options="problemTypes" v-model="selectedProblemType" />
      </div>

      <!-- Operator Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="运算符" :options="operatorOptions" v-model="selectedOperators" />
      </div>

      <!-- Digit Mode Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="数值位数" :options="digitModeOptions" v-model="selectedDigitMode" />
      </div>

      <!-- Max Number Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="最大数值" :options="maxNumberOptions" v-model="selectedMaxNumber" />
      </div>

      <!-- Number of Problems Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="题目数量" :options="numProblemsOptions" v-model="selectedNumProblems" />
      </div>

      <!-- Number of Operands Dropdown -->
      <div class="form-control w-full max-w-xs">
        <SelectComponent label="运算数数量" :options="numOperandsOptions" v-model="selectedNumOperands" />
      </div>

      <!-- Operation Mode Dropdown -->
      <div v-if="parseInt(selectedNumOperands, 10) > 2 && selectedOperators === 'add_subtract'" class="form-control w-full max-w-xs">
        <SelectComponent label="运算模式" :options="opModeOptions" v-model="selectedOpMode" />
      </div>
    </div>

    <div class="mt-6">
      <button class="btn btn-primary" @click="generatePdf" :disabled="!selectedProblemType">
        生成 PDF
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import SelectComponent from '@/components/SelectComponent.vue';
import type { Select } from '@/assets/types';
import api from '@/utils/api';

// --- Refs for user selections ---
const selectedProblemType = ref<string>('simple_calculation');
const selectedOperators = ref<string>('add_subtract');
const selectedMaxNumber = ref<string>('50');
const selectedNumProblems = ref<string>('50');
const selectedNumOperands = ref<string>('2');
const selectedOpMode = ref<string>('mixed');
const selectedDigitMode = ref<string>('unlimited');

// --- Options for dropdowns ---
const problemTypes = ref<Select[]>([
  { label: '常规计算 (例如: 10 + 1)', value: 'simple_calculation' },
  { label: '带未知数的计算 (例如: 10 + ▢ = 15)', value: 'find_missing_number' },
]);

const operatorOptions = ref<Select[]>([
    { label: '加减法', value: 'add_subtract' },
    { label: '乘除法', value: 'multiply_divide' },
    { label: '四则运算', value: 'all' },
]);

const digitModeOptions = ref<Select[]>([
  { label: '无限制', value: 'unlimited' },
  { label: '一位数 (1-9)', value: '1-digit' },
  { label: '两位数 (10-99)', value: '2-digits' },
  { label: '三位数 (100-999)', value: '3-digits' },
]);

const maxNumberOptions = ref<Select[]>([
  { label: '20以内', value: '20' },
  { label: '50以内', value: '50' },
  { label: '200以内', value: '200' },
  { label: '1000以内', value: '1000' }
]);

const numProblemsOptions = ref<Select[]>([
    { label: '20题', value: '20' },
    { label: '50题', value: '50' },
    { label: '100题', value: '100' },
]);

const numOperandsOptions = ref<Select[]>([
  { label: '2个数字', value: '2' },
  { label: '3个数字', value: '3' },
  { label: '4个数字', value: '4' },
]);

const opModeOptions = ref<Select[]>([
    { label: '混合运算', value: 'mixed' },
    { label: '连续运算', value: 'sequential' },
]);

const isMaxNumberDisabled = computed(() => selectedDigitMode.value !== 'unlimited');

// --- PDF Generation Method ---
const generatePdf = async () => {
  try {
    const params: any = {
      problem_type: selectedProblemType.value,
      num_operands: parseInt(selectedNumOperands.value, 10),
      operators: selectedOperators.value,
      num_problems: parseInt(selectedNumProblems.value, 10),
      op_mode: selectedOpMode.value,
    };

    // Set min/max number based on digit mode
    switch (selectedDigitMode.value) {
      case '1-digit':
        params.min_number = 1;
        params.max_number = 9;
        break;
      case '2-digits':
        params.min_number = 10;
        params.max_number = 99;
        break;
      case '3-digits':
        params.min_number = 100;
        params.max_number = 999;
        break;
      default: // unlimited
        params.min_number = parseInt(selectedMaxNumber.value) >= 100 ? 10 : 1;
        params.max_number = parseInt(selectedMaxNumber.value, 10);
        break;
    }

    const response = await api.get('/api/generate-pdf', { params, responseType: 'blob' });

    // Create a URL for the blob and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `math_problems.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('生成PDF失败，请查看控制台获取更多信息。');
  }
};
</script>

<style scoped>
.pdf-generator-view {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
