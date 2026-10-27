-- 응답했지만 확정 못 받은 지원의 사유
-- 실행: .venv/bin/python scripts/q.py sql/analysis/03_unconfirmed_reason.sql
--
-- 확정 마감: 야간조 = 근무 당일 14시, 주간·심야조 = 근무 전날 17시.
-- 마감 이후 응답 → '마감 후 응답', 마감 전 응답인데 미확정 → '정원 초과'.

WITH x AS (
    SELECT *,
           CASE WHEN shift = '야간' THEN work_date + INTERVAL 14 HOUR
                ELSE work_date - INTERVAL 1 DAY + INTERVAL 17 HOUR END AS deadline
    FROM applications
    WHERE responded_at IS NOT NULL
      AND confirmed_at IS NULL
)
SELECT CASE WHEN responded_at >= deadline THEN '마감 후 응답' ELSE '정원 초과' END AS reason,
       COUNT(*)                                     AS n,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 3)   AS share
FROM x
GROUP BY 1
ORDER BY n DESC;
