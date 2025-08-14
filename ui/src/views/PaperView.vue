<script setup lang="ts">
import { ref } from 'vue'
import type { Select, Paper } from '@/assets/types'
import SelectComponent from '@/components/SelectComponent.vue'
import api from '@/utils/api'

const api_path = '/paper/'
const subjectSelect = ref('1')
const subjectOptions = ref<Select[]>([
  {
    value: '1',
    label: '国语',
  },
  {
    value: '2',
    label: '算数',
  },
])
const gradeSelect = ref('1')
const gradeOptions = ref<Select[]>([
  {
    value: '1',
    label: '一年级',
  },
  {
    value: '2',
    label: '二年级',
  },
])

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
  dialog_id_input.value = null
  dialog_subject_select.value = ''
  dialog_grade_select.value = ''
  dialog_title_input.value = ''
  dialog_path_input.value = ''
  dialog_memo_input.value = ''
  handleOpenDailog()
}

const handleCommit = () => {
  const paper: Paper = {
    id: dialog_id_input.value,
    subject: dialog_subject_select.value,
    grade: dialog_grade_select.value,
    title: dialog_title_input.value,
    path: dialog_path_input.value,
    memo: dialog_memo_input.value,
  }

  if (paper.id != null) {
    api.put(api_path, paper).then(() => {
      tableData.value = tableData.value.map((item) => {
        if (item.id === paper.id) {
          return paper
        }
        return item
      })
      handleCloseDialog()
    })
  } else {
    api
      .post(api_path, paper)
      .then(() => {
        handleCloseDialog()
        handleSearch()
      })
      .catch((err) => {
        console.log(err)
      })
  }
}

const handleOpenPaper = (paper: Paper) => {
  if (paper.path) {
    window.open(paper.path, '_blank')
  }
}

const handleUpdate = (paper: Paper) => {
  dialog_id_input.value = paper.id
  dialog_subject_select.value = paper.subject
  dialog_grade_select.value = paper.grade
  dialog_title_input.value = paper.title
  dialog_path_input.value = paper.path
  dialog_memo_input.value = paper.memo!
  handleOpenDailog()
}

const handleDelete = async (id: number | undefined) => {
  if (!confirm('确定删除吗？')) return
  if (id === undefined) return
  await api.delete(`${api_path}${id}/`).then((res) => {
    if (res.data.status == '200') {
      tableData.value = tableData.value.filter((paper) => paper.id !== id)
    }
  })
}

const tableData = ref<Paper[]>([])
const error = ref('')
const handleSearch = async () => {
  await api
    .get(api_path, {
      params: {
        subject: subjectSelect.value,
        grade: gradeSelect.value,
      },
    })
    .then((res) => (tableData.value = res.data))
    .catch((err) => (error.value = err))
}

const my_modal_dialog = ref<HTMLDialogElement | null>(null)
const dialog_id_input = ref()
const dialog_grade_select = ref('')
const dialog_subject_select = ref('')
const dialog_title_input = ref('')
const dialog_path_input = ref('')
const dialog_memo_input = ref('')
</script>

<template>
  <div class="flex flex-col">
    <div class="h-auto flex flex-col md:flex-row md:h-16 items-center justify-start gap-4">
      <select-component
        v-model="subjectSelect"
        class="md:border-none md:shadow-none"
        :label="'学科'"
        :options="subjectOptions"
      ></select-component>
      <select-component
        v-model="gradeSelect"
        class="md:border-none md:shadow-none"
        :label="'年级'"
        :options="gradeOptions"
      ></select-component>
      <div class="btn btn-primary btn-wide md:ml-auto md:w-24" @click="handleCreatePaper">添加</div>
      <div class="btn btn-info btn-wide md:w-24" @click="handleSearch">查询</div>
    </div>
    <div class="divider"></div>

    <div v-if="tableData.length > 0" class="overflow-x-auto">
      <table class="table table-zebra table-xs">
        <thead>
          <tr>
            <th class="w-auto md:min-w-64">试卷名</th>
            <th class="w-16 hidden md:table-cell">科目</th>
            <th class="w-16 hidden md:table-cell">年级</th>
            <th class="w-56 text-center font-bold"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tableData" :key="item.id">
            <td>{{ item.title }}</td>
            <td class="hidden md:table-cell">
              {{ subjectOptions.find((x) => x.value == item.subject)?.label }}
            </td>
            <td class="hidden md:table-cell">
              {{ gradeOptions.find((x) => x.value == item.grade)?.label }}
            </td>
            <td>
              <div class="flex gap-4 justify-center">
                <div class="badge badge-primary md:cursor-pointer" @click="handleOpenPaper(item)">
                  查看
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
      <h3 class="font-bold text-xl text-center">无查询结果</h3>
    </div>
  </div>

  <dialog ref="my_modal_dialog" class="modal modal-bottom md:modal-middle">
    <div class="modal-box">
      <fieldset class="fieldset border-base-300 rounded-box w-full p-4">
        <legend class="fieldset-legend">Paper details</legend>

        <label class="label">学科</label>
        <select-component
          v-model="dialog_subject_select"
          :options="subjectOptions"
          class="md:w-full"
          aria-required="true"
        ></select-component>

        <label class="label">年级</label>
        <select-component
          v-model="dialog_grade_select"
          :options="gradeOptions"
          class="md:w-full"
          aria-required="true"
        ></select-component>

        <label class="label">书名</label>
        <input type="text" v-model="dialog_title_input" class="input md:w-full" placeholder="" />

        <label class="label">网盘地址</label>
        <input type="text" v-model="dialog_path_input" class="input md:w-full" placeholder="" />

        <label class="label">备注</label>
        <input type="text" v-model="dialog_memo_input" class="input md:w-full" placeholder="" />
      </fieldset>
      <div class="modal-action">
        <div class="btn btn-primary" @click="handleCommit">登录</div>
        <div class="btn btn-neutral" @click="handleCloseDialog">关闭</div>
      </div>
    </div>
  </dialog>
</template>
