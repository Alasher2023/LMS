<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { Select, Paper } from '@/assets/types'
import SelectComponent from '@/components/SelectComponent.vue'
import api from '@/utils/api'

const api_path = '/paper/'

// Search filters
const subjectSelect = ref('2')
const gradeSelect = ref('1')
const authorSelect = ref('0')
const statusSelect = ref('0')
const typeSelect = ref('0')

// Static options for select components
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
]

// Computed maps for faster label lookup
const authorLabelMap = computed(() => Object.fromEntries(authorOptions.map(opt => [opt.value, opt.label])))
const subjectLabelMap = computed(() => Object.fromEntries(subjectOptions.map(opt => [opt.value, opt.label])))
const typeLabelMap = computed(() => Object.fromEntries(typeOptions.map(opt => [opt.value, opt.label])))
const statusLabelMap = computed(() => Object.fromEntries(statusOptions.map(opt => [opt.value, opt.label])))

const getAuthorClass = (author: string | undefined) => {
  if (!author) return ''
  return {
    '1': 'text-primary',
    '2': 'text-secondary',
    '3': 'text-info',
  }[author] || ''
}

const getStatusClass = (status: string | undefined) => {
  if (!status) return ''
  return {
    '1': 'text-error',
    '4': 'text-error',
    '2': 'text-primary',
    '5': 'text-primary',
    '3': 'text-info',
  }[status] || ''
}


const my_modal_dialog = ref<HTMLDialogElement | null>(null)

const dialogData = reactive<Partial<Paper>>({})

const handleOpenDailog = () => {
  const width = document.body.clientWidth + 'px'
  my_modal_dialog.value?.showModal()
  document.body.style.width = width
  document.body.style.overflow = 'hidden' // 阻止滚动
}

const handleCloseDialog = () => {
  document.body.style.width = ''
  document.body.style.overflow = '' // 恢复滚动
  my_modal_dialog.value?.close()
}

const handleCreatePaper = () => {
  Object.assign(dialogData, {
    id: null,
    subject: '',
    grade: '',
    type: '',
    status: '',
    author: '',
    title: '',
    path: '',
    memo: '',
  })
  handleOpenDailog()
}

const handleCommit = async () => {
  if (dialogData.id != null) {
    await api.put(api_path, dialogData)
    const index = tableData.value.findIndex(item => item.id === dialogData.id)
    if (index !== -1) {
      tableData.value[index] = { ...dialogData }
    }
  } else {
    await api.post(api_path, dialogData)
    await handleSearch()
  }
  handleCloseDialog()
}

const handleDownloadPaper = async (paper: Paper) => {
  try {
    const res = await api.get('/pdf', {
      params: { filename: paper.path },
      responseType: 'blob',
      headers: { 'Accept': 'application/pdf' }
    })
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${paper.title || 'paper'}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    error.value = err as string;
  }
}

const handleUpdate = (paper: Paper) => {
  Object.assign(dialogData, paper)
  handleOpenDailog()
}

const handleDelete = async (id: number | undefined) => {
  if (!confirm('确定删除吗？') || id === undefined) return
  try {
    const res = await api.delete(`${api_path}${id}/`)
    if (res.data.status == '200') {
      tableData.value = tableData.value.filter((paper) => paper.id !== id)
    }
  } catch (err) {
    error.value = err as string;
  }
}

const tableData = ref<Paper[]>([])
const nullText = ref('')
const error = ref<string | unknown>('')
const handleSearch = async () => {
  try {
    const res = await api.get(api_path, {
      params: {
        author: authorSelect.value,
        type: typeSelect.value,
        status: statusSelect.value,
        subject: subjectSelect.value,
        grade: gradeSelect.value,
        academic_only: true,
      },
    })
    tableData.value = res.data
    if (res.data?.length === 0) nullText.value = '無資料'
  } catch (err) {
    error.value = err
  }
}

</script>

<template>
  <div class="flex flex-col md:h-full">
    <div class="h-auto flex flex-col md:flex-row md:h-8 items-center justify-start gap-4">
      <select-component v-model="gradeSelect" :label="'年级'"
        :options="gradeOptions"></select-component>
      <select-component v-model="authorSelect" :label="'机构'"
        :options="authorOptions"></select-component>
      <select-component v-model="subjectSelect" :label="'科目'"
        :options="subjectOptions"></select-component>

    </div>
    <div class="h-auto flex flex-col mt-4 md:flex-row md:h-8 items-center justify-start gap-4">
      <select-component v-model="typeSelect" :label="'类型'"
        :options="typeOptions"></select-component>
      <select-component v-model="statusSelect"  :label="'状态'"
        :options="statusOptions"></select-component>

      <div class="btn btn-primary btn-wide md:btn-sm md:ml-auto md:w-24" @click="handleCreatePaper">添加</div>
      <div class="btn btn-info btn-wide md:btn-sm md:w-24" @click="handleSearch">查询</div>
    </div>
    <div class="divider"></div>

    <div v-if="tableData.length > 0" class="overflow-auto md:flex-1">
      <table class="table table-pin-rows table-zebra table-xs">
        <thead>
          <tr>
            <th class="w-auto md:min-w-64">标题</th>
            <th class="w-24 text-center hidden md:table-cell">机构</th>
            <th class="w-18 text-center hidden md:table-cell">科目</th>
            <th class="w-18 text-center hidden md:table-cell">类型</th>
            <th class="w-18 text-center hidden md:table-cell">状态</th>
            <!-- <th class="w-16 hidden md:table-cell">年级</th> -->
            <th class="w-56 text-center font-bold"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tableData" :key="item.id">
            <td>{{ item.title }}</td>
            <td class="hidden text-center md:table-cell">
              <p :class="getAuthorClass(item.author)">
                {{ item.author ? authorLabelMap[item.author] : '' }}
              </p>
            </td>
            <td class="hidden text-center md:table-cell">
              {{ item.subject ? subjectLabelMap[item.subject] : '' }}
            </td>
            <td class="hidden text-center md:table-cell">
              {{ item.type ? typeLabelMap[item.type] : '' }}
            </td>
            <td class="hidden text-center md:table-cell">
              <p :class="getStatusClass(item.status)">
                {{ item.status ? statusLabelMap[item.status] : '' }}
              </p>
            </td>
            <!-- <td class="hidden md:table-cell">
              {{ gradeOptions.find((x) => x.value == item.grade)?.label }}
            </td> -->
            <td>
              <div class="flex gap-4 justify-center">
                <div class="badge badge-primary md:cursor-pointer" @click="handleDownloadPaper(item)">
                  下载
                </div>
                <div class="badge badge-info md:cursor-pointer" @click="handleUpdate(item)">
                  编辑
                </div>
                <div class="badge badge-warning md:cursor-pointer" @click="handleDelete(item?.id)">
                  删除
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <h3 class="font-bold text-xl text-center">{{ nullText }}</h3>
    </div>
  </div>

  <dialog ref="my_modal_dialog" class="modal modal-bottom md:modal-middle">
    <div class="modal-box">
      <form @submit.prevent="handleCommit">
        <fieldset class="fieldset border-base-300 rounded-box w-full p-4">
          <legend class="fieldset-legend">Paper details</legend>

          <label class="label">机构</label>
          <select-component v-model="dialogData.author" :options="authorOptions.filter(opt => opt.value !== '0')" class="md:w-full"
            required></select-component>

          <label class="label">学科</label>
          <select-component v-model="dialogData.subject" :options="subjectOptions.filter(opt => opt.value !== '0')" class="md:w-full"
            required></select-component>

          <label class="label">年级</label>
          <select-component v-model="dialogData.grade" :options="gradeOptions" class="md:w-full"
            required></select-component>

          <label class="label">类型</label>
          <select-component v-model="dialogData.type" :options="typeOptions.filter(opt => opt.value !== '0')" class="md:w-full"
            required></select-component>

          <label class="label">状态</label>
          <select-component v-model="dialogData.status" :options="statusOptions.filter(opt => opt.value !== '0')" class="md:w-full"
            required></select-component>

          <label class="label">标题</label>
          <input type="text" v-model="dialogData.title" class="input md:w-full" placeholder="" required />

          <label class="label">网盘地址</label>
          <input type="text" v-model="dialogData.path" class="input md:w-full" placeholder="" />

          <label class="label">备注</label>
          <input type="text" v-model="dialogData.memo" class="input md:w-full" placeholder="" />
        </fieldset>
        <div class="modal-action">
          <button type="submit" class="btn btn-primary">提交</button>
          <div class="btn btn-neutral" @click="handleCloseDialog">关闭</div>
        </div>
      </form>
    </div>
  </dialog>

  
</template>
