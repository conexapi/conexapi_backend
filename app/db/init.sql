CREATE TABLE oauth_tokens (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,                          -- ID de usuario de MercadoLibre
    platform VARCHAR(50) NOT NULL,                    -- Nombre de la plataforma, por si luego agregamos otras (ej: 'mercadolibre')
    access_token TEXT NOT NULL,
    token_type VARCHAR(50),
    expires_in INTEGER,
    scope TEXT,
    refresh_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id,platform)
);