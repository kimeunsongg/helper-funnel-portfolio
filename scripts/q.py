"""SQL 파일이나 쿼리 문자열을 가상 헬퍼 퍼널 DB에서 실행한다.

사용법:
  .venv/bin/python scripts/q.py sql/session1/q1_tables.sql
  .venv/bin/python scripts/q.py "SELECT COUNT(*) FROM applications"
"""

import sys
from pathlib import Path

import duckdb

DB = Path(__file__).resolve().parent.parent / "data" / "helper_funnel.duckdb"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    arg = sys.argv[1]
    path = Path(arg)
    sql = path.read_text() if path.suffix == ".sql" and path.exists() else arg

    con = duckdb.connect(str(DB), read_only=True)
    # 세미콜론으로 나뉜 여러 문장을 차례로 실행해 결과를 모두 보여준다
    for stmt in [s.strip() for s in sql.split(";") if s.strip() and not all(
        line.strip().startswith("--") or not line.strip() for line in s.splitlines()
    )]:
        print(con.sql(stmt).show(max_rows=40, max_width=200) or "")


if __name__ == "__main__":
    main()
