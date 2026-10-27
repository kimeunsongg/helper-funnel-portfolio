-- 검증 사례: 한 조만 펼쳐서 손으로 세기
-- 실행: .venv/bin/python scripts/q.py sql/validation/02_handcheck.sql
--
-- 여울캠프(C08) 2026-09-15 심야조에 확정된 지원 건과 출근 스캔 횟수.
-- 손으로 센 결과: 확정 17명, 출근 11명. scan_count가 2 이상이면 중복 스캔이다 (이 조에는 없음).
-- 퍼널 쿼리를 같은 조건으로 돌린 결과와 이 숫자가 맞는지 비교했다.

SELECT p.application_id,
       p.applicant_id,
       p.confirmed_at,
       COUNT(t.application_id) AS scan_count
FROM applications p
LEFT JOIN attendance t USING (application_id)
WHERE p.camp_id = 'C08'
  AND p.work_date = DATE '2026-09-15'
  AND p.shift = '심야'
  AND p.confirmed_at IS NOT NULL
GROUP BY ALL
ORDER BY p.confirmed_at;
