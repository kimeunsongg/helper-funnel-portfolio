-- 전체 퍼널 (지원 → 응답 → 확정 → 출근)
-- 실행: .venv/bin/python scripts/q.py sql/analysis/01_funnel.sql
--
-- 분석 단위: 지원 슬롯 = 사람 × 캠프 × 조 × 날짜. 중복 지원은 한 슬롯으로 합친다.
-- 출근은 attendance를 지원 건 단위로 먼저 줄인 뒤(DISTINCT) 붙여서 중복 스캔을 막는다.
-- 전환율의 분모는 바로 앞 단계.

WITH attended AS (
    SELECT DISTINCT application_id FROM attendance
),
slots AS (
    SELECT applicant_id, camp_id, shift, work_date,
           BOOL_OR(p.responded_at IS NOT NULL)   AS responded,
           BOOL_OR(p.confirmed_at IS NOT NULL)   AS confirmed,
           BOOL_OR(a.application_id IS NOT NULL) AS attended
    FROM applications p
    LEFT JOIN attended a USING (application_id)
    GROUP BY ALL
)
SELECT COUNT(*)                          AS applied,
       COUNT(*) FILTER (WHERE responded) AS responded,
       COUNT(*) FILTER (WHERE confirmed) AS confirmed,
       COUNT(*) FILTER (WHERE attended)  AS attended,
       ROUND(COUNT(*) FILTER (WHERE responded) / COUNT(*), 3)                          AS response_rate,
       ROUND(COUNT(*) FILTER (WHERE confirmed) / COUNT(*) FILTER (WHERE responded), 3) AS confirm_rate,
       ROUND(COUNT(*) FILTER (WHERE attended)  / COUNT(*) FILTER (WHERE confirmed), 3) AS attend_rate
FROM slots;
