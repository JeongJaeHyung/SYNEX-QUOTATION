-- ============================================================
-- SYNEX+ Quotation System - Indexes
-- ============================================================

-- category 인덱스
CREATE INDEX idx_category_major ON category(major);

-- maker 인덱스
CREATE INDEX idx_maker_name ON maker(name);

-- resources 인덱스
CREATE INDEX idx_resources_category ON resources(category_id);
CREATE INDEX idx_resources_name ON resources(name);

-- certification 인덱스
CREATE INDEX idx_cert_resource ON certification(resources_id, maker_id);