export interface FavoritesState {
  topicIds: string[];
  source?: 'api' | 'db' | 'fallback' | 'localStorage';
  persisted?: boolean;
}

export const DEFAULT_FAVORITES_STATE: FavoritesState = {
  topicIds: [],
  source: 'fallback',
  persisted: false,
};
