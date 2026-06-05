import type { NormalizedContent } from '../types/normalizedContent';

interface ContentCardProps {
  item: NormalizedContent;
}

export function ContentCard({ item }: ContentCardProps) {
  return (
    <article className="content-card">
      <div className="content-card__source">{item.sourcePlatform}</div>
      <h2>{item.topicTitle}</h2>
      <p>{item.normalizedText}</p>
    </article>
  );
}
