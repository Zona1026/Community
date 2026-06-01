<script setup lang="ts">
import { computed, reactive } from 'vue';
import type { InspirationForm, InspirationIdea, Trend } from '../types/trend';

const props = defineProps<{
  trend: Trend;
}>();

const form = reactive<InspirationForm>({
  industry: '',
  brandTone: '',
  targetAudience: '',
  publishingPlatform: '',
  contentFormat: ''
});

const generatedIdea = computed<InspirationIdea>(() => ({
  id: `idea-${props.trend.id}`,
  trendId: props.trend.id,
  ideaTitle: `${form.industry || '你的產業'}可以如何觀察「${props.trend.topicName}」`,
  ideaSummary: `從「${props.trend.summary}」延伸，找出與受眾生活情境有關的切入點。`,
  contentAngle: props.trend.contentAngles[0] || '趨勢解析',
  openingHook: `最近大家都在討論「${props.trend.topicName}」，但它和${form.industry || '你的產業'}有什麼關係？`,
  suggestedPlatforms: [form.publishingPlatform || 'Threads'],
  suggestedFormat: form.contentFormat || '圖文',
  notRecommendedApproach: props.trend.unsuitableIndustries.length
    ? `避免用${props.trend.unsuitableIndustries[0]}的角度硬跟，容易顯得牽強。`
    : '避免只複製熱門梗，應補上自己的觀點與情境。',
  riskNote: props.trend.riskNote
}));
</script>

<template>
  <section class="container-fluid px-4 py-4">
    <div class="row g-4">
      <div class="col-lg-5">
        <div class="border rounded-3 p-4">
          <h2 class="h4 mb-3">內容靈感產生區</h2>
          <p class="text-secondary">
            這裡產生的是內容方向與切入建議，不是完整社群貼文。
          </p>

          <div class="mb-3">
            <label class="form-label">我的產業</label>
            <input v-model="form.industry" class="form-control" placeholder="例如：餐飲業、科技業、房地產" />
          </div>

          <div class="mb-3">
            <label class="form-label">品牌調性</label>
            <input v-model="form.brandTone" class="form-control" placeholder="例如：專業、幽默、溫暖、犀利" />
          </div>

          <div class="mb-3">
            <label class="form-label">目標受眾</label>
            <input v-model="form.targetAudience" class="form-control" placeholder="例如：大學生、上班族、首購族" />
          </div>

          <div class="mb-3">
            <label class="form-label">想發布的平台</label>
            <select v-model="form.publishingPlatform" class="form-select">
              <option value="">請選擇</option>
              <option>Threads</option>
              <option>Instagram</option>
              <option>Dcard</option>
              <option>PTT</option>
              <option>電子報</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">想要的內容形式</label>
            <select v-model="form.contentFormat" class="form-select">
              <option value="">請選擇</option>
              <option>短影音</option>
              <option>圖文</option>
              <option>限動</option>
              <option>長文</option>
              <option>電子報</option>
            </select>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="border rounded-3 p-4 bg-light">
          <span class="badge text-bg-dark mb-3">Inspiration</span>
          <h2 class="h4">{{ generatedIdea.ideaTitle }}</h2>
          <p>{{ generatedIdea.ideaSummary }}</p>

          <dl class="row">
            <dt class="col-sm-4">可以怎麼切入</dt>
            <dd class="col-sm-8">{{ generatedIdea.ideaSummary }}</dd>

            <dt class="col-sm-4">內容角度</dt>
            <dd class="col-sm-8">{{ generatedIdea.contentAngle }}</dd>

            <dt class="col-sm-4">標題方向</dt>
            <dd class="col-sm-8">{{ generatedIdea.ideaTitle }}</dd>

            <dt class="col-sm-4">開場 hook</dt>
            <dd class="col-sm-8">{{ generatedIdea.openingHook }}</dd>

            <dt class="col-sm-4">適合平台</dt>
            <dd class="col-sm-8">{{ generatedIdea.suggestedPlatforms.join('、') }}</dd>

            <dt class="col-sm-4">不建議的切法</dt>
            <dd class="col-sm-8">{{ generatedIdea.notRecommendedApproach }}</dd>

            <dt class="col-sm-4">需要注意的風險</dt>
            <dd class="col-sm-8">{{ generatedIdea.riskNote }}</dd>
          </dl>
        </div>
      </div>
    </div>
  </section>
</template>
