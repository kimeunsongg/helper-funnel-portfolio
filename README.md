# 헬퍼 채용 퍼널 진단

물류센터 단기 헬퍼 채용 퍼널(지원 → 응답 → 확정 → 출근 → 재출근)을 SQL로 분석하고, 단계별 이탈 요인과 개선 파일럿을 정리한 포트폴리오입니다.

> **모든 데이터는 가상 데이터입니다.** 공개된 헬퍼 채용 과정 안내의 퍼널 단계와 확정 마감 시각만 따랐고, 숫자는 Python으로 생성했습니다. 실제 회사의 데이터·지표·캠프와 관계없습니다.

## 데이터

- 기간: 2026-08-31 ~ 2026-10-11 (6주), 캠프 8곳 × 주간·야간·심야 3개 조
- 테이블 5개: `camps`, `camp_demand`, `applicants`, `applications`(58,238행), `attendance`(27,562행)
- 실제 데이터처럼 중복 지원(약 2%)과 중복 출근 스캔(약 1.2%)이 섞여 있음
- 분석 연습을 위해 생성기에 일부 패턴(웰컴 지연, 신규·심야 노쇼, 캠프별 차이)을 심어 두었음. 설정은 [scripts/generate_data.py](scripts/generate_data.py)에서 볼 수 있음
- 컬럼 설명: [DATA_DICTIONARY.md](DATA_DICTIONARY.md)

## 주요 결과

| 단계 | 결과 | 쿼리 |
|---|---|---|
| 퍼널 | 지원 57,097 → 응답 44,797 (78.5%) → 확정 35,266 (78.7%) → 출근 27,274 (77.3%) | [01_funnel.sql](sql/analysis/01_funnel.sql) |
| 지원→응답 | 웰컴 메시지 20분 초과 시 응답률 79.8% → 58.1% (−21.7%p). 월요일 근무분 지연 12.1% | [02_welcome_delay.sql](sql/analysis/02_welcome_delay.sql) |
| 응답→확정 | 응답 후 미확정 9,531건 중 90.8%가 정원 초과 (마감 후 응답은 9.2%) | [03_unconfirmed_reason.sql](sql/analysis/03_unconfirmed_reason.sql) |
| 확정→출근 | 노쇼율 신규 25.6% vs 기존 16.0%, 심야조 27.3% | [04_noshow.sql](sql/analysis/04_noshow.sql) |
| 대기 명단 | 인원 부족 조 415개 중 394개에 대기자 있음, 부족 인원 최대 89% 보충 가능 | [05_waitlist.sql](sql/analysis/05_waitlist.sql) |
| 출근→재출근 | 14일 내 재출근율 최저 보람캠프 26.2% vs 최고 37.0% | [06_reattend_14d.sql](sql/analysis/06_reattend_14d.sql) |

## 검증 방식

쿼리 초안은 Claude Code로 받고, 지표 정의·쿼리 리뷰·숫자 검증은 직접 했습니다. 잡아낸 문제와 숫자 변화는 [VALIDATION_LOG.md](VALIDATION_LOG.md)에 있습니다.

- [sql/validation/01_funnel_ai_draft.sql](sql/validation/01_funnel_ai_draft.sql): 처음 받은 퍼널 쿼리 원본 (중복 때문에 숫자가 틀림)
- [sql/validation/02_handcheck.sql](sql/validation/02_handcheck.sql): 한 조를 펼쳐 손으로 센 검증용 쿼리

## 사용 도구

Python · pandas (데이터 생성), SQL · DuckDB (분석), Claude Code (쿼리 초안), GitHub (기록 공개)

## 직접 돌려 보기

```bash
python3 -m venv .venv && .venv/bin/pip install duckdb pandas
.venv/bin/python scripts/generate_data.py      # 시드 고정, 언제 돌려도 같은 데이터
.venv/bin/python scripts/q.py sql/analysis/01_funnel.sql
```
