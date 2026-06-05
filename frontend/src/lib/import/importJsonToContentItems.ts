import type { ContentItem } from '../../types/content';

type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function getString(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function getNumber(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0
    ? value
    : 0;
}

function getStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => getString(item))
    .filter((item): item is string => Boolean(item));
}

function getImportedRows(jsonData: unknown): unknown[] {
  if (Array.isArray(jsonData)) {
    return jsonData;
  }

  if (isRecord(jsonData) && Array.isArray(jsonData.items)) {
    return jsonData.items;
  }

  return [];
}

function toContentItem(row: unknown): ContentItem | undefined {
  if (!isRecord(row)) {
    return undefined;
  }

  const id = getString(row.id);
  const platform = getString(row.platform);
  const title = getString(row.title);
  const content = getString(row.content);

  if (!id || !platform || !title || !content) {
    return undefined;
  }

  return {
    id,
    platform,
    title,
    content,
    url: getString(row.url) ?? '',
    likeCount: getNumber(row.likeCount),
    commentCount: getNumber(row.commentCount),
    hotTags: getStringArray(row.hotTags),
    createdAt: getString(row.createdAt) ?? new Date(0).toISOString(),
    importedAt: getString(row.importedAt) ?? new Date().toISOString(),
    industryTags: getStringArray(row.industryTags),
    keywords: getStringArray(row.keywords),
  };
}

export function importJsonToContentItems(jsonData: unknown): ContentItem[] {
  return getImportedRows(jsonData)
    .map(toContentItem)
    .filter((item): item is ContentItem => Boolean(item));
}
