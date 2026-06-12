'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import {
  addFavorite,
  fetchFavorites,
  removeFavorite,
} from '../lib/api/favoritesApi';
import { fetchDashboardTopics } from '../lib/api/topicsApi';
import { fetchUserSettings } from '../lib/api/userSettingsApi';
import { createAiAnalysis } from '../lib/ai/createAiAnalysis';
import { requestAiAnalysis } from '../lib/ai/requestAiAnalysis';
import { DEFAULT_FAVORITES_STATE, type FavoritesState } from '../types/favorites';
import { DEFAULT_USER_SETTINGS, type UserSettings } from '../types/userSettings';
import type {
  AiAnalysis,
  AiAnalysisInput,
  AiTone,
  GeneratedCopy,
  PostAngle,
} from '../types/aiAnalysis';
import type { TrendSignal } from '../types/trendSignal';

export interface DashboardRelatedContent {
  id: string;
  title: string;
  source: string;
  text: string;
}

export interface DashboardTopic {
  id: string;
  topic: string;
  score: number;
  growthRate: number;
  momentum: TrendSignal['momentum'];
  lifecycleStage: TrendSignal['lifecycleStage'];
  scoreHistory: TrendSignal['scoreHistory'];
  summary: string;
  insight: string;
  source: string;
  contentCount: number;
  relatedContent: DashboardRelatedContent[];
  inspirationIdeas: string[];
  platformTags: string[];
  topicTags: string[];
  searchText: string;
}

interface TopicDashboardProps {
  allTopics: DashboardTopic[];
  industryTopics: DashboardTopic[];
  userKeywordTopics: DashboardTopic[];
}

interface DashboardOverview {
  totalTopics: number;
  highestScore: number;
  platformCount: number;
  riskTopicCount: number;
}

interface CopyEditorState {
  topic: DashboardTopic;
  copy: GeneratedCopy;
  tone: AiTone;
  angle: PostAngle;
}

interface CopyVersion {
  id: string;
  label: string;
  text: string;
  copy: GeneratedCopy;
}

interface CopyHistoryRecord {
  id: string;
  content: string;
  tone: AiTone;
  createdAt: string;
  topicTitle: string;
}

interface PlatformDistributionItem {
  platform: string;
  count: number;
}

interface SourceStat {
  platform: string;
  contentCount: number;
  totalScore: number;
  averageScore: number;
  topicCount: number;
  share: number;
}

interface TopicSourceBreakdown {
  platform: string;
  contentCount: number;
  scoreContribution: number;
  share: number;
}

interface TopicSourceAnalysis {
  primaryPlatform: string;
  relatedPlatforms: string[];
  breakdown: TopicSourceBreakdown[];
  summary: string;
}

interface PlatformTopicGroup {
  platform: PublicPlatform;
  topics: DashboardTopic[];
}

const AI_TONES: AiTone[] = ['專業', '輕鬆', '犀利'];
const POST_ANGLES: PostAngle[] = ['教學', '觀點', '懶人包'];
const COPY_HISTORY_STORAGE_KEY = 'trend-radar-copy-history';
const INDUSTRY_BASE_KEYWORDS = ['AI', 'Agent', 'ChatGPT', 'Automation'];
const RISK_KEYWORDS = [
  '爭議',
  '風險',
  '炎上',
  '隱私',
  '誤導',
  '偏見',
  '資安',
  '個資',
  '抄襲',
  '版權',
  '擔心',
  '依賴',
];

function getMomentumLabel(momentum: TrendSignal['momentum']): string {
  if (momentum === 'rising') {
    return '上升';
  }

  if (momentum === 'stable') {
    return '穩定';
  }

  return '偏弱';
}

function getMomentumBadgeLevel(
  momentum: TrendSignal['momentum'],
): 'strong' | 'medium' | 'weak' {
  if (momentum === 'rising') {
    return 'strong';
  }

  if (momentum === 'stable') {
    return 'medium';
  }

  return 'weak';
}

function MomentumBadge({ momentum }: { momentum: TrendSignal['momentum'] }) {
  const level = getMomentumBadgeLevel(momentum);

  return (
    <span className={`momentum-badge momentum-badge--${level}`}>
      {getMomentumLabel(momentum)}
    </span>
  );
}

function getLifecycleStageLabel(
  lifecycleStage: TrendSignal['lifecycleStage'],
): string {
  if (lifecycleStage === 'growing') {
    return '成長中';
  }

  if (lifecycleStage === 'mainstream') {
    return '穩定';
  }

  if (lifecycleStage === 'declining') {
    return '衰退';
  }

  return '新興';
}

function createAiInput(
  topic: DashboardTopic,
  tone: AiTone,
  angle: PostAngle,
): AiAnalysisInput {
  return {
    topicId: topic.id,
    topic: topic.topic,
    score: topic.score,
    momentum: topic.momentum,
    summary: topic.summary,
    insight: topic.insight,
    source: topic.source,
    contentCount: topic.contentCount,
    relatedContent: topic.relatedContent,
    platformTags: topic.platformTags,
    topicTags: topic.topicTags,
    tone,
    angle,
  };
}

function topicSearchText(topic: DashboardTopic): string {
  return [
    topic.searchText,
    topic.topic,
    topic.summary,
    topic.insight,
    topic.source,
    ...topic.platformTags,
    ...topic.topicTags,
    ...topic.relatedContent.flatMap((content) => [
      content.title,
      content.text,
      content.source,
    ]),
  ]
    .join(' ')
    .toLowerCase();
}

function normalizeSourceText(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

type PublicPlatform = 'RSS' | 'Podcast' | 'Threads' | 'Dcard';

const PUBLIC_PLATFORM_ORDER: PublicPlatform[] = [
  'RSS',
  'Podcast',
  'Threads',
  'Dcard',
];

function normalizeSourceKey(value: unknown): string {
  return normalizeSourceText(value)
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizePlatformForDisplay(value: unknown): PublicPlatform | null {
  const key = normalizeSourceKey(value);

  if (!key) {
    return null;
  }

  if (key === 'rss' || key === 'hacker news' || key === 'hackernews') {
    return 'RSS';
  }

  if (
    key === 'podcast' ||
    key === 'npr planet money' ||
    key === 'planet money'
  ) {
    return 'Podcast';
  }

  if (key === 'threads') {
    return 'Threads';
  }

  if (key === 'dcard') {
    return 'Dcard';
  }

  return null;
}

function isInternalSource(value: unknown): boolean {
  const key = normalizeSourceKey(value);

  return (
    key === 'backend' ||
    key === 'dev smoke' ||
    key === 'rss smoke test' ||
    key === 'podcast smoke test' ||
    key === 'dcard smoke test' ||
    key.includes('smoke test')
  );
}

function getTopicPublicPlatforms(topic: DashboardTopic): PublicPlatform[] {
  const candidates = [
    topic.source,
    ...topic.platformTags,
    ...topic.relatedContent.map((content) => content.source),
  ];
  const platforms = new Set<PublicPlatform>();

  candidates.forEach((candidate) => {
    const platform = normalizePlatformForDisplay(candidate);

    if (platform) {
      platforms.add(platform);
    }
  });

  return PUBLIC_PLATFORM_ORDER.filter((platform) => platforms.has(platform));
}

function getTopicSourceBadge(topic: DashboardTopic): string {
  const publicPlatform = getTopicPublicPlatforms(topic)[0];

  if (publicPlatform) {
    return publicPlatform;
  }

  const primarySource = normalizeSourceText(topic.source);

  if (isInternalSource(primarySource)) {
    return 'Unknown';
  }

  return primarySource || 'Unknown';
}

function createPlatformTopicGroups(
  topics: DashboardTopic[],
  limitPerPlatform: number,
): PlatformTopicGroup[] {
  return PUBLIC_PLATFORM_ORDER.map((platform) => ({
    platform,
    topics: topics
      .filter((topic) => getTopicPublicPlatforms(topic).includes(platform))
      .slice(0, limitPerPlatform),
  })).filter((group) => group.topics.length > 0);
}

function matchesKeywords(topic: DashboardTopic, keywords: string[]): boolean {
  const searchText = topicSearchText(topic);

  return keywords
    .map((keyword) => keyword.trim().toLowerCase())
    .filter(Boolean)
    .some((keyword) => searchText.includes(keyword));
}

function hasRiskSignal(topic: DashboardTopic): boolean {
  const searchText = topicSearchText(topic);

  return RISK_KEYWORDS.some((keyword) =>
    searchText.includes(keyword.toLowerCase()),
  );
}

function getRiskLabel(topic: DashboardTopic): string {
  if (hasRiskSignal(topic)) {
    return '需人工確認';
  }

  if (topic.momentum === 'weak') {
    return '訊號偏弱';
  }

  return '一般';
}

function hasVisibleTopics(data: TopicDashboardProps): boolean {
  return Array.isArray(data.allTopics) && data.allTopics.length > 0;
}

function normalizeTopic(topic: unknown): DashboardTopic | null {
  if (!topic || typeof topic !== 'object') {
    return null;
  }

  const value = topic as Partial<DashboardTopic>;

  if (!value.id || !value.topic) {
    return null;
  }

  return {
    id: String(value.id),
    topic: String(value.topic),
    score: Number.isFinite(Number(value.score)) ? Number(value.score) : 0,
    growthRate: Number.isFinite(Number(value.growthRate))
      ? Number(value.growthRate)
      : 0,
    momentum:
      value.momentum === 'rising' ||
      value.momentum === 'stable' ||
      value.momentum === 'weak'
        ? value.momentum
        : 'weak',
    lifecycleStage:
      value.lifecycleStage === 'emerging' ||
      value.lifecycleStage === 'growing' ||
      value.lifecycleStage === 'mainstream' ||
      value.lifecycleStage === 'declining'
        ? value.lifecycleStage
        : 'emerging',
    scoreHistory: Array.isArray(value.scoreHistory)
      ? value.scoreHistory
          .filter((point) => point && typeof point === 'object')
          .map((point) => ({
            label: String(point.label ?? ''),
            score: Number.isFinite(Number(point.score))
              ? Number(point.score)
              : 0,
          }))
      : [],
    summary: value.summary ? String(value.summary) : '目前尚無摘要。',
    insight: value.insight ? String(value.insight) : '目前尚無洞察。',
    source: value.source ? String(value.source) : 'Unknown',
    contentCount: Number.isFinite(Number(value.contentCount))
      ? Number(value.contentCount)
      : 0,
    relatedContent: Array.isArray(value.relatedContent)
      ? value.relatedContent
          .filter((content) => content && typeof content === 'object')
          .map((content) => {
            const nextContent = content as Partial<DashboardRelatedContent>;

            return {
              id: String(nextContent.id ?? `${value.id}-content`),
              title: String(nextContent.title ?? value.topic),
              source: String(nextContent.source ?? value.source ?? 'Unknown'),
              text: String(nextContent.text ?? ''),
            };
          })
      : [],
    inspirationIdeas: Array.isArray(value.inspirationIdeas)
      ? value.inspirationIdeas.map(String)
      : [],
    platformTags: Array.isArray(value.platformTags)
      ? value.platformTags.map(String)
      : value.source
        ? [String(value.source)]
        : ['Unknown'],
    topicTags: Array.isArray(value.topicTags)
      ? value.topicTags.map(String)
      : ['Demo'],
    searchText: value.searchText
      ? String(value.searchText)
      : [value.topic, value.summary, value.source].filter(Boolean).join(' '),
  };
}

function normalizeTopicList(topics: unknown): DashboardTopic[] {
  if (!Array.isArray(topics)) {
    return [];
  }

  return topics
    .map(normalizeTopic)
    .filter((topic): topic is DashboardTopic => Boolean(topic));
}

function normalizeTopicsData(
  data: Partial<TopicDashboardProps>,
  fallback: TopicDashboardProps,
): TopicDashboardProps {
  const nextData = {
    allTopics: normalizeTopicList(data.allTopics),
    industryTopics: normalizeTopicList(data.industryTopics),
    userKeywordTopics: normalizeTopicList(data.userKeywordTopics),
  };

  return hasVisibleTopics(nextData) ? nextData : fallback;
}

function createOverview(topics: DashboardTopic[]): DashboardOverview {
  const platforms = new Set(
    topics.flatMap((topic) => getTopicPublicPlatforms(topic)),
  );

  return {
    totalTopics: topics.length,
    highestScore: topics.reduce(
      (highest, topic) => Math.max(highest, topic.score),
      0,
    ),
    platformCount: platforms.size,
    riskTopicCount: topics.filter(hasRiskSignal).length,
  };
}

function createPlatformDistribution(
  topics: DashboardTopic[],
): PlatformDistributionItem[] {
  const counts = new Map<string, number>();

  topics.forEach((topic) => {
    const platforms = getTopicPublicPlatforms(topic);

    platforms.forEach((platform) => {
      counts.set(platform, (counts.get(platform) ?? 0) + topic.contentCount);
    });
  });

  return Array.from(counts.entries())
    .map(([platform, count]) => ({ platform, count }))
    .sort((left, right) => right.count - left.count);
}

function getTopicPlatformCounts(topic: DashboardTopic): Map<string, number> {
  const counts = new Map<string, number>();

  topic.relatedContent.forEach((content) => {
    const platform = normalizePlatformForDisplay(content.source);

    if (platform) {
      counts.set(platform, (counts.get(platform) ?? 0) + 1);
    }
  });

  if (counts.size === 0) {
    const platforms = getTopicPublicPlatforms(topic);

    platforms.forEach((platform) => {
      counts.set(platform, 1);
    });
  }

  return counts;
}

function createTopicSourceAnalysis(topic: DashboardTopic): TopicSourceAnalysis {
  const platformCounts = getTopicPlatformCounts(topic);
  const totalContent = Array.from(platformCounts.values()).reduce(
    (sum, count) => sum + count,
    0,
  );
  const breakdown = Array.from(platformCounts.entries())
    .map(([platform, contentCount]) => {
      const share = totalContent > 0 ? contentCount / totalContent : 0;

      return {
        platform,
        contentCount,
        scoreContribution: Math.round(topic.score * share),
        share,
      };
    })
    .sort((left, right) => right.scoreContribution - left.scoreContribution);
  const primaryPlatform = breakdown[0]?.platform ?? getTopicSourceBadge(topic);
  const relatedPlatforms = breakdown
    .slice(1)
    .map((item) => item.platform);

  return {
    primaryPlatform,
    relatedPlatforms,
    breakdown,
    summary:
      relatedPlatforms.length > 0
        ? `此話題主要由 ${primaryPlatform} 貢獻，其他相關來源包含 ${relatedPlatforms.join(
            '、',
          )}。`
        : `此話題目前主要集中在 ${primaryPlatform}，尚未看到其他平台明顯共同貢獻。`,
  };
}

function createSourceStats(topics: DashboardTopic[]): SourceStat[] {
  const stats = new Map<
    string,
    {
      contentCount: number;
      totalScore: number;
      topicIds: Set<string>;
    }
  >();

  topics.forEach((topic) => {
    const platformCounts = getTopicPlatformCounts(topic);
    const totalContent = Array.from(platformCounts.values()).reduce(
      (sum, count) => sum + count,
      0,
    );

    platformCounts.forEach((contentCount, platform) => {
      const current = stats.get(platform) ?? {
        contentCount: 0,
        totalScore: 0,
        topicIds: new Set<string>(),
      };
      const scoreShare =
        totalContent > 0 ? topic.score * (contentCount / totalContent) : 0;

      current.contentCount += contentCount;
      current.totalScore += scoreShare;
      current.topicIds.add(topic.id);
      stats.set(platform, current);
    });
  });

  const totalScore = Array.from(stats.values()).reduce(
    (sum, item) => sum + item.totalScore,
    0,
  );

  return Array.from(stats.entries())
    .map(([platform, item]) => ({
      platform,
      contentCount: item.contentCount,
      totalScore: Math.round(item.totalScore),
      averageScore:
        item.contentCount > 0
          ? Math.round(item.totalScore / item.contentCount)
          : 0,
      topicCount: item.topicIds.size,
      share: totalScore > 0 ? item.totalScore / totalScore : 0,
    }))
    .sort((left, right) => right.totalScore - left.totalScore);
}

function formatTopicSourceSummary(analysis: TopicSourceAnalysis): string {
  if (analysis.relatedPlatforms.length > 0) {
    return `此話題主要由 ${analysis.primaryPlatform} 帶動，${analysis.relatedPlatforms.join(
      '、',
    )} 也有相關內容，可視為跨平台延伸訊號。`;
  }

  return `此話題目前主要集中在 ${analysis.primaryPlatform}，適合先觀察該平台的留言與互動語境。`;
}

function topicsFromFavoriteIds(
  topics: DashboardTopic[],
  favoriteTopicIds: string[],
): DashboardTopic[] {
  const topicMap = new Map(topics.map((topic) => [topic.id, topic]));

  return favoriteTopicIds
    .map((topicId) => topicMap.get(topicId))
    .filter((topic): topic is DashboardTopic => Boolean(topic));
}

function TopicCard({
  topic,
  isFavorite,
  onOpen,
  onToggleFavorite,
}: {
  topic: DashboardTopic;
  isFavorite: boolean;
  onOpen: (topic: DashboardTopic) => void;
  onToggleFavorite: (topic: DashboardTopic) => void;
}) {
  const sourceBadge = getTopicSourceBadge(topic);

  return (
    <article className={isFavorite ? 'topic-card topic-card--favorite' : 'topic-card'}>
      <header className="topic-card__header">
        <div>
          <p className="topic-card__source">{sourceBadge}</p>
          <h3>{topic.topic}</h3>
        </div>
        <div className="topic-card__score">{topic.score}</div>
      </header>

      <p className="topic-card__summary">{topic.summary}</p>

      <dl className="topic-card__meta">
        <div>
          <dt>成長率</dt>
          <dd>{topic.growthRate}%</dd>
        </div>
        <div>
          <dt>熱度趨勢</dt>
          <dd>
            <MomentumBadge momentum={topic.momentum} />
          </dd>
        </div>
        <div>
          <dt>生命週期</dt>
          <dd>{getLifecycleStageLabel(topic.lifecycleStage)}</dd>
        </div>
        <div>
          <dt>來源</dt>
          <dd>{sourceBadge}</dd>
        </div>
        <div>
          <dt>內容數</dt>
          <dd>{topic.contentCount}</dd>
        </div>
      </dl>

      <div className="topic-card__actions">
        <button type="button" onClick={() => onOpen(topic)}>
          查看詳情
        </button>
        <button
          aria-pressed={isFavorite}
          className={isFavorite ? 'topic-card__favorite is-active' : 'topic-card__favorite'}
          type="button"
          onClick={() => onToggleFavorite(topic)}
        >
          {isFavorite ? '已收藏' : '收藏'}
        </button>
      </div>
    </article>
  );
}

function DashboardSection({
  title,
  eyebrow,
  emptyTitle,
  emptyDescription,
  topics,
  favoriteTopicIds,
  onOpenTopic,
  onToggleFavorite,
}: {
  title: string;
  eyebrow: string;
  emptyTitle: string;
  emptyDescription: string;
  topics: DashboardTopic[];
  favoriteTopicIds: string[];
  onOpenTopic: (topic: DashboardTopic) => void;
  onToggleFavorite: (topic: DashboardTopic) => void;
}) {
  return (
    <section className="dashboard-section" aria-label={title}>
      <div className="page-section__header">
        <p className="page-section__eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>

      {topics.length > 0 ? (
        <div className="topic-card-list">
          {topics.map((topic) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              isFavorite={favoriteTopicIds.includes(topic.id)}
              onOpen={onOpenTopic}
              onToggleFavorite={onToggleFavorite}
            />
          ))}
        </div>
      ) : (
        <article className="topic-card topic-card--empty">
          <p className="topic-card__source">Empty State</p>
          <h3>{emptyTitle}</h3>
          <p className="topic-card__summary">{emptyDescription}</p>
        </article>
      )}
    </section>
  );
}

function GroupedTopicsSection({
  title,
  eyebrow,
  emptyTitle,
  emptyDescription,
  groups,
  favoriteTopicIds,
  onOpenTopic,
  onToggleFavorite,
}: {
  title: string;
  eyebrow: string;
  emptyTitle: string;
  emptyDescription: string;
  groups: PlatformTopicGroup[];
  favoriteTopicIds: string[];
  onOpenTopic: (topic: DashboardTopic) => void;
  onToggleFavorite: (topic: DashboardTopic) => void;
}) {
  return (
    <section className="dashboard-section" aria-label={title}>
      <div className="page-section__header">
        <p className="page-section__eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
      </div>

      {groups.length > 0 ? (
        groups.map((group) => (
          <article className="dashboard-data-card" key={group.platform}>
            <div className="dashboard-data-card__header">
              <p className="page-section__eyebrow">{group.platform}</p>
              <h3>{group.platform}</h3>
            </div>
            <div className="topic-card-list">
              {group.topics.map((topic) => (
                <TopicCard
                  key={`${group.platform}-${topic.id}`}
                  topic={topic}
                  isFavorite={favoriteTopicIds.includes(topic.id)}
                  onOpen={onOpenTopic}
                  onToggleFavorite={onToggleFavorite}
                />
              ))}
            </div>
          </article>
        ))
      ) : (
        <article className="topic-card topic-card--empty">
          <p className="topic-card__source">Empty State</p>
          <h3>{emptyTitle}</h3>
          <p className="topic-card__summary">{emptyDescription}</p>
        </article>
      )}
    </section>
  );
}

function InspirationIdeasPanel({ topics }: { topics: DashboardTopic[] }) {
  if (topics.length === 0) {
    return null;
  }

  const featuredTopic = topics[0];

  return (
    <section className="dashboard-section" aria-label="內容靈感總覽">
      <div className="page-section__header">
        <p className="page-section__eyebrow">Inspiration Ideas</p>
        <h2>內容靈感總覽</h2>
      </div>

      <div className="signal-list">
        <article className="signal-card" key={featuredTopic.id}>
          <header className="signal-card__header">
            <div>
              <p className="signal-card__label">內容靈感</p>
              <h2>{featuredTopic.topic}</h2>
            </div>
          </header>

          <div className="signal-card__layout">
            <div className="signal-card__panel signal-card__panel--summary">
              <div className="signal-card__section signal-card__subcard">
                <h3>摘要</h3>
                <p>{featuredTopic.summary}</p>
              </div>

              <div className="signal-card__section signal-card__subcard">
                <h3>洞察</h3>
                <p>{featuredTopic.insight}</p>
              </div>
            </div>

            <div className="signal-card__panel signal-card__panel--ideas">
              <div className="signal-card__section signal-card__subcard">
                <h3>靈感</h3>
                {featuredTopic.inspirationIdeas.length > 0 ? (
                  <ul>
                    {featuredTopic.inspirationIdeas.map((idea) => (
                      <li key={idea}>{idea}</li>
                    ))}
                  </ul>
                ) : (
                  <p>目前尚無靈感建議。</p>
                )}
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>
  );
}

function FavoriteTopicsSection({
  topics,
  favoriteTopicIds,
  onOpenTopic,
  onToggleFavorite,
}: {
  topics: DashboardTopic[];
  favoriteTopicIds: string[];
  onOpenTopic: (topic: DashboardTopic) => void;
  onToggleFavorite: (topic: DashboardTopic) => void;
}) {
  return (
    <DashboardSection
      title="我的收藏"
      eyebrow={`Favorites · ${favoriteTopicIds.length}`}
      emptyTitle="尚未收藏話題"
      emptyDescription="可在任一話題卡片點擊收藏，重整頁面後仍會保留。"
      topics={topics}
      favoriteTopicIds={favoriteTopicIds}
      onOpenTopic={onOpenTopic}
      onToggleFavorite={onToggleFavorite}
    />
  );
}

function TrendOverview({
  overview,
  favoriteCount,
}: {
  overview: DashboardOverview;
  favoriteCount: number;
}) {
  const items = [
    { label: '總話題數', value: overview.totalTopics },
    { label: '最高熱門分數', value: overview.highestScore },
    { label: '涉及平台數', value: overview.platformCount },
    { label: '爭議提醒話題', value: overview.riskTopicCount },
    { label: '收藏數量', value: favoriteCount },
  ];

  return (
    <article className="dashboard-data-card" aria-label="趨勢總覽">
      <div className="dashboard-data-card__header">
        <p className="page-section__eyebrow">Overview</p>
        <h3>趨勢總覽</h3>
      </div>
      <div className="dashboard-metric-grid dashboard-metric-grid--five">
        {items.map((item) => (
          <article className="dashboard-metric" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>
    </article>
  );
}

function TopTopicsRanking({
  topics,
  favoriteTopicIds,
  onOpenTopic,
  onToggleFavorite,
}: {
  topics: DashboardTopic[];
  favoriteTopicIds: string[];
  onOpenTopic: (topic: DashboardTopic) => void;
  onToggleFavorite: (topic: DashboardTopic) => void;
}) {
  const topTopics = [...topics]
    .sort((left, right) => right.score - left.score)
    .slice(0, 5);

  return (
    <article className="dashboard-data-card" aria-label="熱門排行">
      <div className="dashboard-data-card__header">
        <p className="page-section__eyebrow">Top Ranking</p>
        <h3>熱門排行</h3>
      </div>

      {topTopics.length > 0 ? (
        <div className="ranking-list">
          {topTopics.map((topic, index) => {
            const isFavorite = favoriteTopicIds.includes(topic.id);

            return (
              <article className="ranking-row" key={topic.id}>
                <button type="button" onClick={() => onOpenTopic(topic)}>
                  <span className="ranking-row__rank">{index + 1}</span>
                  <span className="ranking-row__topic">{topic.topic}</span>
                  <span className="ranking-row__platform">
                    {getTopicSourceBadge(topic)}
                  </span>
                  <strong>{topic.score}</strong>
                  <span className="ranking-row__risk">{getRiskLabel(topic)}</span>
                </button>
                <button
                  aria-pressed={isFavorite}
                  className={isFavorite ? 'ranking-row__favorite is-active' : 'ranking-row__favorite'}
                  type="button"
                  onClick={() => onToggleFavorite(topic)}
                >
                  {isFavorite ? '已收藏' : '收藏'}
                </button>
              </article>
            );
          })}
        </div>
      ) : (
        <article className="dashboard-empty">
          <h3>尚無排行資料</h3>
          <p>目前沒有可排序的熱門話題。</p>
        </article>
      )}
    </article>
  );
}

function PlatformDistribution({
  items,
}: {
  items: PlatformDistributionItem[];
}) {
  const total = items.reduce((sum, item) => sum + item.count, 0);

  return (
    <article className="dashboard-data-card" aria-label="平台分布">
      <div className="dashboard-data-card__header">
        <p className="page-section__eyebrow">Platform Mix</p>
        <h3>平台分布</h3>
      </div>

      {items.length > 0 ? (
        <div className="platform-list">
          {items.map((item) => (
            <article className="platform-row" key={item.platform}>
              <div>
                <strong>{item.platform}</strong>
                <span>{item.count} 筆內容</span>
              </div>
              <div className="platform-row__bar" aria-hidden="true">
                <span
                  style={{
                    width: `${total > 0 ? (item.count / total) * 100 : 0}%`,
                  }}
                />
              </div>
            </article>
          ))}
        </div>
      ) : (
        <article className="dashboard-empty">
          <h3>尚無平台分布</h3>
          <p>資料不足時會保留空狀態，不影響其他 Dashboard 區塊。</p>
        </article>
      )}
    </article>
  );
}

function SourceAnalysisPanel({
  stats,
}: {
  stats: SourceStat[];
}) {
  const maxScore = stats.reduce(
    (highest, item) => Math.max(highest, item.totalScore),
    0,
  );
  const maxContentCount = stats.reduce(
    (highest, item) => Math.max(highest, item.contentCount),
    0,
  );
  const topPlatform = stats[0];

  return (
    <section className="dashboard-section" aria-label="Source Analysis">
      <div className="page-section__header">
        <p className="page-section__eyebrow">Source Analysis</p>
        <h2>來源分析</h2>
        <p className="page-section__description">
          比較 Threads、Dcard、Reddit 等平台對話題熱度與內容量的貢獻。
        </p>
      </div>

      {stats.length > 0 ? (
        <div className="source-analysis">
          <article className="source-summary">
            <h3>來源摘要</h3>
            <p>
              目前共納入 {stats.length} 個平台訊號，{topPlatform.platform}
              的熱度貢獻最高，約占 {Math.round(topPlatform.share * 100)}%。
              分數以現有 topic score 依各平台內容占比分攤，適合用來判斷哪個平台最值得優先觀察。
            </p>
          </article>
          <article className="source-summary">
            <h3>來源摘要</h3>
            <p>
              目前共有 {stats.length} 個來源平台被納入統計，
              {topPlatform.platform} 的總熱門分數最高，貢獻約{' '}
              {Math.round(topPlatform.share * 100)}%。此分析使用現有內容數與
              topic score 計算，不依賴額外外部 API。
            </p>
          </article>

          <div className="source-analysis__grid">
            <section className="source-analysis__panel">
              <h3>平台熱度比較</h3>
              <div className="source-analysis__rows">
                {stats.map((item) => (
                  <article className="source-analysis__row" key={item.platform}>
                    <div>
                      <strong>{item.platform}</strong>
                      <span>
                        總分 {item.totalScore} · 平均 {item.averageScore}
                      </span>
                    </div>
                    <div className="source-analysis__bar" aria-hidden="true">
                      <span
                        style={{
                          width: `${
                            maxScore > 0
                              ? (item.totalScore / maxScore) * 100
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="source-analysis__panel">
              <h3>平台內容量比較</h3>
              <div className="source-analysis__rows">
                {stats.map((item) => (
                  <article className="source-analysis__row" key={item.platform}>
                    <div>
                      <strong>{item.platform}</strong>
                      <span>
                        {item.contentCount} 筆內容 · {item.topicCount} 個話題
                      </span>
                    </div>
                    <div className="source-analysis__bar" aria-hidden="true">
                      <span
                        style={{
                          width: `${
                            maxContentCount > 0
                              ? (item.contentCount / maxContentCount) * 100
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </div>
      ) : (
        <article className="dashboard-empty">
          <h3>尚無來源分析</h3>
          <p>目前沒有足夠資料計算來源貢獻。</p>
        </article>
      )}
    </section>
  );
}

function DashboardStatusNotice({
  dataSourceLabel,
  settingsSourceLabel,
  favoritesSourceLabel,
}: {
  dataSourceLabel: string;
  settingsSourceLabel: string;
  favoritesSourceLabel: string;
}) {
  const isFallback = dataSourceLabel !== 'API data';

  return (
    <article
      className={
        isFallback
          ? 'dashboard-status dashboard-status--fallback'
          : 'dashboard-status'
      }
    >
      <strong>{isFallback ? '目前使用 fallback 資料' : '目前使用 API 資料'}</strong>
      <p>
        資料來源：{dataSourceLabel}；設定來源：{settingsSourceLabel}；收藏來源：
        {favoritesSourceLabel}。API 失敗或回傳空資料時，Dashboard 會保留
        mockData / JSON sample 與 localStorage fallback。
      </p>
    </article>
  );
}

function TagList({ label, tags }: { label: string; tags: string[] }) {
  const visibleTags = tags.length > 0 ? tags : ['尚無標籤'];

  return (
    <div className="topic-detail__tag-group">
      <h4>{label}</h4>
      <div className="topic-detail__tags">
        {visibleTags.map((tag) => (
          <span key={tag}>{tag}</span>
        ))}
      </div>
    </div>
  );
}

function TrendChartMvp({
  scoreHistory,
}: {
  scoreHistory: TrendSignal['scoreHistory'];
}) {
  if (scoreHistory.length === 0) {
    return <p>No score history available.</p>;
  }

  const chartWidth = 320;
  const chartHeight = 160;
  const paddingX = 28;
  const paddingY = 22;
  const scores = scoreHistory.map((point) => point.score);
  const minScore = Math.min(...scores);
  const maxScore = Math.max(...scores);
  const scoreRange = maxScore - minScore || 1;
  const plotWidth = chartWidth - paddingX * 2;
  const plotHeight = chartHeight - paddingY * 2;
  const points = scoreHistory.map((point, index) => {
    const x =
      scoreHistory.length === 1
        ? chartWidth / 2
        : paddingX + (index / (scoreHistory.length - 1)) * plotWidth;
    const y =
      chartHeight -
      paddingY -
      ((point.score - minScore) / scoreRange) * plotHeight;

    return {
      ...point,
      x,
      y,
    };
  });
  const linePoints = points.map((point) => `${point.x},${point.y}`).join(' ');

  return (
    <div className="trend-chart" aria-label="Score history trend chart">
      <svg
        aria-hidden="true"
        className="trend-chart__svg"
        focusable="false"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
      >
        <line
          className="trend-chart__axis"
          x1={paddingX}
          x2={chartWidth - paddingX}
          y1={chartHeight - paddingY}
          y2={chartHeight - paddingY}
        />
        <line
          className="trend-chart__axis"
          x1={paddingX}
          x2={paddingX}
          y1={paddingY}
          y2={chartHeight - paddingY}
        />
        <polyline className="trend-chart__line" points={linePoints} />
        {points.map((point) => (
          <g key={`${point.label}-${point.score}`}>
            <circle
              className="trend-chart__point"
              cx={point.x}
              cy={point.y}
              r="4"
            />
            <text
              className="trend-chart__score"
              x={point.x}
              y={Math.max(point.y - 10, 12)}
              textAnchor="middle"
            >
              {point.score}
            </text>
            <text
              className="trend-chart__label"
              x={point.x}
              y={chartHeight - 6}
              textAnchor="middle"
            >
              {point.label}
            </text>
          </g>
        ))}
      </svg>
      <ul className="trend-chart__values">
        {scoreHistory.map((point) => (
          <li key={`${point.label}-${point.score}-value`}>
            {point.label}: {point.score}
          </li>
        ))}
      </ul>
    </div>
  );
}

function SelectField<TValue extends string>({
  id,
  label,
  value,
  options,
  onChange,
}: {
  id: string;
  label: string;
  value: TValue;
  options: TValue[];
  onChange: (value: TValue) => void;
}) {
  return (
    <label className="topic-detail__select" htmlFor={id}>
      <span>{label}</span>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value as TValue)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function AiCopyEditorModal({
  copy,
  topicTitle,
  tone,
  angle,
  onRegenerate,
  onClose,
}: {
  copy: GeneratedCopy;
  topicTitle: string;
  tone: AiTone;
  angle: PostAngle;
  onRegenerate: () => Promise<GeneratedCopy | null>;
  onClose: () => void;
}) {
  const [versions, setVersions] = useState<CopyVersion[]>(() => [
    {
      id: copy.id,
      label: 'Version 1',
      text: copy.text,
      copy,
    },
  ]);
  const [selectedVersionId, setSelectedVersionId] = useState(copy.id);
  const [editedText, setEditedText] = useState(copy.text);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'success' | 'error'>(
    'idle',
  );
  const [historyStatus, setHistoryStatus] = useState<
    'idle' | 'saved' | 'empty' | 'error' | 'loaded'
  >('idle');
  const [copyHistory, setCopyHistory] = useState<CopyHistoryRecord[]>([]);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenerateError, setRegenerateError] = useState('');

  useEffect(() => {
    try {
      const rawHistory = window.localStorage.getItem(COPY_HISTORY_STORAGE_KEY);

      if (!rawHistory) {
        return;
      }

      const parsedHistory = JSON.parse(rawHistory) as CopyHistoryRecord[];

      if (Array.isArray(parsedHistory)) {
        setCopyHistory(
          parsedHistory.filter(
            (record) =>
              record &&
              typeof record.id === 'string' &&
              typeof record.content === 'string' &&
              typeof record.tone === 'string' &&
              typeof record.createdAt === 'string' &&
              typeof record.topicTitle === 'string',
          ),
        );
      }
    } catch {
      setCopyHistory([]);
    }
  }, []);

  useEffect(() => {
    setVersions((currentVersions) => {
      if (currentVersions.some((version) => version.id === copy.id)) {
        return currentVersions;
      }

      return [
        ...currentVersions,
        {
          id: copy.id,
          label: `Version ${currentVersions.length + 1}`,
          text: copy.text,
          copy,
        },
      ];
    });
    setSelectedVersionId(copy.id);
    setEditedText(copy.text);
    setCopyStatus('idle');
    setHistoryStatus('idle');
    setRegenerateError('');
  }, [copy]);

  function updateSelectedVersionText(text: string) {
    setVersions((currentVersions) =>
      currentVersions.map((version) =>
        version.id === selectedVersionId
          ? {
              ...version,
              text,
            }
          : version,
      ),
    );
  }

  function handleTextChange(text: string) {
    setEditedText(text);
    updateSelectedVersionText(text);
  }

  function handleSelectVersion(versionId: string) {
    updateSelectedVersionText(editedText);

    const nextVersion = versions.find((version) => version.id === versionId);

    if (!nextVersion) {
      return;
    }

    setSelectedVersionId(versionId);
    setEditedText(nextVersion.text);
    setCopyStatus('idle');
    setHistoryStatus('idle');
    setRegenerateError('');
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(editedText);
      setCopyStatus('success');
      setHistoryStatus('idle');
    } catch {
      setCopyStatus('error');
      setHistoryStatus('idle');
    }
  }

  async function handleRegenerate() {
    setIsRegenerating(true);
    setRegenerateError('');
    setCopyStatus('idle');
    setHistoryStatus('idle');

    try {
      const nextCopy = await onRegenerate();

      if (!nextCopy) {
        setRegenerateError('重新生成失敗，請稍後再試。');
        return;
      }

      setEditedText(nextCopy.text);
      setCopyStatus('idle');
    } catch {
      setRegenerateError('重新生成失敗，請稍後再試。');
    } finally {
      setIsRegenerating(false);
    }
  }

  function handleSaveToHistory() {
    const content = editedText.trim();

    setCopyStatus('idle');
    setRegenerateError('');

    if (!content) {
      setHistoryStatus('empty');
      return;
    }

    const record: CopyHistoryRecord = {
      id:
        typeof crypto !== 'undefined' && 'randomUUID' in crypto
          ? crypto.randomUUID()
          : `${Date.now()}`,
      content: editedText,
      tone,
      createdAt: new Date().toISOString(),
      topicTitle,
    };
    const nextHistory = [record, ...copyHistory];

    try {
      window.localStorage.setItem(
        COPY_HISTORY_STORAGE_KEY,
        JSON.stringify(nextHistory),
      );
      setCopyHistory(nextHistory);
      setHistoryStatus('saved');
    } catch {
      setHistoryStatus('error');
    }
  }

  function handleLoadHistory(record: CopyHistoryRecord) {
    handleTextChange(record.content);
    setCopyStatus('idle');
    setRegenerateError('');
    setHistoryStatus('loaded');
  }

  function getStatusMessage() {
    if (isRegenerating) {
      return '重新生成中';
    }

    if (regenerateError) {
      return regenerateError;
    }

    if (copyStatus === 'success') {
      return '已複製';
    }

    if (copyStatus === 'error') {
      return '複製失敗，請手動選取文字';
    }

    if (historyStatus === 'saved') {
      return '已儲存到 History';
    }

    if (historyStatus === 'loaded') {
      return '已載入歷史紀錄';
    }

    if (historyStatus === 'empty') {
      return '文案內容為空，無法儲存。';
    }

    if (historyStatus === 'error') {
      return 'History 儲存失敗，請稍後再試。';
    }

    return '';
  }

  return (
    <div className="copy-editor-modal" role="presentation">
      <button
        aria-label="關閉文案編輯視窗"
        className="copy-editor-modal__backdrop"
        type="button"
        onClick={onClose}
      />
      <section
        aria-label="AI 文案編輯"
        aria-modal="true"
        className="copy-editor"
        role="dialog"
      >
        <header className="copy-editor__header">
          <div>
            <p className="topic-detail__eyebrow">
              Tone: {tone}
            </p>
            <h3>AI Copy Editor</h3>
          </div>
          <button className="topic-detail__close" type="button" onClick={onClose}>
            關閉
          </button>
        </header>

        <dl className="copy-editor__meta">
          <div>
            <dt>Tone</dt>
            <dd>{tone}</dd>
          </div>
          <div>
            <dt>Angle</dt>
            <dd>{angle}</dd>
          </div>
        </dl>

        <div className="copy-editor__versions" aria-label="文案版本">
          {versions.map((version) => (
            <button
              key={version.id}
              className={
                version.id === selectedVersionId
                  ? 'copy-editor__version is-active'
                  : 'copy-editor__version'
              }
              type="button"
              onClick={() => handleSelectVersion(version.id)}
            >
              {version.label}
            </button>
          ))}
        </div>

        <textarea
          aria-label="AI 文案內容"
          className="copy-editor__textarea"
          value={editedText}
          onChange={(event) => handleTextChange(event.target.value)}
        />

        <section className="copy-editor__history" aria-label="Copy History">
          <div className="copy-editor__history-header">
            <h4>History</h4>
            <span>{copyHistory.length}</span>
          </div>
          {copyHistory.length > 0 ? (
            <div className="copy-editor__history-list">
              {copyHistory.map((record) => (
                <button
                  key={record.id}
                  className="copy-editor__history-item"
                  type="button"
                  onClick={() => handleLoadHistory(record)}
                >
                  <strong>{record.topicTitle}</strong>
                  <span>
                    {record.tone} ·{' '}
                    {new Date(record.createdAt).toLocaleString('zh-TW')}
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <p>尚無歷史紀錄。</p>
          )}
        </section>

        <footer className="copy-editor__footer">
          <span className="copy-editor__status" aria-live="polite">
            {getStatusMessage()}
          </span>
          <div className="copy-editor__actions">
            <button
              className="copy-editor__regenerate"
              type="button"
              onClick={handleRegenerate}
              disabled={isRegenerating}
            >
              {isRegenerating ? '重新生成中' : '重新生成'}
            </button>
            <button
              className="copy-editor__copy"
              type="button"
              onClick={handleCopy}
              disabled={isRegenerating}
            >
              一鍵複製
            </button>
            <button
              className="copy-editor__save"
              type="button"
              onClick={handleSaveToHistory}
              disabled={isRegenerating}
            >
              保存
            </button>
          </div>
        </footer>
      </section>
    </div>
  );
}

function TopicDetailModal({
  topic,
  defaultTone,
  onGenerateCopy,
  onClose,
}: {
  topic: DashboardTopic;
  defaultTone: AiTone;
  onGenerateCopy: (
    topic: DashboardTopic,
    tone: AiTone,
    angle: PostAngle,
  ) => Promise<void>;
  onClose: () => void;
}) {
  const sourceAnalysis = useMemo(
    () => createTopicSourceAnalysis(topic),
    [topic],
  );
  const [tone, setTone] = useState<AiTone>(defaultTone);
  const [angle, setAngle] = useState<PostAngle>('教學');
  const aiInput = useMemo(
    () => createAiInput(topic, tone, angle),
    [angle, tone, topic],
  );
  const [analysis, setAnalysis] = useState<AiAnalysis>(() =>
    createAiAnalysis(aiInput),
  );
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    let isCurrent = true;
    const fallback = createAiAnalysis(aiInput);

    setAnalysis(fallback);

    requestAiAnalysis(aiInput).then((nextAnalysis) => {
      if (isCurrent) {
        setAnalysis(nextAnalysis);
      }
    });

    return () => {
      isCurrent = false;
    };
  }, [aiInput]);

  async function handleGenerateClick() {
    setIsGenerating(true);

    try {
      await onGenerateCopy(topic, tone, angle);
    } finally {
      setIsGenerating(false);
    }
  }

  const providerLabel =
    !analysis.isFallback && analysis.provider === 'gemini'
      ? 'Gemini'
      : !analysis.isFallback && analysis.provider === 'openai'
        ? 'OpenAI'
        : 'Mock Fallback';
  const sourceBadge = getTopicSourceBadge(topic);

  return (
    <div className="topic-detail-modal" role="presentation">
      <button
        aria-label="關閉話題詳情"
        className="topic-detail-modal__backdrop"
        type="button"
        onClick={onClose}
      />
      <section
        aria-label={`${topic.topic} 詳情`}
        aria-modal="true"
        className="topic-detail"
        role="dialog"
      >
        <header className="topic-detail__header">
          <div>
            <p className="topic-detail__eyebrow">{sourceBadge}</p>
            <h2>{topic.topic}</h2>
          </div>
          <button className="topic-detail__close" type="button" onClick={onClose}>
            關閉
          </button>
        </header>

        <dl className="topic-detail__stats">
          <div>
            <dt>Score</dt>
            <dd>{topic.score}</dd>
          </div>
          <div>
            <dt>成長率</dt>
            <dd>{topic.growthRate}%</dd>
          </div>
          <div>
            <dt>熱度趨勢</dt>
            <dd>
              <MomentumBadge momentum={topic.momentum} />
            </dd>
          </div>
          <div>
            <dt>生命週期</dt>
            <dd>{getLifecycleStageLabel(topic.lifecycleStage)}</dd>
          </div>
          <div>
            <dt>來源</dt>
            <dd>{sourceBadge}</dd>
          </div>
          <div>
            <dt>內容數</dt>
            <dd>{topic.contentCount}</dd>
          </div>
        </dl>

        <div className="topic-detail__grid">
          <section className="topic-detail__panel">
            <h3>Summary</h3>
            <p>{topic.summary}</p>
          </section>

          <section className="topic-detail__panel">
            <h3>Insight</h3>
            <p>{topic.insight}</p>
          </section>

          <section className="topic-detail__panel">
            <h3>Score History</h3>
            <TrendChartMvp scoreHistory={topic.scoreHistory} />
          </section>

          <section className="topic-detail__panel topic-detail__panel--warning">
            <h3>爭議提醒</h3>
            <p>{analysis.controversyWarning}</p>
          </section>

          <section className="topic-detail__panel">
            <h3>標籤區</h3>
            <TagList label="Platform Tags" tags={topic.platformTags} />
            <TagList label="Topic Tags" tags={topic.topicTags} />
          </section>

          <section className="topic-detail__panel">
            <h3>來源分析</h3>
            <p>主要來源平台：{sourceAnalysis.primaryPlatform}</p>
            <p>
              其他相關來源：
              {sourceAnalysis.relatedPlatforms.length > 0
                ? sourceAnalysis.relatedPlatforms.join('、')
                : '尚未偵測到'}
            </p>
            <p>{formatTopicSourceSummary(sourceAnalysis)}</p>
            <div className="topic-detail__source-list">
              <div>
                <strong>主要來源平台</strong>
                <span>{sourceAnalysis.primaryPlatform}</span>
              </div>
              <div>
                <strong>其他相關平台</strong>
                <span>
                  {sourceAnalysis.relatedPlatforms.length > 0
                    ? sourceAnalysis.relatedPlatforms.join('、')
                    : '目前沒有其他平台訊號'}
                </span>
              </div>
            </div>
            <div className="topic-detail__source-list">
              {sourceAnalysis.breakdown.map((item) => (
                <div key={item.platform}>
                  <strong>{item.platform}</strong>
                  <span>
                    {item.contentCount} 筆 · 占比{' '}
                    {Math.round(item.share * 100)}% · 貢獻分數{' '}
                    {item.scoreContribution}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="topic-detail__panel">
            <h3>Related Content</h3>
            {topic.relatedContent.length > 0 ? (
              <ul className="topic-detail__list">
                {topic.relatedContent.map((content) => (
                  <li key={content.id}>
                    <strong>{content.title}</strong>
                    <span>{content.source}</span>
                    <p>{content.text}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>尚無相關內容。</p>
            )}
          </section>

          <section className="topic-detail__panel">
            <h3>Inspiration Ideas</h3>
            {topic.inspirationIdeas.length > 0 ? (
              <ul className="topic-detail__list">
                {topic.inspirationIdeas.map((idea) => (
                  <li key={idea}>{idea}</li>
                ))}
              </ul>
            ) : (
              <p>尚無內容靈感。</p>
            )}
          </section>

          <section className="topic-detail__panel topic-detail__panel--wide">
            <div className="topic-detail__panel-header">
              <div>
                <p className="topic-detail__eyebrow">{providerLabel}</p>
                <h3>AI 分析與內容生成</h3>
              </div>
            </div>

            <div className="topic-detail__controls">
              <SelectField
                id="ai-tone"
                label="語氣"
                value={tone}
                options={AI_TONES}
                onChange={setTone}
              />
              <SelectField
                id="post-angle"
                label="發文角度"
                value={angle}
                options={POST_ANGLES}
                onChange={setAngle}
              />
              <button
                className="topic-detail__generate"
                type="button"
                onClick={handleGenerateClick}
                disabled={isGenerating}
              >
                {isGenerating ? '產生中' : '產生文案'}
              </button>
            </div>

            {analysis.errorMessage ? (
              <p className="topic-detail__error">{analysis.errorMessage}</p>
            ) : null}

            <div className="topic-detail__ai-grid">
              <section>
                <h4>AI 短摘要</h4>
                <p>{analysis.shortSummary}</p>
              </section>
              <section>
                <h4>AI 完整摘要</h4>
                <p>{analysis.fullSummary}</p>
              </section>
              <section>
                <h4>內容靈感</h4>
                {analysis.contentIdeas.length > 0 ? (
                  <ul className="topic-detail__list">
                    {analysis.contentIdeas.map((idea) => (
                      <li key={idea}>{idea}</li>
                    ))}
                  </ul>
                ) : (
                  <p>AI 內容靈感暫時無法產生。</p>
                )}
              </section>
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}

export function TopicDashboard({
  allTopics,
  industryTopics,
  userKeywordTopics,
}: TopicDashboardProps) {
  const [selectedTopic, setSelectedTopic] = useState<DashboardTopic | null>(null);
  const [topicsData, setTopicsData] = useState<TopicDashboardProps>({
    allTopics,
    industryTopics,
    userKeywordTopics,
  });
  const [userSettings, setUserSettings] =
    useState<UserSettings>(DEFAULT_USER_SETTINGS);
  const [favoritesState, setFavoritesState] =
    useState<FavoritesState>(DEFAULT_FAVORITES_STATE);
  const [dataSourceLabel, setDataSourceLabel] = useState('Fallback data');
  const [settingsSourceLabel, setSettingsSourceLabel] = useState('Fallback settings');
  const [favoritesSourceLabel, setFavoritesSourceLabel] =
    useState('Fallback favorites');
  const [copyEditorState, setCopyEditorState] =
    useState<CopyEditorState | null>(null);

  useEffect(() => {
    let isCurrent = true;
    const fallbackTopicsData = {
      allTopics,
      industryTopics,
      userKeywordTopics,
    };

    fetchDashboardTopics()
      .then((data) => {
        if (!isCurrent) {
          return;
        }

        const nextTopicsData = normalizeTopicsData(data, fallbackTopicsData);
        const isApiData = hasVisibleTopics(nextTopicsData)
          && nextTopicsData !== fallbackTopicsData;

        setTopicsData(nextTopicsData);
        setDataSourceLabel(isApiData ? 'API data' : 'Fallback data');
      })
      .catch(() => {
        if (isCurrent) {
          setTopicsData(fallbackTopicsData);
          setDataSourceLabel('Fallback data');
        }
      });

    fetchUserSettings().then((settings) => {
      if (!isCurrent) {
        return;
      }

      setUserSettings(settings);
      setSettingsSourceLabel(
        settings.source === 'localStorage'
          ? 'Local settings'
          : settings.persisted
            ? 'Saved settings'
            : 'Fallback settings',
      );
    });

    fetchFavorites().then((state) => {
      if (!isCurrent) {
        return;
      }

      setFavoritesState(state);
      setFavoritesSourceLabel(
        state.source === 'localStorage'
          ? 'Local favorites'
          : state.persisted
            ? 'Saved favorites'
            : 'Fallback favorites',
      );
    });

    return () => {
      isCurrent = false;
    };
  }, [allTopics, industryTopics, userKeywordTopics]);

  const displayedIndustryTopics = useMemo(() => {
    const keywords = [
      userSettings.industry,
      ...INDUSTRY_BASE_KEYWORDS,
    ].filter(Boolean);

    return topicsData.allTopics.filter((topic) => matchesKeywords(topic, keywords));
  }, [topicsData.allTopics, userSettings.industry]);
  const featuredIndustryTopics = useMemo(() => {
    return displayedIndustryTopics.length > 0
      ? displayedIndustryTopics
      : topicsData.allTopics;
  }, [displayedIndustryTopics, topicsData.allTopics]);

  const displayedUserKeywordTopics = useMemo(
    () =>
      topicsData.allTopics.filter((topic) =>
        matchesKeywords(topic, userSettings.keywords),
      ),
    [topicsData.allTopics, userSettings.keywords],
  );
  const displayedUserKeywordPreviewTopics = useMemo(
    () => displayedUserKeywordTopics.slice(0, 6),
    [displayedUserKeywordTopics],
  );
  const groupedAllTopics = useMemo(
    () => createPlatformTopicGroups(topicsData.allTopics, 3),
    [topicsData.allTopics],
  );
  const topRankingTopics = useMemo(
    () => topicsData.allTopics,
    [topicsData.allTopics],
  );

  const favoriteTopics = useMemo(
    () => topicsFromFavoriteIds(topicsData.allTopics, favoritesState.topicIds),
    [topicsData.allTopics, favoritesState.topicIds],
  );
  const overview = useMemo(
    () => createOverview(topicsData.allTopics),
    [topicsData.allTopics],
  );
  const platformDistribution = useMemo(
    () => createPlatformDistribution(topicsData.allTopics),
    [topicsData.allTopics],
  );
  const sourceStats = useMemo(
    () => createSourceStats(topicsData.allTopics),
    [topicsData.allTopics],
  );
  async function handleToggleFavorite(topic: DashboardTopic) {
    const isFavorite = favoritesState.topicIds.includes(topic.id);
    const nextState = isFavorite
      ? await removeFavorite(topic.id)
      : await addFavorite(topic.id);

    setFavoritesState(nextState);
    setFavoritesSourceLabel(
      nextState.source === 'localStorage'
        ? 'Local favorites'
        : nextState.persisted
          ? 'Saved favorites'
          : 'Fallback favorites',
    );
  }

  async function generateCopyForTopic(
    topic: DashboardTopic,
    tone: AiTone,
    angle: PostAngle,
  ): Promise<GeneratedCopy | null> {
    const analysis = await requestAiAnalysis(createAiInput(topic, tone, angle));

    return analysis.generatedCopies[0] ?? null;
  }

  async function handleGenerateCopy(
    topic: DashboardTopic,
    tone: AiTone,
    angle: PostAngle,
  ) {
    const nextCopy = await generateCopyForTopic(topic, tone, angle);

    if (!nextCopy) {
      return;
    }

    setCopyEditorState({ topic, copy: nextCopy, tone, angle });
  }

  function handleCloseTopicDetail() {
    setSelectedTopic(null);
    setCopyEditorState(null);
  }

  return (
    <>
      <section className="dashboard" aria-label="Dashboard">
        <div className="dashboard__header">
          <p className="page-section__eyebrow">
            Dashboard · {dataSourceLabel} · {settingsSourceLabel} ·{' '}
            {favoritesSourceLabel}
          </p>
          <h2>熱門話題 Dashboard</h2>
          <p className="dashboard__description">
            目前產業：{userSettings.industry}；自訂關鍵字：
            {userSettings.keywords.join('、') || '尚未設定'}；收藏：
            {favoritesState.topicIds.length}
          </p>
          <Link className="page__link" href="/settings">
            編輯使用者設定
          </Link>
        </div>

        <DashboardSection
          title="符合產業熱門話題"
          eyebrow="Industry Match"
          emptyTitle="尚無符合產業的熱門話題"
          emptyDescription="可至設定頁調整產業類別，或確認資料中是否包含相關關鍵字。"
          topics={featuredIndustryTopics.slice(0, 6)}
          favoriteTopicIds={favoritesState.topicIds}
          onOpenTopic={setSelectedTopic}
          onToggleFavorite={handleToggleFavorite}
        />

        <InspirationIdeasPanel topics={topicsData.allTopics} />

        <DashboardSection
          title="自訂關鍵字熱門話題"
          eyebrow="User Keywords"
          emptyTitle="尚無符合自訂關鍵字的熱門話題"
          emptyDescription="可至設定頁新增關鍵字，或檢查目前展示資料是否包含對應內容。"
          topics={displayedUserKeywordPreviewTopics}
          favoriteTopicIds={favoritesState.topicIds}
          onOpenTopic={setSelectedTopic}
          onToggleFavorite={handleToggleFavorite}
        />

        <div className="dashboard-two-column-layout">
          <SourceAnalysisPanel stats={sourceStats} />
          <FavoriteTopicsSection
            topics={favoriteTopics}
            favoriteTopicIds={favoritesState.topicIds}
            onOpenTopic={setSelectedTopic}
            onToggleFavorite={handleToggleFavorite}
          />
        </div>

        <section className="dashboard-section" aria-label="資料展示">
          <div className="page-section__header">
            <p className="page-section__eyebrow">Data Display</p>
            <h2>資料展示</h2>
          </div>

          <div className="dashboard-data-display">
            <DashboardStatusNotice
              dataSourceLabel={dataSourceLabel}
              settingsSourceLabel={settingsSourceLabel}
              favoritesSourceLabel={favoritesSourceLabel}
            />
            <TrendOverview
              overview={overview}
              favoriteCount={favoritesState.topicIds.length}
            />
            <TopTopicsRanking
              topics={topRankingTopics}
              favoriteTopicIds={favoritesState.topicIds}
              onOpenTopic={setSelectedTopic}
              onToggleFavorite={handleToggleFavorite}
            />
            <PlatformDistribution items={platformDistribution} />
          </div>
        </section>

        <GroupedTopicsSection
          title="所有熱門話題"
          eyebrow="All Topics"
          emptyTitle="尚無熱門話題"
          emptyDescription="請確認 mockData、JSON sample 或 API 是否已提供資料。"
          groups={groupedAllTopics}
          favoriteTopicIds={favoritesState.topicIds}
          onOpenTopic={setSelectedTopic}
          onToggleFavorite={handleToggleFavorite}
        />
      </section>

      {selectedTopic ? (
        <TopicDetailModal
          topic={selectedTopic}
          defaultTone={userSettings.tone}
          onGenerateCopy={handleGenerateCopy}
          onClose={handleCloseTopicDetail}
        />
      ) : null}
      {copyEditorState ? (
        <AiCopyEditorModal
          copy={copyEditorState.copy}
          topicTitle={copyEditorState.topic.topic}
          tone={copyEditorState.tone}
          angle={copyEditorState.angle}
          onRegenerate={async () => {
            const nextCopy = await generateCopyForTopic(
              copyEditorState.topic,
              copyEditorState.tone,
              copyEditorState.angle,
            );

            if (nextCopy) {
              setCopyEditorState((current) =>
                current
                  ? {
                      ...current,
                      copy: nextCopy,
                    }
                  : current,
              );
            }

            return nextCopy;
          }}
          onClose={() => setCopyEditorState(null)}
        />
      ) : null}
    </>
  );
}
