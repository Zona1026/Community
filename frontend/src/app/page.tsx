import { TopicDashboard } from '../components/TopicDashboard';
import { buildDashboardData } from '../lib/dashboard/buildDashboardData';

export default async function HomePage() {
  const dashboardData = await buildDashboardData();

  return (
    <main className="page">
      <div className="page__inner">
        <header className="page__header">
          <p className="page__eyebrow">Trend Radar Phase 1 Demo</p>
          <h1>AI 內容趨勢雷達</h1>
          <p className="page__description">
            整合多來源趨勢訊號，集中展示熱門話題、內容靈感、來源分析與
            AI mock / OpenAI adapter 分析流程。
          </p>
        </header>

        <TopicDashboard
          allTopics={dashboardData.allTopics}
          industryTopics={dashboardData.industryTopics}
          userKeywordTopics={dashboardData.userKeywordTopics}
        />

      </div>
    </main>
  );
}
