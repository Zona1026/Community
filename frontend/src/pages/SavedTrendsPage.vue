<script setup lang="ts">
import AppNavigation from '../components/AppNavigation.vue';
</script>

<template>
  <AppNavigation />
  <main class="container-fluid px-4 py-4">
    <div class="mb-4">
      <span class="badge text-bg-dark mb-2">Saved</span>
      <h1 class="h2">收藏</h1>
      <p class="text-secondary">收藏想持續觀察的趨勢、報告與靈感。</p>
    </div>

    <div class="border rounded-3 p-4 text-secondary">
      目前尚無收藏項目。
    </div>
  </main>
</template>
