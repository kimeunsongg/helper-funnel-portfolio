-- 검증 사례: Claude가 처음 준 퍼널 쿼리 (원본 그대로 보존)
-- 실행: .venv/bin/python scripts/q.py sql/validation/01_funnel_ai_draft.sql
--
-- 문법 오류 없이 돌아가고 숫자도 그럴듯하지만 틀렸다.
--   1) attendance를 LEFT JOIN하면서 중복 출근 스캔(288건)만큼 행이 불어난다.
--   2) 같은 사람이 같은 캠프·날짜·조에 두 번 지원한 건(1,141건)이 그대로 남는다.
-- 고친 쿼리: sql/analysis/01_funnel.sql / 기록: VALIDATION_LOG.md

SELECT
    COUNT(*)                                        AS applied,
    COUNT(p.responded_at)                           AS responded,
    COUNT(p.confirmed_at)                           AS confirmed,
    COUNT(t.application_id)                         AS attended,
    ROUND(COUNT(p.responded_at) / COUNT(*), 3)      AS response_rate,
    ROUND(COUNT(p.confirmed_at) / COUNT(p.responded_at), 3) AS confirm_rate,
    ROUND(COUNT(t.application_id) / COUNT(p.confirmed_at), 3) AS attend_rate
FROM applications p
LEFT JOIN attendance t ON t.application_id = p.application_id;
