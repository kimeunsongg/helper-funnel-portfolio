-- 캠프별 14일 내 재출근율
-- 분모: 첫 출근한 사람 (첫 출근일이 9/27 이전 → 14일을 끝까지 관찰 가능)
-- 분자: 그중 첫 출근 다음 날부터 14일 안에 한 번 더 출근한 사람

WITH att AS (
    SELECT DISTINCT p.applicant_id, p.camp_id, p.work_date
    FROM attendance t
    JOIN applications p USING (application_id)
),
first_att AS (
    SELECT applicant_id,
           MIN(work_date)               AS first_date,
           arg_min(camp_id, work_date)  AS first_camp
    FROM att
    GROUP BY applicant_id
),
flagged AS (
    SELECT f.*,
           EXISTS (
               SELECT 1 FROM att a
               WHERE a.applicant_id = f.applicant_id
                 AND a.work_date >  f.first_date
                 AND a.work_date <= f.first_date + 14
           ) AS came_back
    FROM first_att f
    WHERE f.first_date <= DATE '2026-09-27'
)
SELECT c.camp_name,
       COUNT(*)                                 AS first_timers,
       COUNT(*) FILTER (WHERE came_back)        AS came_back,
       ROUND(AVG(came_back::INT), 3)            AS reattend_rate_14d
FROM flagged f
JOIN camps c ON c.camp_id = f.first_camp
GROUP BY ALL
ORDER BY reattend_rate_14d;
