WITH att AS (
    SELECT DISTINCT p.application_id, p.applicant_id, p.work_date
    FROM attendance t JOIN applications p USING (application_id)
),
conf AS (
    SELECT p.*, c.shuttle_available,
           p.application_id IN (SELECT application_id FROM att) AS attended,
           NOT EXISTS (SELECT 1 FROM att a WHERE a.applicant_id = p.applicant_id AND a.work_date < p.work_date) AS is_new
    FROM applications p JOIN camps c USING (camp_id)
    WHERE p.confirmed_at IS NOT NULL
)
SELECT '신규·기존' AS axis, CASE WHEN is_new THEN '신규' ELSE '기존' END AS grp, COUNT(*) AS confirmed, ROUND(1 - AVG(attended::INT), 3) AS noshow_rate FROM conf GROUP BY ALL
UNION ALL
SELECT '조', shift, COUNT(*), ROUND(1 - AVG(attended::INT), 3) FROM conf GROUP BY ALL
UNION ALL
SELECT '셔틀', CASE WHEN shuttle_available THEN '있음' ELSE '없음' END, COUNT(*), ROUND(1 - AVG(attended::INT), 3) FROM conf GROUP BY ALL
ORDER BY axis, noshow_rate DESC;
