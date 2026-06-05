import type { ContentItem } from '../../types/content';
import type { RedditPost } from './fetchRedditPosts';

function createFallbackContent(post: RedditPost): string {
  return `這篇 Reddit 討論目前有 ${post.score} 分、${post.num_comments} 則留言。原文：https://www.reddit.com${post.permalink}`;
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
    industryTags: ['科技業'],
    keywords: ['AI', 'Reddit', post.subreddit],
  };
}
