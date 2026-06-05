import { ContentCard } from '../components/ContentCard';
import { TopicDashboard } from '../components/TopicDashboard';
import { buildDashboardData } from '../lib/dashboard/buildDashboardData';
import type { NormalizedContent } from '../types/normalizedContent';

interface SampleSectionProps {
  title: string;
  eyebrow: string;
  emptyTitle: string;
  emptyDescription: string;
  items: NormalizedContent[];
}

function SampleSection({
  title,
  eyebrow,
  emptyTitle,
  emptyDescription,
  items,
}: SampleSectionProps) {
  return (
    <section className="page-section" aria-label={title}>
      <div className="page-section__header">
        <p className="page-section__eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>

      {items.length > 0 ? (
        <div className="content-list">
          {items.map((item) => (
            <ContentCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <article className="content-card">
          <div className="content-card__source">Empty State</div>
          <h2>{emptyTitle}</h2>
          <p>{emptyDescription}</p>
        </article>
      )}
    </section>
  );
}

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

        <SampleSection
          title="mockData 展示資料"
          eyebrow="mockData"
          emptyTitle="mockData 尚無資料"
          emptyDescription="請確認 frontend/src/data/mockData.ts 是否仍提供 Phase 1 展示資料。"
          items={dashboardData.demoContent}
        />

        <SampleSection
          title="Threads 假資料展示"
          eyebrow="JSON Import"
          emptyTitle="Threads sample 尚無資料"
          emptyDescription="請確認 threads.sample.json 可被 importJsonToContentItems() 轉換。"
          items={dashboardData.threadsSampleContent}
        />

        <SampleSection
          title="Dcard 假資料展示"
          eyebrow="JSON Import"
          emptyTitle="Dcard sample 尚無資料"
          emptyDescription="請確認 dcard.sample.json 可被 importJsonToContentItems() 轉換。"
          items={dashboardData.dcardSampleContent}
        />

        <SampleSection
          title="Reddit 資料來源展示"
          eyebrow={
            dashboardData.redditStatus?.isFallback
              ? 'Reddit fallback data'
              : 'Reddit live data'
          }
          emptyTitle="Reddit 尚無資料"
          emptyDescription="Reddit 資料暫時不可用時，Demo 仍會使用固定 fallback。"
          items={dashboardData.redditContent}
        />

        {dashboardData.redditStatus?.isFallback ? (
          <section className="page-section" aria-label="Reddit fallback notice">
            <article className="content-card">
              <div className="content-card__source">Reddit fallback</div>
              <h2>Reddit 使用固定備援資料</h2>
              <p>
                {dashboardData.redditStatus.errorMessage}
                {' '}目前使用 r/{dashboardData.redditStatus.subreddit} 的固定展示資料。
              </p>
            </article>
          </section>
        ) : null}

        <section className="page-section" aria-label="內容靈感">
          <div className="page-section__header">
            <p className="page-section__eyebrow">Inspiration Ideas</p>
            <h2>內容靈感總覽</h2>
          </div>

          <div className="signal-list">
            {dashboardData.inspirationIdeas.map((item) => (
              <article className="signal-card" key={item.id}>
                <header className="signal-card__header">
                  <div>
                    <p className="signal-card__label">內容靈感</p>
                    <h2>{item.topic}</h2>
                  </div>
                </header>

                <div className="signal-card__layout">
                  <div className="signal-card__panel signal-card__panel--summary">
                    <div className="signal-card__section signal-card__subcard">
                      <h3>摘要</h3>
                      <p>{item.summary}</p>
                    </div>

                    <div className="signal-card__section signal-card__subcard">
                      <h3>洞察</h3>
                      <p>{item.insight}</p>
                    </div>
                  </div>

                  <div className="signal-card__panel signal-card__panel--ideas">
                    <div className="signal-card__section signal-card__subcard">
                      <h3>靈感</h3>
                      <ul>
                        {item.ideas.map((idea) => (
                          <li key={idea}>{idea}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
