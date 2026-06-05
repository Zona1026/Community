import type { ContentItem } from '../types/content';

export const mockData: ContentItem[] = [
  {
    id: 'ai-search',
    platform: 'Threads',
    title: 'AI 搜尋正在改變使用者找資料的方式',
    content:
      '越來越多人開始用 AI 助理整理搜尋結果，不只查關鍵字，也期待直接得到摘要、比較與下一步建議。',
    url: 'https://example.com/threads/ai-search',
    likeCount: 4200,
    commentCount: 680,
    hotTags: ['最多人討論', '按讚數最高'],
    createdAt: '2026-05-31T08:10:00+08:00',
    importedAt: '2026-06-01T09:00:00+08:00',
    industryTags: ['科技業', '教育業', '行銷顧問'],
    keywords: ['AI', 'AI 搜尋', 'SEO', '內容策略'],
  },
  {
    id: 'ai-video-tools',
    platform: 'Dcard',
    title: 'AI 影音工具讓短影音製作門檻降低',
    content:
      '創作者討論用 AI 生成腳本、字幕與分鏡，讓小團隊也能快速測試不同內容題材。',
    url: 'https://example.com/dcard/ai-video-tools',
    likeCount: 2600,
    commentCount: 410,
    hotTags: ['留言數最多', '創作者熱議'],
    createdAt: '2026-05-31T12:20:00+08:00',
    importedAt: '2026-06-01T09:00:00+08:00',
    industryTags: ['科技業', '自媒體', '行銷顧問'],
    keywords: ['AI', '短影音', '影音工具', '創作者'],
  },
  {
    id: 'ai-workflow',
    platform: 'Threads',
    title: 'AI 工作流成為知識工作者的新習慣',
    content:
      '許多人開始分享自己的 AI 工作流，像是會議摘要、資料整理、企劃草稿與社群內容發想。',
    url: 'https://example.com/threads/ai-workflow',
    likeCount: 3100,
    commentCount: 520,
    hotTags: ['最多人討論', '工作效率'],
    createdAt: '2026-05-30T18:40:00+08:00',
    importedAt: '2026-06-01T09:00:00+08:00',
    industryTags: ['科技業', '教育業', '行銷顧問'],
    keywords: ['AI', '工作流', '效率', '企劃'],
  },
];
