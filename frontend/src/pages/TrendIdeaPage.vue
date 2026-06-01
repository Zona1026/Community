<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppNavigation from '../components/AppNavigation.vue';
import InspirationPanel from '../components/InspirationPanel.vue';
import TrendDetailPanel from '../components/TrendDetailPanel.vue';
import { mockTrends } from '../data/mockTrends';

const route = useRoute();

const trend = computed(() => mockTrends.find((item) => item.id === route.params.id) ?? mockTrends[0]);
</script>

<template>
  <AppNavigation />
  <TrendDetailPanel :trend="trend" />
  <InspirationPanel :trend="trend" />
</template>
