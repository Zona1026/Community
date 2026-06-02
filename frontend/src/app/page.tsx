import { ContentCard } from '../components/ContentCard';
import { mockData } from '../data/mockData';
import { createInspirationIdeas } from '../lib/createInspirationIdeas';
import { createTopicClusters } from '../lib/createTopicClusters';
import { createTrendReports } from '../lib/createTrendReports';
import { createTrendSignals } from '../lib/createTrendSignals';
import { normalizeContent } from '../lib/normalizeContent';
import { fetchRedditPostsWithStatus } from '../lib/reddit/fetchRedditPosts';
import { redditPostToContentItem } from '../lib/reddit/redditPostToContentItem';

const USE_MOCK_DATA = process.env.USE_MOCK_DATA !== 'false';

export default async function HomePage() {
  const isRedditEnabled = !USE_MOCK_DATA;
  const redditResult = isRedditEnabled
    ? await fetchRedditPostsWithStatus()
    : undefined;
  const redditPosts = redditResult?.posts ?? [];
  const contentItems = USE_MOCK_DATA
    ? mockData
    : redditPosts.map(redditPostToContentItem);
  const normalizedContent = normalizeContent(contentItems);
  const redditContent = isRedditEnabled ? normalizedContent : [];
  const topicClusters = createTopicClusters(normalizedContent);
  const trendSignals = createTrendSignals(topicClusters);
  const trendReports = createTrendReports(trendSignals);
  const inspirationIdeas = createInspirationIdeas(trendReports);

  return (
    <main className="page">
      <div className="page__inner">
        <header className="page__header">
          <p className="page__eyebrow">內容靈感儀表板</p>
          <h1>AI 趨勢探索平台</h1>
          <p className="page__description">
            目前資料會依序完成：假資料讀取、資料標準化、主題分群、趨勢訊號、趨勢報告與內容靈感產生。此頁先用簡單規則顯示可延伸的內容方向。
          </p>
        </header>

        <section className="page-section" aria-label="Reddit 熱門討論">
          <div className="page-section__header">
            <p className="page-section__eyebrow">Reddit 資料來源</p>
            <h2>Reddit 熱門討論</h2>
          </div>

          {isRedditEnabled && redditContent.length > 0 ? (
            <div className="content-list">
              {redditResult?.isFallback ? (
                <article className="content-card">
                  <div className="content-card__source">Reddit 連線狀態</div>
                  <h2>Reddit 資料暫時無法取得</h2>
                  <p>
                    {redditResult.errorMessage}
                    下面會先顯示 r/{redditResult.subreddit} 的備援展示資料，頁面不會因此中斷。
                  </p>
                </article>
              ) : null}

              {redditContent.map((item) => (
                <ContentCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <article className="content-card">
              <div className="content-card__source">目前使用 mockData</div>
              <h2>Reddit 資料尚未啟用</h2>
              <p>
                將環境變數 USE_MOCK_DATA 設為 false 後，這裡會顯示
                r/artificial 的熱門討論資料。
              </p>
            </article>
          )}
        </section>

        <section className="page-section" aria-label="內容靈感建議">
          <div className="page-section__header">
            <p className="page-section__eyebrow">趨勢報告延伸</p>
            <h2>內容靈感卡片</h2>
          </div>

          <div className="signal-list">
          {inspirationIdeas.map((item) => (
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
                    <h3>靈感建議</h3>
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
