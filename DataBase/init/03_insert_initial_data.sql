-- ============================================================
-- SYNEX+ Quotation System - Initial Data
-- ============================================================

-- ============================================================
-- Category 초기 데이터
-- ============================================================
INSERT INTO category (major, minor) VALUES
-- 판넬
('판넬', '전면판넬'),
('판넬', '측면판넬'),
('판넬', '후면판넬'),
('판넬', '도어판넬'),

-- 명판
('명판', '메탈명판'),
('명판', '라벨명판'),
('명판', '에칭명판'),

-- 잡재료 및 케이블
('잡재료 및 케이블', '열수축 튜브'),
('잡재료 및 케이블', '전선'),
('잡재료 및 케이블', '케이블 타이'),
('잡재료 및 케이블', '단자대'),
('잡재료 및 케이블', '절연 테이프'),

-- 인건비
('인건비', '설치비'),
('인건비', '검수비'),
('인건비', '시운전비');

-- ============================================================
-- Maker 샘플 데이터
-- ============================================================
INSERT INTO maker (id, name) VALUES
('J012', 'LS ELECTRIC'),
('K999', 'SAMPLE MAKER');

-- ============================================================
-- Resources 샘플 데이터
-- ============================================================
INSERT INTO resources (id, maker_id, category_id, name, unit, solo_price) VALUES
('000001', 'J012',
    (SELECT id FROM category WHERE major = '잡재료 및 케이블' AND minor = '열수축 튜브' LIMIT 1),
    'LCP-32FM 15A WA', 'ea', 22000),
    
('000002', 'J012',
    (SELECT id FROM category WHERE major = '판넬' AND minor = '전면판넬' LIMIT 1),
    'AD-4212C-6000', 'ea', 3200000);

-- ============================================================
-- Certification 샘플 데이터
-- ============================================================
INSERT INTO certification (resources_id, maker_id, ul, ce, kc, etc) VALUES
('000001', 'J012', TRUE, FALSE, FALSE, 'RoHS'),
('000002', 'J012', FALSE, TRUE, TRUE, NULL);

-- ============================================================
-- Verify Data
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'SYNEX+ Database Initialization Complete';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Categories: %', (SELECT COUNT(*) FROM category);
    RAISE NOTICE 'Makers: %', (SELECT COUNT(*) FROM maker);
    RAISE NOTICE 'Resources: %', (SELECT COUNT(*) FROM resources);
    RAISE NOTICE 'Certifications: %', (SELECT COUNT(*) FROM certification);
    RAISE NOTICE '==============================================';
END $$;