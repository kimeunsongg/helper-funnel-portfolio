-- 웰컴 메시지 지연과 응답률
-- 실행: .venv/bin/python scripts/q.py sql/analysis/02_welcome_delay.sql
--
-- 지연 기준: 지원 후 20분 초과 (채용 안내의 발송 기준).
-- 같은 슬롯 중복 지원은 첫 지원만 남긴다.

-- 1) 20분 이내 vs 초과 응답률
WITH apps AS (
    SELECT * FROM applications
    QUALIFY ROW_NUMBER() OVER (PARTITION BY applicant_id, camp_id, shift, work_date ORDER BY applied_at) = 1
)
SELECT CASE WHEN date_diff('minute', applied_at, welcome_sent_at) > 20
            THEN '늦음 (20분 초과)' ELSE '제때 (20분 이내)' END AS welcome,
       COUNT(*)                                  AS apps,
       COUNT(responded_at)                       AS responded,
       ROUND(COUNT(responded_at) / COUNT(*), 3)  AS response_rate
FROM apps
GROUP BY 1
ORDER BY 1;

-- 2) 근무 요일별 지연 비율 (월요일 근무분에 지연이 몰리는지)
WITH apps AS (
    SELECT * FROM applications
    QUALIFY ROW_NUMBER() OVER (PARTITION BY applicant_id, camp_id, shift, work_date ORDER BY applied_at) = 1
)
SELECT dayname(work_date) AS work_day,
       isodow(work_date)  AS n,
       COUNT(*)           AS apps,
       ROUND(AVG((date_diff('minute', applied_at, welcome_sent_at) > 20)::INT), 3) AS late_rate
FROM apps
GROUP BY ALL
ORDER BY n;
