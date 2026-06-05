import type { AiTone } from './aiAnalysis';

export interface UserSettings {
  industry: string;
  tone: AiTone;
  keywords: string[];
  source?: 'api' | 'db' | 'fallback' | 'localStorage';
  persisted?: boolean;
}

export const DEFAULT_USER_SETTINGS: UserSettings = {
  industry: 'AI',
  tone: '專業',
  keywords: ['AI', '創業'],
  source: 'fallback',
  persisted: false,
};

export const USER_SETTING_TONES: AiTone[] = ['專業', '輕鬆', '犀利'];
