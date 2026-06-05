export interface ContentItem {
  id: string;
  platform: string;
  title: string;
  content: string;
  url: string;
  likeCount: number;
  commentCount: number;
  hotTags: string[];
  createdAt: string;
  importedAt: string;
  industryTags: string[];
  keywords: string[];
}
