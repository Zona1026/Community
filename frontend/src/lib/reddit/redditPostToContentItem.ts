import type { ContentItem } from '../../types/content';
import type { RedditPost } from './fetchRedditPosts';

function createFallbackContent(post: RedditPost): string {
  return `This Reddit discussion has ${post.score} score and ${post.num_comments} comments. Original post: https://www.reddit.com${post.permalink}`;
}

export function redditPostToContentItem(post: RedditPost): ContentItem {
  const originalUrl = `https://www.reddit.com${post.permalink}`;

  return {
    id: `reddit-${post.id}`,
    platform: `Reddit r/${post.subreddit}`,
    title: post.title,
    content: post.selftext?.trim() || createFallbackContent(post),
    url: originalUrl,
    likeCount: post.score,
    commentCount: post.num_comments,
    hotTags: ['Reddit 熱門討論'],
    createdAt: new Date().toISOString(),
    importedAt: new Date().toISOString(),
    industryTags: ['科技業', 'AI 社群'],
    keywords: ['AI', 'Reddit', post.subreddit],
  };
}
