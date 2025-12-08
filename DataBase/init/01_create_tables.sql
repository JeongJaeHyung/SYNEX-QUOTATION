-- ============================================================
-- SYNEX+ Quotation System - Database Schema
-- ============================================================

SET TIME ZONE 'Asia/Seoul';

-- ============================================================
-- 1. category (카테고리 마스터)
-- ============================================================
CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    major VARCHAR(50) NOT NULL,
    minor VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_category_major_minor UNIQUE (major, minor)
);

-- ============================================================
-- 2. maker (제조사)
-- ============================================================
CREATE TABLE maker (
    id VARCHAR(4) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. resources (제품/자원)
-- ============================================================
CREATE TABLE resources (
    id VARCHAR(6) NOT NULL,
    maker_id VARCHAR(4) NOT NULL,
    category_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    solo_price INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, maker_id),
    FOREIGN KEY (maker_id) REFERENCES maker(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);

-- ============================================================
-- 4. certification (인증 정보)
-- ============================================================
CREATE TABLE certification (
    id SERIAL PRIMARY KEY,
    resources_id VARCHAR(6) NOT NULL,
    maker_id VARCHAR(4) NOT NULL,
    ul BOOLEAN NOT NULL DEFAULT FALSE,
    ce BOOLEAN NOT NULL DEFAULT FALSE,
    kc BOOLEAN NOT NULL DEFAULT FALSE,
    etc TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (resources_id, maker_id) 
        REFERENCES resources(id, maker_id),
    CONSTRAINT uk_cert_resource UNIQUE (resources_id, maker_id)
);

-- ============================================================
-- 5. Updated At Trigger Function
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_category_updated_at
    BEFORE UPDATE ON category
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maker_updated_at
    BEFORE UPDATE ON maker
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resources_updated_at
    BEFORE UPDATE ON resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certification_updated_at
    BEFORE UPDATE ON certification
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();