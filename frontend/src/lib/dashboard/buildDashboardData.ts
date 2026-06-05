import type { DashboardTopic } from '../../components/TopicDashboard';
import dcardSampleJson from '../../data/importSamples/dcard.sample.json';
import threadsSampleJson from '../../data/importSamples/threads.sample.json';
import { mockData } from '../../data/mockData';
import type { InspirationIdea } from '../../types/inspirationIdea';
import type { NormalizedContent } from '../../types/normalizedContent';
import type { TopicCluster } from '../../types/topicCluster';
import type { TrendReport } from '../../types/trendReport';
import type { TrendSignal } from '../../types/trendSignal';
import { createInspirationIdeas } from '../createInspirationIdeas';
import { createTopicClusters } from '../createTopicClusters';
import { createTrendReports } from '../createTrendReports';
import { createTrendSignals } from '../createTrendSignals';
import { importJsonToContentItems } from '../import/importJsonToContentItems';
import { normalizeContent } from '../normalizeContent';
import { fetchRedditPostsWithStatus } from '../reddit/fetchRedditPosts';
import { redditPostToContentItem } from '../reddit/redditPostToContentItem';

const INDUSTRY_KEYWORDS = ['AI', 'Agent', 'ChatGPT', 'Automation'];
const USER_KEYWORDS = ['AI', '創業'];

export interface DashboardApiData {
  allTopics: DashboardTopic[];
  industryTopics: DashboardTopic[];
  userKeywordTopics: DashboardTopic[];
}

export interface DashboardData extends DashboardApiData {
  demoContent: NormalizedContent[];
  threadsSampleContent: NormalizedContent[];
  dcardSampleContent: NormalizedContent[];
  redditContent: NormalizedContent[];
  inspirationIdeas: InspirationIdea[];
  isRedditEnabled: boolean;
  redditStatus?: {
    isFallback: boolean;
    errorMessage?: string;
    subreddit: string;
  };
}

function createDashboardTopics(
  clusters: TopicCluster[],
  signals: TrendSignal[],
  reports: TrendReport[],
  ideas: InspirationIdea[],
): DashboardTopic[] {
  return clusters.map((cluster) => {
    const signal = signals.find((item) => item.id === cluster.id);
    const report = reports.find((item) => item.id === cluster.id);
    const idea = ideas.find((item) => item.id === cluster.id);
    const platformTags = Array.from(
      new Set(cluster.items.map((item) => item.sourcePlatform)),
    );
    const topicTags = Array.from(
      new Set(
        cluster.items.flatMap((item) => [
          ...item.hotTags,
          ...item.industryTags,
          ...item.keywords,
        ]),
      ),
    );
    const searchText = [
      cluster.name,
      cluster.platform,
      report?.summary,
      ...cluster.items.flatMap((item) => [
        item.topicTitle,
        item.normalizedText,
        item.sourcePlatform,
        ...item.hotTags,
        ...item.industryTags,
        ...item.keywords,
      ]),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    return {
      id: cluster.id,
      topic: report?.topic ?? cluster.name,
      score: report?.score ?? signal?.score ?? 0,
      momentum: report?.momentum ?? signal?.momentum ?? 'weak',
      summary:
        report?.summary ??
        `${cluster.name} 目前整合 ${cluster.items.length} 筆內容。`,
      insight:
        report?.insight ??
        '此話題可作為 Demo 的跨來源內容觀察起點。',
      source: cluster.platform,
      contentCount: cluster.items.length,
      relatedContent: cluster.items.map((item) => ({
        id: item.id,
        title: item.topicTitle,
        source: item.sourcePlatform,
        text: item.normalizedText,
      })),
      inspirationIdeas: idea?.ideas ?? [],
      platformTags: platformTags.length > 0 ? platformTags : [cluster.platform],
      topicTags: topicTags.length > 0 ? topicTags : ['Demo'],
      searchText,
    };
  });
}

function matchesKeywords(topic: DashboardTopic, keywords: string[]): boolean {
  const normalizedKeywords = keywords
    .map((keyword) => keyword.trim().toLowerCase())
    .filter(Boolean);

  return normalizedKeywords.some((keyword) =>
    topic.searchText.toLowerCase().includes(keyword),
  );
}

export async function buildDashboardData(): Promise<DashboardData> {
  const redditResult = await fetchRedditPostsWithStatus();
  const demoContent = normalizeContent(mockData);
  const threadsSampleContent = normalizeContent(
    importJsonToContentItems(threadsSampleJson),
  );
  const dcardSampleContent = normalizeContent(
    importJsonToContentItems(dcardSampleJson),
  );
  const redditContent = normalizeContent(
    redditResult.posts.map(redditPostToContentItem),
  );
  const stableContent = [
    ...demoContent,
    ...threadsSampleContent,
    ...dcardSampleContent,
    ...redditContent,
  ];
  const topicClusters = createTopicClusters(stableContent);
  const trendSignals = createTrendSignals(topicClusters);
  const trendReports = createTrendReports(trendSignals);
  const inspirationIdeas = createInspirationIdeas(trendReports);
  const allTopics = createDashboardTopics(
    topicClusters,
    trendSignals,
    trendReports,
    inspirationIdeas,
  );

  return {
    allTopics,
    industryTopics: allTopics.filter((topic) =>
      matchesKeywords(topic, INDUSTRY_KEYWORDS),
    ),
    userKeywordTopics: allTopics.filter((topic) =>
      matchesKeywords(topic, USER_KEYWORDS),
    ),
    demoContent,
    threadsSampleContent,
    dcardSampleContent,
    redditContent,
    inspirationIdeas,
    isRedditEnabled: true,
    redditStatus: {
      isFallback: redditResult.isFallback,
      errorMessage: redditResult.errorMessage,
      subreddit: redditResult.subreddit,
    },
  };
}
