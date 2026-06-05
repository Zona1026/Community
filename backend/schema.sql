CREATE TABLE IF NOT EXISTS topics (
    id BIGSERIAL PRIMARY KEY,
    topic_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
    id BIGSERIAL PRIMARY KEY,
    user_key TEXT NOT NULL UNIQUE,
    industry TEXT NOT NULL DEFAULT '',
    tone TEXT NOT NULL DEFAULT '專業',
    keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generated_copies (
    id BIGSERIAL PRIMARY KEY,
    topic_id BIGINT REFERENCES topics(id) ON DELETE CASCADE,
    tone TEXT NOT NULL,
    angle TEXT NOT NULL,
    content TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'mock',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS favorites (
    id BIGSERIAL PRIMARY KEY,
    user_key TEXT NOT NULL DEFAULT 'default-user',
    topic_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_key, topic_id)
);
