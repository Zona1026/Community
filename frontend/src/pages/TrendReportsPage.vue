<script setup lang="ts">
import AppNavigation from '../components/AppNavigation.vue';
import { mockTrends } from '../data/mockTrends';
</script>

<template>
  <AppNavigation />
  <main class="container-fluid px-4 py-4">
    <div class="mb-4">
      <span class="badge text-bg-dark mb-2">Reports</span>
      <h1 class="h2">趨勢報告</h1>
      <p class="text-secondary">彙整趨勢摘要、跨平台訊號、生命週期與觀察建議。</p>
    </div>

    <div class="list-group">
      <RouterLink
        v-for="trend in mockTrends"
        :key="trend.id"
        class="list-group-item list-group-item-action"
        :to="`/trends/${trend.id}`"
      >
        <div class="d-flex justify-content-between">
          <strong>{{ trend.topicName }}</strong>
          <span>Heat {{ trend.heatScore }}</span>
        </div>
        <div class="text-secondary">{{ trend.summary }}</div>
      </RouterLink>
    </div>
  </main>
</template>
