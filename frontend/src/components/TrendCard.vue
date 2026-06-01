<script setup lang="ts">
import type { Trend } from '../types/trend';

defineProps<{
  trend: Trend;
}>();

const lifecycleLabel: Record<string, string> = {
  emerging: '萌芽',
  growing: '成長',
  viral: '爆紅',
  declining: '衰退',
  expired: '過氣'
};

const riskClass: Record<string, string> = {
  low: 'text-bg-success',
  medium: 'text-bg-warning',
  high: 'text-bg-danger'
};
</script>

<template>
  <article class="card h-100 border-0 shadow-sm">
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-start gap-3 mb-3">
        <div>
          <h3 class="h5 mb-2">{{ trend.topicName }}</h3>
          <p class="text-secondary mb-0">{{ trend.summary }}</p>
        </div>
        <span class="badge text-bg-primary fs-6">{{ trend.heatScore }}</span>
      </div>

      <div class="d-flex flex-wrap gap-2 mb-3">
        <span class="badge text-bg-light border">Heat {{ trend.heatScore }}</span>
        <span class="badge text-bg-light border">
          Growth {{ trend.growthRate > 0 ? '+' : '' }}{{ trend.growthRate }}%
        </span>
        <span class="badge text-bg-dark">{{ lifecycleLabel[trend.lifecycleStage] }}</span>
        <span class="badge" :class="riskClass[trend.riskLevel]">{{ trend.riskNote }}</span>
      </div>

      <div class="mb-3">
        <div class="small text-secondary mb-1">主要來源平台</div>
        <div class="d-flex flex-wrap gap-2">
          <span v-for="platform in trend.platforms" :key="platform" class="badge text-bg-secondary">
            {{ platform }}
          </span>
        </div>
      </div>

      <div class="mb-3">
        <div class="small text-secondary mb-1">相關關鍵字</div>
        <div class="d-flex flex-wrap gap-2">
          <span v-for="keyword in trend.keywords" :key="keyword" class="badge text-bg-light border">
            {{ keyword }}
          </span>
        </div>
      </div>

      <div class="mb-4">
        <div class="small text-secondary mb-1">可切入產業</div>
        <div class="small">{{ trend.suitableIndustries.join('、') }}</div>
      </div>

      <div class="mt-auto d-flex gap-2">
        <RouterLink class="btn btn-outline-primary flex-fill" :to="`/trends/${trend.id}`">
          查看趨勢詳情
        </RouterLink>
        <RouterLink class="btn btn-primary flex-fill" :to="`/trends/${trend.id}/ideas`">
          產生內容靈感
        </RouterLink>
      </div>
    </div>
  </article>
</template>
