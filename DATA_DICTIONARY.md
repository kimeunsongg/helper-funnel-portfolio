# 데이터 사전 — 가상 헬퍼 채용 퍼널

> **모든 데이터는 포트폴리오용 가상 데이터입니다.** 실제 쿠팡 CLS의 데이터·지표·캠프와 관계없습니다.
> 퍼널 단계와 확정 마감 시각만 공개된 [채용 과정 안내](https://helper.coupangls.com/recruitment-process/)를 따랐습니다.

- 기간: 2026-08-31(월) ~ 2026-10-11(일), 6주
- 캠프 8곳 × 조 3개(주간·야간·심야)
- DB 파일: `data/helper_funnel.duckdb` (CSV 원본도 `data/`에 있음)

## 퍼널 한눈에

```
지원(applied_at) → 웰컴 메시지(welcome_sent_at) → 응답(responded_at) → 확정(confirmed_at)
  → 리마인더(reminder_sent_at) → 출근(attendance.checked_in_at) → 재출근(같은 applicant_id의 다음 출근)
```

확정 마감: **야간조는 근무 당일 14시**, **주간·심야조는 근무 전날 17시**. 마감 뒤 응답은 확정될 수 없다.

## 조별 시작 시각

| shift | 시작 |
|---|---|
| 주간 | work_date 09:00 |
| 야간 | work_date 18:00 |
| 심야 | work_date 01:00 (근무일 새벽) |

## 테이블

### camps — 캠프 (8행)
| 컬럼 | 설명 |
|---|---|
| camp_id | 캠프 ID (C01~C08) |
| camp_name | 캠프 이름 (가상) |
| region | 권역 |
| shuttle_available | 셔틀 운행 여부 |
| reminder_policy | 캠프의 리마인더 발송 관행. `prev_evening` = 근무 전날 저녁, `pre_3h` = 출근 3시간 전 |

### camp_demand — 캠프·날짜·조별 필요 인원 (1,008행)
| 컬럼 | 설명 |
|---|---|
| camp_id, work_date, shift | 키 (이 세 개로 한 행) |
| required_headcount | 그 조에 필요한 헬퍼 수 |

### applicants — 지원자 (사람 단위)
| 컬럼 | 설명 |
|---|---|
| applicant_id | 지원자 ID (H로 시작) |
| first_apply_date | 처음 지원한 날 |
| channel | 처음 유입된 채널 (카카오광고, 네이버, 당근, 메타, 지인추천) |
| age_band | 연령대 |

### applications — 지원 건 (지원 1건 = 1행)
| 컬럼 | 설명 |
|---|---|
| application_id | 지원 건 ID (A로 시작) |
| applicant_id | 누가 지원했는지 |
| camp_id, shift, work_date | 어느 캠프·조·날짜에 지원했는지 |
| applied_at | 지원 시각 |
| welcome_sent_at | 웰컴 메시지 발송 시각 |
| responded_at | 카카오톡 응답 또는 설문 작성 시각. 응답 안 했으면 NULL |
| response_type | `kakao` / `survey` / NULL |
| confirmed_at | 근무 확정(출근 예정 안내) 시각. 확정 안 됐으면 NULL |
| reminder_sent_at | 출근 리마인더 발송 시각. 확정자에게만 있음 |

### attendance — 출근 기록 (출근 스캔 1회 = 1행)
| 컬럼 | 설명 |
|---|---|
| application_id | 어느 지원 건의 출근인지 |
| checked_in_at | 캠프 단말기 출근 스캔 시각 |

> 데이터를 그대로 믿지 마세요. 실제 운영 데이터처럼 **세면 안 되는 행**이 섞여 있습니다. 찾는 것도 스터디의 일부예요.
