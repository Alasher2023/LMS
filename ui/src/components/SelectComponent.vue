<script setup lang="ts">
import { defineModel } from 'vue'
import type { Select } from '@/assets/types'

const props = defineProps<{
  label?: string
  options: Select[]
}>()

const modelValue = defineModel<string | undefined>()
</script>

<template>
  <select v-if="props.label === undefined" class="select" v-model="modelValue">
    <option v-for="option in props.options" :key="option.value" :value="option.value">
      {{ option.label }}
    </option>
  </select>
  <label v-else class="select">
    <span class="label">{{ props.label }}</span>
    <select v-model="modelValue">
      <option v-for="option in props.options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
