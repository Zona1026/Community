import type { NormalizedContent } from '../types/normalizedContent';

interface ContentCardProps {
  item: NormalizedContent;
}

export function ContentCard({ item }: ContentCardProps) {
  const platform = item.sourcePlatform || '未知平台';
  const title = item.topicTitle || '未命名話題';
  const text = item.normalizedText || '此筆資料尚無可展示的摘要。';
  const hotScore = Number.isFinite(item.hotScore) ? item.hotScore : 0;

  return (
    <article className="content-card">
      <div className="content-card__header">
        <div className="content-card__source">{platform}</div>
        <div className="content-card__score">熱門分數 {hotScore}</div>
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
      {item.hotTags.length > 0 ? (
        <div className="content-card__tags" aria-label="熱門標籤">
          {item.hotTags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : null}
    </article>
  );
}
