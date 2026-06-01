import { createRouter, createWebHistory } from 'vue-router';
import IndustryInspirationPage from '../pages/IndustryInspirationPage.vue';
import SavedTrendsPage from '../pages/SavedTrendsPage.vue';
import TrendDetailPage from '../pages/TrendDetailPage.vue';
import TrendExplorePage from '../pages/TrendExplorePage.vue';
import TrendIdeaPage from '../pages/TrendIdeaPage.vue';
import TrendRadarHome from '../pages/TrendRadarHome.vue';
import TrendReportsPage from '../pages/TrendReportsPage.vue';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TrendRadarHome },
    { path: '/explore', component: TrendExplorePage },
    { path: '/industries', component: IndustryInspirationPage },
    { path: '/reports', component: TrendReportsPage },
    { path: '/saved', component: SavedTrendsPage },
    { path: '/trends/:id', component: TrendDetailPage },
    { path: '/trends/:id/ideas', component: TrendIdeaPage }
  ]
});
