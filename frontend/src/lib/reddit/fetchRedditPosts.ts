export interface RedditPost {
  id: string;
  title: string;
  selftext?: string;
  subreddit: string;
  permalink: string;
  score: number;
  num_comments: number;
}

export interface RedditFetchResult {
  posts: RedditPost[];
  subreddit: string;
  isFallback: boolean;
  errorMessage?: string;
}

interface RedditListingChild {
  data: RedditPost;
}

interface RedditListingResponse {
  data: {
    children: RedditListingChild[];
  };
}

const REDDIT_SUBREDDIT = 'artificial';
const REDDIT_HOT_URL = `https://www.reddit.com/r/${REDDIT_SUBREDDIT}/hot.json?limit=10`;

const fallbackRedditPosts: RedditPost[] = [
  {
    id: 'fallback-ai-agents',
    title: 'AI agents are becoming more common in daily workflows',
    selftext:
      'People are discussing how AI agents can help summarize research, plan tasks, and automate repetitive work.',
    subreddit: 'artificial',
    permalink: '/r/artificial/comments/fallback_ai_agents/',
    score: 128,
    num_comments: 34,
  },
  {
    id: 'fallback-open-source-models',
    title: 'Open source AI models are getting more attention',
    selftext:
      'The community is comparing open source models with commercial AI tools for writing, coding, and research tasks.',
    subreddit: 'artificial',
    permalink: '/r/artificial/comments/fallback_open_source_models/',
    score: 96,
    num_comments: 21,
  },
  {
    id: 'fallback-ai-search',
    title: 'AI search tools may change how people browse the web',
    selftext:
      'Users are debating whether AI summaries can replace traditional search result pages for everyday questions.',
    subreddit: 'artificial',
    permalink: '/r/artificial/comments/fallback_ai_search/',
    score: 82,
    num_comments: 18,
  },
];

export async function fetchRedditPostsWithStatus(): Promise<RedditFetchResult> {
  try {
    const response = await fetch(REDDIT_HOT_URL, {
      headers: {
        Accept: 'application/json',
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36',
      },
      next: {
        revalidate: 300,
      },
    });

    if (!response.ok) {
      return {
        posts: fallbackRedditPosts,
        subreddit: REDDIT_SUBREDDIT,
        isFallback: true,
        errorMessage: `Reddit 公開 JSON 目前回傳 ${response.status}，暫時使用備援展示資料。`,
      };
    }

    const data = (await response.json()) as RedditListingResponse;

    return {
      posts: data.data.children.map((child) => child.data),
      subreddit: REDDIT_SUBREDDIT,
      isFallback: false,
    };
  } catch {
    return {
      posts: fallbackRedditPosts,
      subreddit: REDDIT_SUBREDDIT,
      isFallback: true,
      errorMessage: 'Reddit 公開 JSON 目前無法連線，暫時使用備援展示資料。',
    };
  }
}

export async function fetchRedditPosts(): Promise<RedditPost[]> {
  const result = await fetchRedditPostsWithStatus();

  return result.posts;
}
