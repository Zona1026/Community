import type { DashboardTopic } from '../../components/TopicDashboard';

export interface TopicsApiResponse {
  allTopics: DashboardTopic[];
  industryTopics: DashboardTopic[];
  userKeywordTopics: DashboardTopic[];
  source?: string;
}

export async function fetchDashboardTopics(): Promise<TopicsApiResponse> {
  const response = await fetch('/api/topics', {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Topics API failed with ${response.status}.`);
  }

  return (await response.json()) as TopicsApiResponse;
}

export async function fetchTopicById(id: string): Promise<DashboardTopic> {
  const response = await fetch(`/api/topics/${encodeURIComponent(id)}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Topic API failed with ${response.status}.`);
  }

  return (await response.json()) as DashboardTopic;
}
