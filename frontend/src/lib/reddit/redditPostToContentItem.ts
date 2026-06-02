import type { ContentItem } from '../../types/content';
import type { RedditPost } from './fetchRedditPosts';

function createFallbackContent(post: RedditPost): string {
  return `這篇 Reddit 討論目前有 ${post.score} 分、${post.num_comments} 則留言。原文：https://www.reddit.com${post.permalink}`;
}

export function redditPostToContentItem(post: RedditPost): ContentItem {
  return {
    id: `reddit-${post.id}`,
    title: post.title,
    content: post.selftext?.trim() || createFallbackContent(post),
    source: `Reddit r/${post.subreddit}`,
  };
}
