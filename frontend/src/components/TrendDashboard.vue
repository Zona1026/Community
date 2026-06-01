<script setup lang="ts">
import type { Trend } from '../types/trend';
import TrendCard from './TrendCard.vue';

const props = defineProps<{
  trends: Trend[];
}>();

const hotTrends = props.trends.slice(0, 3);
const risingTrends = props.trends.filter((trend) => trend.momentum === 'rising');
const crossPlatformTrends = props.trends.filter((trend) => trend.platforms.length >= 3);
const coolingTrends = props.trends.filter((trend) => trend.momentum === 'cooling');
const editorPicks = props.trends.filter((trend) => trend.riskLevel !== 'high').slice(0, 2);
</script>

<template>
  <main class="container-fluid px-4 py-4">
    <section id="today-trends" class="mb-5">
      <div class="d-flex justify-content-between align-items-end mb-3">
        <div>
          <h2 class="h4 mb-1">今日熱門趨勢</h2>
          <p class="text-secondary mb-0">依 Heat Score 排序的高關注話題。</p>
        </div>
      </div>
      <div class="row g-3">
        <div v-for="trend in hotTrends" :key="trend.id" class="col-lg-4">
          <TrendCard :trend="trend" />
        </div>
      </div>
    </section>

    <section class="mb-5">
      <h2 class="h4 mb-3">快速升溫趨勢</h2>
      <div class="row g-3">
        <div v-for="trend in risingTrends" :key="trend.id" class="col-lg-4">
          <TrendCard :trend="trend" />
        </div>
      </div>
    </section>

    <section class="mb-5">
      <h2 class="h4 mb-3">跨平台爆紅趨勢</h2>
      <div class="row g-3">
        <div v-for="trend in crossPlatformTrends" :key="trend.id" class="col-lg-4">
          <TrendCard :trend="trend" />
        </div>
      </div>
    </section>

    <section class="mb-5">
      <h2 class="h4 mb-3">即將過氣 / 熱度下降趨勢</h2>
      <div class="row g-3">
        <div v-for="trend in coolingTrends" :key="trend.id" class="col-lg-4">
          <TrendCard :trend="trend" />
        </div>
      </div>
    </section>

    <section>
      <h2 class="h4 mb-3">編輯精選 / AI 推薦觀察</h2>
      <div class="row g-3">
        <div v-for="trend in editorPicks" :key="trend.id" class="col-lg-6">
          <TrendCard :trend="trend" />
        </div>
      </div>
    </section>
  </main>
</template>
