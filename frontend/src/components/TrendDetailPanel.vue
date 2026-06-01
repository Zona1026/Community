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
</script>

<template>
  <section class="container-fluid px-4 py-4">
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="mb-4">
          <span class="badge text-bg-dark mb-2">Trend Detail</span>
          <h1 class="h2 mb-2">{{ trend.topicName }}</h1>
          <p class="lead text-secondary">{{ trend.summary }}</p>
        </div>

        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">為什麼正在紅</h2>
          <p class="mb-0">{{ trend.whyTrending }}</p>
        </div>

        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">代表內容 / 代表貼文</h2>
          <div v-for="content in trend.representativeContents" :key="content.id" class="border-top pt-3 mt-3">
            <div class="d-flex justify-content-between gap-3">
              <h3 class="h6 mb-1">{{ content.title }}</h3>
              <span class="badge text-bg-secondary">{{ content.platformName }}</span>
            </div>
            <p class="text-secondary mb-2">{{ content.body }}</p>
            <div class="small text-secondary">
              Likes {{ content.likes }} · Comments {{ content.comments }} · Shares {{ content.shares }}
            </div>
          </div>
        </div>

        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">可能的內容角度</h2>
          <ul class="mb-0">
            <li v-for="angle in trend.contentAngles" :key="angle">{{ angle }}</li>
          </ul>
        </div>

        <div class="border rounded-3 p-4">
          <h2 class="h5">風險與注意事項</h2>
          <p class="mb-2">{{ trend.riskNote }}</p>
          <div class="small text-secondary">
            過氣風險判斷：{{ trend.lifecycleStage === 'declining' || trend.lifecycleStage === 'expired' ? '偏高' : '可觀察' }}
          </div>
        </div>
      </div>

      <aside class="col-lg-4">
        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">趨勢訊號</h2>
          <dl class="row mb-0">
            <dt class="col-6">Heat Score</dt>
            <dd class="col-6 text-end fw-bold">{{ trend.heatScore }}</dd>
            <dt class="col-6">Growth Rate</dt>
            <dd class="col-6 text-end fw-bold">{{ trend.growthRate > 0 ? '+' : '' }}{{ trend.growthRate }}%</dd>
            <dt class="col-6">Momentum</dt>
            <dd class="col-6 text-end fw-bold">{{ trend.momentum }}</dd>
            <dt class="col-6">Lifecycle</dt>
            <dd class="col-6 text-end fw-bold">{{ lifecycleLabel[trend.lifecycleStage] }}</dd>
          </dl>
        </div>

        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">跨平台表現比較</h2>
          <div v-for="platform in trend.platforms" :key="platform" class="d-flex justify-content-between border-top py-2">
            <span>{{ platform }}</span>
            <span class="fw-semibold">觀察中</span>
          </div>
        </div>

        <div class="border rounded-3 p-4 mb-4">
          <h2 class="h5">適合切入的產業</h2>
          <div class="d-flex flex-wrap gap-2">
            <span v-for="industry in trend.suitableIndustries" :key="industry" class="badge text-bg-success">
              {{ industry }}
            </span>
          </div>
        </div>

        <div class="border rounded-3 p-4">
          <h2 class="h5">不適合硬跟的產業</h2>
          <div class="d-flex flex-wrap gap-2">
            <span v-for="industry in trend.unsuitableIndustries" :key="industry" class="badge text-bg-light border">
              {{ industry }}
            </span>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
