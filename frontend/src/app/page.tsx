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
            使用 mockData、Threads / Dcard JSON sample 與 Reddit fallback
            資料，展示多來源資料整合、熱門話題分類、AI mock / OpenAI
            adapter 分析與文案生成流程。
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
