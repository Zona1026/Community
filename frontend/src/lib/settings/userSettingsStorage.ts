import {
  DEFAULT_USER_SETTINGS,
  USER_SETTING_TONES,
  type UserSettings,
} from '../../types/userSettings';

const STORAGE_KEY = 'trend-radar-user-settings';

function normalizeKeywords(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return DEFAULT_USER_SETTINGS.keywords;
  }

  const keywords = value
    .filter((item): item is string => typeof item === 'string')
    .map((item) => item.trim())
    .filter(Boolean);

  return keywords.length > 0 ? Array.from(new Set(keywords)) : [];
}

export function normalizeUserSettings(value: unknown): UserSettings {
  if (!value || typeof value !== 'object') {
    return DEFAULT_USER_SETTINGS;
  }

  const settings = value as Partial<UserSettings>;
  const tone = USER_SETTING_TONES.includes(settings.tone ?? '專業')
    ? settings.tone ?? '專業'
    : '專業';

  return {
    industry:
      typeof settings.industry === 'string' && settings.industry.trim()
        ? settings.industry.trim()
        : DEFAULT_USER_SETTINGS.industry,
    tone,
    keywords: normalizeKeywords(settings.keywords),
    source: settings.source ?? DEFAULT_USER_SETTINGS.source,
    persisted: Boolean(settings.persisted),
  };
}

export function loadUserSettingsFromStorage(): UserSettings {
  if (typeof window === 'undefined') {
    return DEFAULT_USER_SETTINGS;
  }

  const rawValue = window.localStorage.getItem(STORAGE_KEY);

  if (!rawValue) {
    return DEFAULT_USER_SETTINGS;
  }

  try {
    return {
      ...normalizeUserSettings(JSON.parse(rawValue)),
      source: 'localStorage',
      persisted: true,
    };
  } catch {
    return DEFAULT_USER_SETTINGS;
  }
}

export function saveUserSettingsToStorage(settings: UserSettings): void {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      industry: settings.industry,
      tone: settings.tone,
      keywords: settings.keywords,
    }),
  );
}
