"""가상 헬퍼 채용 퍼널 데이터 생성기.

모든 데이터는 포트폴리오용 가상 데이터다. 실제 쿠팡 CLS 데이터·지표와 관계없다.
퍼널 구조(지원 → 웰컴 메시지 → 응답 → 확정 → 출근 → 재출근)와 확정 마감 시각만
공개된 채용 안내(helper.coupangls.com/recruitment-process)를 따른다.

실행: .venv/bin/python scripts/generate_data.py
"""

import math
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb
import pandas as pd

SEED = 20261026
START = date(2026, 8, 31)  # 월요일
WEEKS = 6
OUT = Path(__file__).resolve().parent.parent / "data"

rng = random.Random(SEED)

# 캠프: 이름은 가상. reminder_policy는 캠프별 리마인더 발송 관행.
CAMPS = [
    # camp_id, camp_name, region, shuttle, base_demand, reminder_policy
    ("C01", "가람캠프", "경기남부", True, 120, "prev_evening"),
    ("C02", "나래캠프", "경기남부", True, 95, "pre_3h"),
    ("C03", "다솜캠프", "인천", True, 110, "prev_evening"),
    ("C04", "라온캠프", "경기북부", False, 70, "pre_3h"),
    ("C05", "마루캠프", "대전", False, 60, "prev_evening"),
    ("C06", "보람캠프", "대구", True, 80, "pre_3h"),
    ("C07", "새벽캠프", "부산", True, 90, "prev_evening"),
    ("C08", "여울캠프", "전남", False, 45, "pre_3h"),
]
SHIFTS = ["주간", "야간", "심야"]
SHIFT_SHARE = {"주간": 0.30, "야간": 0.45, "심야": 0.25}
DOW_FACTOR = [1.25, 1.15, 1.0, 0.95, 0.95, 0.80, 0.70]  # 월~일
CHANNELS = [("카카오광고", 0.30), ("네이버", 0.20), ("당근", 0.18), ("메타", 0.17), ("지인추천", 0.15)]
AGE_BANDS = [("20대", 0.30), ("30대", 0.22), ("40대", 0.22), ("50대", 0.18), ("60대+", 0.08)]


def pick(weighted):
    r, acc = rng.random(), 0.0
    for value, w in weighted:
        acc += w
        if r < acc:
            return value
    return weighted[-1][0]


def shift_start(work_date: date, shift: str) -> datetime:
    hour = {"주간": 9, "야간": 18, "심야": 1}[shift]
    return datetime.combine(work_date, datetime.min.time()) + timedelta(hours=hour)


def confirm_deadline(work_date: date, shift: str) -> datetime:
    # 야간: 근무 당일 14시 / 심야·주간: 근무 전날 17시
    base = datetime.combine(work_date, datetime.min.time())
    if shift == "야간":
        return base + timedelta(hours=14)
    return base - timedelta(days=1) + timedelta(hours=17)


def reminder_time(work_date: date, shift: str, policy: str) -> datetime:
    start = shift_start(work_date, shift)
    if policy == "pre_3h":
        return start - timedelta(hours=3)
    # prev_evening: 근무 전날 20시 (심야는 전날 15시)
    base = datetime.combine(work_date, datetime.min.time()) - timedelta(days=1)
    return base + timedelta(hours=15 if shift == "심야" else 20)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    camps = {c[0]: c for c in CAMPS}

    applicants = {}  # applicant_id -> dict
    returners = defaultdict(list)  # date -> [(applicant_id, camp_id)]
    attended_count = defaultdict(int)
    next_applicant = 1

    demand_rows, app_rows, att_rows = [], [], []
    next_app = 1

    def new_applicant(d):
        nonlocal next_applicant
        aid = f"H{next_applicant:06d}"
        next_applicant += 1
        applicants[aid] = {
            "applicant_id": aid,
            "first_apply_date": d,
            "channel": pick(CHANNELS),
            "age_band": pick(AGE_BANDS),
        }
        return aid

    for day in range(WEEKS * 7):
        d = START + timedelta(days=day)
        dow = d.weekday()

        # 오늘 지원하는 재지원자를 캠프·조에 배정
        todays_returners = defaultdict(list)
        for aid, camp_id in returners.pop(d, []):
            if rng.random() > 0.9:  # 10%는 다른 캠프로
                camp_id = rng.choice(list(camps))
            todays_returners[camp_id].append(aid)

        for camp_id, _, _, shuttle, base_demand, policy in CAMPS:
            returning_pool = todays_returners.get(camp_id, [])
            rng.shuffle(returning_pool)

            for shift in SHIFTS:
                demand = round(base_demand * SHIFT_SHARE[shift] * DOW_FACTOR[dow] * rng.uniform(0.9, 1.1))
                demand_rows.append((camp_id, d, shift, demand))

                target_apps = round(demand * rng.uniform(1.9, 2.3))
                n_return = min(len(returning_pool), round(target_apps * 0.45))
                pool = [returning_pool.pop() for _ in range(n_return)]
                pool += [new_applicant(d) for _ in range(target_apps - n_return)]

                deadline = confirm_deadline(d, shift)
                start = shift_start(d, shift)
                candidates = []

                for aid in pool:
                    is_new = attended_count[aid] == 0
                    applied_at = deadline - timedelta(minutes=rng.uniform(60, 60 * 72))
                    # 웰컴 메시지: 대부분 20분 이내, 월요일 오전 등 7%는 지연
                    if rng.random() < (0.12 if dow == 0 else 0.05):
                        delay = rng.uniform(60, 300)
                    else:
                        delay = min(rng.lognormvariate(math.log(8), 0.6), 20)
                    welcome_at = applied_at + timedelta(minutes=delay)

                    p_resp = sigmoid(1.3 - 0.006 * delay + (0.5 if not is_new else 0))
                    responded_at, resp_type = None, None
                    if rng.random() < p_resp:
                        responded_at = welcome_at + timedelta(minutes=rng.expovariate(1 / 120))
                        resp_type = "kakao" if rng.random() < 0.8 else "survey"

                    app = {
                        "application_id": f"A{next_app:07d}",
                        "applicant_id": aid,
                        "camp_id": camp_id,
                        "shift": shift,
                        "work_date": d,
                        "applied_at": applied_at,
                        "welcome_sent_at": welcome_at,
                        "responded_at": responded_at,
                        "response_type": resp_type,
                        "confirmed_at": None,
                        "reminder_sent_at": None,
                        "is_new": is_new,
                    }
                    next_app += 1
                    app_rows.append(app)
                    if responded_at and responded_at < deadline:
                        candidates.append(app)

                # 마감 전 응답자 중 먼저 응답한 순으로 필요 인원의 128%까지 확정 (노쇼 대비 초과 확정)
                candidates.sort(key=lambda a: a["responded_at"])
                cap = math.ceil(demand * 1.28)
                for app in candidates[:cap]:
                    app["confirmed_at"] = min(app["responded_at"] + timedelta(minutes=rng.uniform(5, 90)), deadline)
                    used = policy if rng.random() < 0.85 else ("pre_3h" if policy == "prev_evening" else "prev_evening")
                    app["reminder_sent_at"] = reminder_time(d, shift, used)
                    lead_h = (start - app["reminder_sent_at"]).total_seconds() / 3600

                    logit = 2.0
                    logit -= 0.55 if app["is_new"] else 0
                    logit -= 0.30 if shift == "심야" else 0
                    logit -= 0.35 if not shuttle else 0
                    logit -= 0.025 * max(lead_h - 3, 0)  # 리마인더가 이를수록 노쇼↑
                    if rng.random() < sigmoid(logit):
                        checkin = start - timedelta(minutes=rng.uniform(0, 30))
                        att_rows.append((app["application_id"], checkin))
                        if rng.random() < 0.012:  # 단말기 중복 스캔
                            att_rows.append((app["application_id"], checkin + timedelta(seconds=rng.randint(2, 40))))
                        aid = app["applicant_id"]
                        attended_count[aid] += 1
                        # 재출근 의향: 첫 출근 경험(캠프), 누적 출근 횟수에 좌우
                        p_return = 0.62 + min(attended_count[aid], 5) * 0.05
                        p_return -= 0.20 if camp_id == "C06" else 0  # 현장 경험 이슈 캠프
                        if rng.random() < p_return:
                            gap = 1 + int(rng.expovariate(1 / 3.5))
                            returners[d + timedelta(days=gap)].append((aid, camp_id))

    # 중복 지원: 같은 사람이 같은 조에 두 번 지원(새로고침 등), 약 2%
    dupes = []
    for app in rng.sample(app_rows, k=int(len(app_rows) * 0.02)):
        dup = dict(app)
        dup["application_id"] = f"A{next_app:07d}"
        next_app += 1
        dup["applied_at"] = app["applied_at"] + timedelta(minutes=rng.uniform(1, 15))
        dup["welcome_sent_at"] = dup["applied_at"] + timedelta(minutes=rng.uniform(3, 15))
        dup.update(responded_at=None, response_type=None, confirmed_at=None, reminder_sent_at=None)
        dupes.append(dup)
    app_rows += dupes

    camps_df = pd.DataFrame(
        [(c[0], c[1], c[2], c[3], c[5]) for c in CAMPS],
        columns=["camp_id", "camp_name", "region", "shuttle_available", "reminder_policy"],
    )
    demand_df = pd.DataFrame(demand_rows, columns=["camp_id", "work_date", "shift", "required_headcount"])
    apps_df = pd.DataFrame(app_rows).drop(columns=["is_new"]).sort_values("applied_at")
    for col in ["applied_at", "welcome_sent_at", "responded_at", "confirmed_at", "reminder_sent_at"]:
        apps_df[col] = pd.to_datetime(apps_df[col]).dt.floor("s")
    applicants_df = pd.DataFrame(applicants.values())
    att_df = pd.DataFrame(att_rows, columns=["application_id", "checked_in_at"]).sort_values("checked_in_at")
    att_df["checked_in_at"] = pd.to_datetime(att_df["checked_in_at"]).dt.floor("s")

    for name, df in [
        ("camps", camps_df),
        ("camp_demand", demand_df),
        ("applicants", applicants_df),
        ("applications", apps_df),
        ("attendance", att_df),
    ]:
        df.to_csv(OUT / f"{name}.csv", index=False)

    db_path = OUT / "helper_funnel.duckdb"
    db_path.unlink(missing_ok=True)
    con = duckdb.connect(str(db_path))
    for name in ["camps", "camp_demand", "applicants", "applications", "attendance"]:
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv_auto('{OUT / (name + '.csv')}')")
    for name in ["camps", "camp_demand", "applicants", "applications", "attendance"]:
        print(name, con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
    con.close()


if __name__ == "__main__":
    main()
