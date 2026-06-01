<script setup lang="ts">
import AppNavigation from '../components/AppNavigation.vue';
import TrendCard from '../components/TrendCard.vue';
import { mockTrends } from '../data/mockTrends';
</script>

<template>
  <AppNavigation />
  <main class="container-fluid px-4 py-4">
    <div class="mb-4">
      <span class="badge text-bg-dark mb-2">Explore</span>
      <h1 class="h2">趨勢探索</h1>
      <p class="text-secondary">依平台、生命週期、風險與關鍵字探索值得觀察的趨勢。</p>
    </div>

    <div class="row g-3">
      <div v-for="trend in mockTrends" :key="trend.id" class="col-lg-4">
        <TrendCard :trend="trend" />
      </div>
    </div>
  </main>
</template>
