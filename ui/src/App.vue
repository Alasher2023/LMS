<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavbarComponent from '@/components/NavbarComponent.vue'
</script>

<template>
  <NavbarComponent>
    <template #PageContent>
      <router-view></router-view>
    </template>
  </NavbarComponent>
</template>

<style scoped></style>
