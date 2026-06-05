import {
  DEFAULT_FAVORITES_STATE,
  type FavoritesState,
} from '../../types/favorites';

const STORAGE_KEY = 'trend-radar-favorites';

export function normalizeFavoritesState(value: unknown): FavoritesState {
  if (!value || typeof value !== 'object') {
    return DEFAULT_FAVORITES_STATE;
  }

  const state = value as Partial<FavoritesState>;
  const topicIds = Array.isArray(state.topicIds)
    ? state.topicIds
        .filter((item): item is string => typeof item === 'string')
        .map((item) => item.trim())
        .filter(Boolean)
    : [];

  return {
    topicIds: Array.from(new Set(topicIds)),
    source: state.source ?? DEFAULT_FAVORITES_STATE.source,
    persisted: Boolean(state.persisted),
  };
}

export function loadFavoritesFromStorage(): FavoritesState {
  if (typeof window === 'undefined') {
    return DEFAULT_FAVORITES_STATE;
  }

  const rawValue = window.localStorage.getItem(STORAGE_KEY);

  if (!rawValue) {
    return DEFAULT_FAVORITES_STATE;
  }

  try {
    return {
      ...normalizeFavoritesState(JSON.parse(rawValue)),
      source: 'localStorage',
      persisted: true,
    };
  } catch {
    return DEFAULT_FAVORITES_STATE;
  }
}

export function saveFavoritesToStorage(topicIds: string[]): FavoritesState {
  const state = normalizeFavoritesState({
    topicIds,
    source: 'localStorage',
    persisted: true,
  });

  if (typeof window !== 'undefined') {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ topicIds: state.topicIds }),
    );
  }

  return state;
}
