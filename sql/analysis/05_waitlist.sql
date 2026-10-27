-- 대기 명단 가능성 확인
-- 캠프·날짜·조 단위로 "부족 인원"과 "정원 초과로 돌려보낸 인원"을 나란히 놓는다.
-- 대기자가 연락받으면 모두 온다고 가정한 최대치다 (실제로는 이보다 낮다).

WITH att AS (
    SELECT DISTINCT application_id FROM attendance
),
slot AS (
    SELECT p.camp_id, p.work_date, p.shift,
           COUNT(a.application_id) AS attended,
           COUNT(*) FILTER (
               WHERE p.responded_at IS NOT NULL AND p.confirmed_at IS NULL
                 AND p.responded_at < CASE WHEN p.shift = '야간' THEN p.work_date + INTERVAL 14 HOUR
                                           ELSE p.work_date - INTERVAL 1 DAY + INTERVAL 17 HOUR END
           ) AS waitlist
    FROM applications p
    LEFT JOIN att a USING (application_id)
    GROUP BY ALL
),
joined AS (
    SELECT d.shift, d.required_headcount,
           s.attended, s.waitlist,
           GREATEST(d.required_headcount - s.attended, 0) AS shortfall
    FROM camp_demand d
    JOIN slot s USING (camp_id, work_date, shift)
)
SELECT shift,
       COUNT(*)                                          AS slots,
       COUNT(*) FILTER (WHERE shortfall > 0)             AS short_slots,
       COUNT(*) FILTER (WHERE shortfall > 0 AND waitlist > 0) AS short_with_waitlist,
       SUM(shortfall)                                    AS total_shortfall,
       SUM(LEAST(shortfall, waitlist))                   AS coverable_by_waitlist,
       ROUND(SUM(LEAST(shortfall, waitlist)) / SUM(shortfall), 3) AS cover_rate
FROM joined
GROUP BY ALL
ORDER BY total_shortfall DESC;
