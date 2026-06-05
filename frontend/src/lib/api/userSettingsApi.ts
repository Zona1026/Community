import type { UserSettings } from '../../types/userSettings';
import { DEFAULT_USER_SETTINGS } from '../../types/userSettings';
import {
  loadUserSettingsFromStorage,
  normalizeUserSettings,
  saveUserSettingsToStorage,
} from '../settings/userSettingsStorage';

export async function fetchUserSettings(): Promise<UserSettings> {
  try {
    const response = await fetch('/api/user-settings', {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`User settings API failed with ${response.status}.`);
    }

    const settings = normalizeUserSettings(await response.json());
    const storedSettings = loadUserSettingsFromStorage();
    const nextSettings = settings.persisted ? settings : storedSettings;

    return nextSettings.keywords.length > 0
      ? nextSettings
      : DEFAULT_USER_SETTINGS;
  } catch {
    return loadUserSettingsFromStorage();
  }
}

export async function saveUserSettings(
  settings: UserSettings,
): Promise<UserSettings> {
  const normalizedSettings = normalizeUserSettings(settings);
  saveUserSettingsToStorage(normalizedSettings);

  try {
    const response = await fetch('/api/user-settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(normalizedSettings),
    });

    if (!response.ok) {
      throw new Error(`User settings API failed with ${response.status}.`);
    }

    const savedSettings = normalizeUserSettings(await response.json());
    saveUserSettingsToStorage(savedSettings);

    return savedSettings;
  } catch {
    return {
      ...normalizedSettings,
      source: 'localStorage',
      persisted: true,
    };
  }
}
