import type { FavoritesState } from '../../types/favorites';
import {
  loadFavoritesFromStorage,
  normalizeFavoritesState,
  saveFavoritesToStorage,
} from '../favorites/favoritesStorage';

export async function fetchFavorites(): Promise<FavoritesState> {
  try {
    const response = await fetch('/api/favorites', {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Favorites API failed with ${response.status}.`);
    }

    const state = normalizeFavoritesState(await response.json());
    const storedState = loadFavoritesFromStorage();

    return state.persisted ? state : storedState;
  } catch {
    return loadFavoritesFromStorage();
  }
}

export async function addFavorite(topicId: string): Promise<FavoritesState> {
  const currentState = loadFavoritesFromStorage();
  const optimisticState = saveFavoritesToStorage([
    topicId,
    ...currentState.topicIds,
  ]);

  try {
    const response = await fetch(`/api/favorites/${encodeURIComponent(topicId)}`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Favorites API failed with ${response.status}.`);
    }

    const state = normalizeFavoritesState(await response.json());

    return state.persisted ? state : optimisticState;
  } catch {
    return optimisticState;
  }
}

export async function removeFavorite(topicId: string): Promise<FavoritesState> {
  const currentState = loadFavoritesFromStorage();
  const optimisticState = saveFavoritesToStorage(
    currentState.topicIds.filter((item) => item !== topicId),
  );

  try {
    const response = await fetch(`/api/favorites/${encodeURIComponent(topicId)}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Favorites API failed with ${response.status}.`);
    }

    const state = normalizeFavoritesState(await response.json());

    return state.persisted ? state : optimisticState;
  } catch {
    return optimisticState;
  }
}
