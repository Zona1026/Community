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

export const fallbackRedditPosts: RedditPost[] = [
  {
    id: 'fallback-ai-agents',
    title: 'AI agents are becoming more common in daily workflows',
    selftext:
      'People are discussing how AI agents can summarize research, plan tasks, and automate repetitive work.',
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

function shouldUseLiveReddit(): boolean {
  return process.env.USE_REDDIT_LIVE === 'true';
}

function createFallbackResult(errorMessage?: string): RedditFetchResult {
  return {
    posts: fallbackRedditPosts,
    subreddit: REDDIT_SUBREDDIT,
    isFallback: true,
    errorMessage:
      errorMessage ??
      'Reddit live fetch is disabled for Demo stability. Using fixed fallback data.',
  };
}

export async function fetchRedditPostsWithStatus(): Promise<RedditFetchResult> {
  if (!shouldUseLiveReddit()) {
    return createFallbackResult();
  }

  try {
    const response = await fetch(REDDIT_HOT_URL, {
      headers: {
        Accept: 'application/json',
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TrendRadarDemo/1.0',
      },
      next: {
        revalidate: 300,
      },
    });

    if (!response.ok) {
      return createFallbackResult(
        `Reddit public JSON returned ${response.status}. Using fallback data.`,
      );
    }

    const data = (await response.json()) as RedditListingResponse;
    const posts = data.data.children
      .map((child) => child.data)
      .filter((post) => post.id && post.title);

    if (posts.length === 0) {
      return createFallbackResult(
        'Reddit public JSON returned no usable posts. Using fallback data.',
      );
    }

    return {
      posts,
      subreddit: REDDIT_SUBREDDIT,
      isFallback: false,
    };
  } catch {
    return createFallbackResult(
      'Reddit public JSON is unavailable. Using fallback data.',
    );
  }
}

export async function fetchRedditPosts(): Promise<RedditPost[]> {
  const result = await fetchRedditPostsWithStatus();

  return result.posts;
}
