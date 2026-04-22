-- ============================================================
-- IXOVA Database Schema
-- Compatible with: SQLite (default) / PostgreSQL / MySQL
-- ============================================================

-- Auth User (Django built-in, shown for reference)
CREATE TABLE IF NOT EXISTS auth_user (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(150) NOT NULL UNIQUE,
    email         VARCHAR(254) NOT NULL,
    password      VARCHAR(128) NOT NULL,
    first_name    VARCHAR(150) NOT NULL DEFAULT '',
    last_name     VARCHAR(150) NOT NULL DEFAULT '',
    is_active     BOOLEAN NOT NULL DEFAULT 1,
    is_staff      BOOLEAN NOT NULL DEFAULT 0,
    is_superuser  BOOLEAN NOT NULL DEFAULT 0,
    date_joined   DATETIME NOT NULL,
    last_login    DATETIME
);

-- Profile
CREATE TABLE IF NOT EXISTS core_profile (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    avatar         VARCHAR(100),
    bio            TEXT NOT NULL DEFAULT '',
    skills         VARCHAR(500) NOT NULL DEFAULT '',
    ai_score       INTEGER NOT NULL DEFAULT 0,
    profile_views  INTEGER NOT NULL DEFAULT 0
);

-- Course
CREATE TABLE IF NOT EXISTS core_course (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        VARCHAR(200) NOT NULL,
    description  TEXT NOT NULL,
    category     VARCHAR(20) NOT NULL CHECK(category IN ('tech', 'business', 'freelancing')),
    duration     VARCHAR(50) NOT NULL,
    thumbnail    VARCHAR(100),
    is_premium   BOOLEAN NOT NULL DEFAULT 0,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Opportunity
CREATE TABLE IF NOT EXISTS core_opportunity (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        VARCHAR(200) NOT NULL,
    company      VARCHAR(100) NOT NULL,
    description  TEXT NOT NULL,
    type         VARCHAR(20) NOT NULL CHECK(type IN ('internship', 'freelance', 'gig')),
    category     VARCHAR(100) NOT NULL,
    stipend      VARCHAR(50) NOT NULL DEFAULT '',
    deadline     DATE,
    is_trending  BOOLEAN NOT NULL DEFAULT 0,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Application
CREATE TABLE IF NOT EXISTS core_application (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    opportunity_id INTEGER NOT NULL REFERENCES core_opportunity(id) ON DELETE CASCADE,
    status         VARCHAR(20) NOT NULL DEFAULT 'applied'
                   CHECK(status IN ('applied', 'reviewing', 'interview', 'accepted', 'rejected')),
    applied_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, opportunity_id)
);

-- Saved Opportunity
CREATE TABLE IF NOT EXISTS core_savedopportunity (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    opportunity_id INTEGER NOT NULL REFERENCES core_opportunity(id) ON DELETE CASCADE,
    saved_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, opportunity_id)
);

-- Sub-Admin
CREATE TABLE IF NOT EXISTS core_subadmin (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                   INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    assigned_by_id            INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    role                      VARCHAR(20) NOT NULL CHECK(role IN ('content', 'support', 'moderator')),
    can_manage_users          BOOLEAN NOT NULL DEFAULT 0,
    can_manage_opportunities  BOOLEAN NOT NULL DEFAULT 0,
    can_manage_courses        BOOLEAN NOT NULL DEFAULT 0,
    can_manage_applications   BOOLEAN NOT NULL DEFAULT 0,
    is_active                 BOOLEAN NOT NULL DEFAULT 1,
    created_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_application_user        ON core_application(user_id);
CREATE INDEX IF NOT EXISTS idx_application_opportunity ON core_application(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_saved_user              ON core_savedopportunity(user_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_trending    ON core_opportunity(is_trending);
CREATE INDEX IF NOT EXISTS idx_subadmin_user           ON core_subadmin(user_id);
CREATE INDEX IF NOT EXISTS idx_subadmin_active         ON core_subadmin(is_active);
