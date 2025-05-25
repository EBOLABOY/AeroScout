-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    api_call_count_today INTEGER NOT NULL DEFAULT 0,
    last_api_call_date TIMESTAMP
);

-- 创建 invitation_codes 表
CREATE TABLE IF NOT EXISTS invitation_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT 0,
    created_by_user_id INTEGER,
    used_by_user_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    FOREIGN KEY (created_by_user_id) REFERENCES users (id),
    FOREIGN KEY (used_by_user_id) REFERENCES users (id)
);

-- 创建 locations 表
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    trip_type TEXT,
    mode TEXT,
    raw_data TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建 airports 表
CREATE TABLE IF NOT EXISTS airports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    iata_code TEXT UNIQUE NOT NULL,
    icao_code TEXT UNIQUE,
    city TEXT,
    country TEXT,
    latitude REAL,
    longitude REAL,
    data_source TEXT,
    raw_data TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建 potential_hubs 表
CREATE TABLE IF NOT EXISTS potential_hubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    iata_code TEXT UNIQUE NOT NULL,
    city TEXT,
    country TEXT,
    country_code TEXT,
    region TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    source TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_invitation_codes_code ON invitation_codes (code);
CREATE INDEX IF NOT EXISTS idx_locations_query ON locations (query);
CREATE INDEX IF NOT EXISTS idx_airports_iata_code ON airports (iata_code);
CREATE INDEX IF NOT EXISTS idx_airports_icao_code ON airports (icao_code);
CREATE INDEX IF NOT EXISTS idx_potential_hubs_iata_code ON potential_hubs (iata_code);
CREATE INDEX IF NOT EXISTS idx_potential_hubs_country_code ON potential_hubs (country_code);
CREATE INDEX IF NOT EXISTS idx_potential_hubs_region ON potential_hubs (region);
