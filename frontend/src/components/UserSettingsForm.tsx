'use client';

import { FormEvent, useEffect, useState } from 'react';
import {
  fetchUserSettings,
  saveUserSettings,
} from '../lib/api/userSettingsApi';
import { DEFAULT_USER_SETTINGS, USER_SETTING_TONES } from '../types/userSettings';
import type { UserSettings } from '../types/userSettings';

function keywordsToText(keywords: string[]): string {
  return keywords.join(', ');
}

function textToKeywords(value: string): string[] {
  return Array.from(
    new Set(
      value
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
    ),
  );
}

export function UserSettingsForm() {
  const [settings, setSettings] = useState<UserSettings>(DEFAULT_USER_SETTINGS);
  const [keywordText, setKeywordText] = useState(
    keywordsToText(DEFAULT_USER_SETTINGS.keywords),
  );
  const [status, setStatus] = useState('讀取設定中');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    fetchUserSettings().then((nextSettings) => {
      if (!isCurrent) {
        return;
      }

      setSettings(nextSettings);
      setKeywordText(keywordsToText(nextSettings.keywords));
      setStatus(
        nextSettings.persisted
          ? '已載入保存設定'
          : '使用 Demo fallback 設定',
      );
    });

    return () => {
      isCurrent = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setStatus('儲存中');

    const nextSettings = await saveUserSettings({
      ...settings,
      keywords: textToKeywords(keywordText),
    });

    setSettings(nextSettings);
    setKeywordText(keywordsToText(nextSettings.keywords));
    setStatus(
      nextSettings.persisted
        ? '設定已保存'
        : 'API 未連線，已保留在前端 fallback',
    );
    setIsSaving(false);
  }

  return (
    <form className="settings-form" onSubmit={handleSubmit}>
      <label className="settings-form__field" htmlFor="industry">
        <span>產業類別</span>
        <input
          id="industry"
          type="text"
          value={settings.industry}
          onChange={(event) =>
            setSettings((current) => ({
              ...current,
              industry: event.target.value,
            }))
          }
        />
      </label>

      <label className="settings-form__field" htmlFor="tone">
        <span>常用語氣</span>
        <select
          id="tone"
          value={settings.tone}
          onChange={(event) =>
            setSettings((current) => ({
              ...current,
              tone: event.target.value as UserSettings['tone'],
            }))
          }
        >
          {USER_SETTING_TONES.map((tone) => (
            <option key={tone} value={tone}>
              {tone}
            </option>
          ))}
        </select>
      </label>

      <label className="settings-form__field" htmlFor="keywords">
        <span>自訂關鍵字</span>
        <textarea
          id="keywords"
          rows={4}
          value={keywordText}
          onChange={(event) => setKeywordText(event.target.value)}
        />
      </label>

      <div className="settings-form__actions">
        <button type="submit" disabled={isSaving}>
          {isSaving ? '儲存中' : '儲存設定'}
        </button>
        <p>{status}</p>
      </div>
    </form>
  );
}
