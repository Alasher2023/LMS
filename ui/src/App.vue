<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavbarComponent from '@/components/NavbarComponent.vue'
import { useLoadingStore } from '@/stores/loading'

const loadingStore = useLoadingStore()
</script>

<template>
  <div v-if="loadingStore.loading" class="fixed inset-0 z-50 flex items-center justify-center">
    <span class="loading loading-dots loading-lg"></span>
  </div>
  <NavbarComponent>
    <template #PageContent>
      <router-view></router-view>
    </template>
  </NavbarComponent>
</template>

<style scoped></style>
