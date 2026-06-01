<script setup lang="ts">
import AppNavigation from '../components/AppNavigation.vue';
import HeroTrendRadar from '../components/HeroTrendRadar.vue';
import TrendDashboard from '../components/TrendDashboard.vue';
import { mockTrends } from '../data/mockTrends';
</script>

<template>
  <AppNavigation />
  <HeroTrendRadar />
  <TrendDashboard :trends="mockTrends" />
</template>
