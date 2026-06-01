<script setup lang="ts">
import { computed, ref } from 'vue';
import AppNavigation from '../components/AppNavigation.vue';
import TrendCard from '../components/TrendCard.vue';
import { mockTrends } from '../data/mockTrends';

const industry = ref('');

const matchedTrends = computed(() => {
  if (!industry.value.trim()) {
    return mockTrends;
  }

  return mockTrends.filter((trend) =>
    trend.suitableIndustries.some((item) => item.includes(industry.value.trim()))
  );
});
</script>

<template>
  <AppNavigation />
  <main class="container-fluid px-4 py-4">
    <div class="mb-4">
      <span class="badge text-bg-dark mb-2">Industry Inspiration</span>
      <h1 class="h2">輸入產業找靈感</h1>
      <p class="text-secondary">找出適合你的產業觀察、切入或延伸的趨勢。</p>
    </div>

    <div class="border rounded-3 p-4 mb-4">
      <label class="form-label">我的產業</label>
      <input v-model="industry" class="form-control" placeholder="例如：餐飲業、科技業、房地產" />
    </div>

    <div class="row g-3">
      <div v-for="trend in matchedTrends" :key="trend.id" class="col-lg-4">
        <TrendCard :trend="trend" />
      </div>
    </div>
  </main>
</template>
