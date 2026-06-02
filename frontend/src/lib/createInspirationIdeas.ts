import type { InspirationIdea } from '../types/inspirationIdea';
import type { TrendReport } from '../types/trendReport';

function createIdeas(report: TrendReport): string[] {
  return [
    `用「${report.topic}」做一篇快速懶人包，整理目前大家在討論什麼。`,
    `從品牌或產業角度切入，說明這個主題可能帶來的機會與限制。`,
    `整理一篇社群貼文，提醒使用者觀察這個主題時要注意的風險。`,
    `設計一個互動提問，邀請受眾分享自己對「${report.topic}」的看法。`,
  ];
}

export function createInspirationIdeas(
  reports: TrendReport[],
): InspirationIdea[] {
  return reports.map((report) => ({
    id: report.id,
    topic: report.topic,
    summary: report.summary,
    insight: report.insight,
    ideas: createIdeas(report),
  }));
}
