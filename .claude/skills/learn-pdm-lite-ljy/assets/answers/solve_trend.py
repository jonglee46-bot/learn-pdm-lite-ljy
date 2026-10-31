"""설비센서 50건으로 노이즈와 추세를 판정하고 대시보드 한 장을 만든다.

현재 폴더의 설비센서 csv를 읽어 trend_judgement.csv, index.html, expected.json 을 쓴다.
판정 규칙은 원본 PdM_Prompts_II.md 프롬프트 3을 따른다.
"""
import csv, json, statistics as st
from pathlib import Path

SENSORS = {"진동": "진동(mm/s)", "온도": "온도(℃)", "압력": "압력(bar)"}

# 데이터 읽기
src = next(Path(".").glob("*설비센서_50건*.csv"))
rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
equipment = {}
for r in rows:
    equipment.setdefault(r["설비"][:3], []).append(r)
times = [r["시간"][11:] for r in equipment["설비A"]]


def judge(values):
    """기준선 상한을 구하고 3번 연속 초과 여부로 판정한다."""
    base = values[:12]  # 처음 12점(08:00~11:40)이 기준선
    upper = st.mean(base) + 3 * st.stdev(base)
    over = [v > upper for v in values]
    for i in range(len(values) - 2):
        if all(over[i:i + 3]):
            return upper, "추세", times[i]
    return upper, ("노이즈" if any(over) else "정상"), ""


def normal_first(values):
    """평상 범위(25점 전체의 평균 ± 2σ)로 처음 잡힌 시각을 찾는다."""
    m, s = st.mean(values), st.stdev(values)
    return next((t for t, v in zip(times, values) if abs(v - m) > 2 * s), None)


def minutes(t):
    return int(t[:2]) * 60 + int(t[3:])


# 판정
table, series = [], {}
for eq, rs in equipment.items():
    for name, col in SENSORS.items():
        values = [float(r[col]) for r in rs]
        series[eq, name] = values
        upper, result, start = judge(values)
        table.append({"설비": eq, "센서": name, "기준선 상한": round(upper, 3), "판정": result, "추세 시작": start})

with open("trend_judgement.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(table[0]))
    w.writeheader()
    w.writerows(table)

get = lambda eq, name: next(t for t in table if t["설비"] == eq and t["센서"] == name)
b_temp, b_vib, a_vib = get("설비B", "온도"), get("설비B", "진동"), get("설비A", "진동")
first_normal = min(t for t in (normal_first(series["설비B", n]) for n in SENSORS) if t)
lead = minutes(first_normal) - minutes(b_temp["추세 시작"])

# 그래프 한 장 (왼쪽 축 진동, 오른쪽 축 온도)
W, H, L, R, T, B = 640, 440, 54, 58, 34, 46
px = lambda i: L + (W - L - R) * i / (len(times) - 1)
py_vib = lambda v: H - B - (H - T - B) * v / 4
py_tmp = lambda v: H - B - (H - T - B) * (v - 30) / 40


def path(values, y):
    return " ".join(f"{'M' if i == 0 else 'L'}{px(i):.1f},{y(v):.1f}" for i, v in enumerate(values))


svg = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="설비A·B 진동과 설비B 온도 시간순 선 그래프">']
for v in range(0, 5):
    y = py_vib(v)
    svg.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}"/>')
    svg.append(f'<text class="tick" x="{L - 8}" y="{y + 5:.1f}" text-anchor="end">{v}</text>')
    svg.append(f'<text class="tick" x="{W - R + 8}" y="{y + 5:.1f}">{30 + v * 10}</text>')
for i, t in enumerate(times):
    if i % 6 == 0:
        svg.append(f'<text class="tick" x="{px(i):.1f}" y="{H - B + 24}" text-anchor="middle">{t}</text>')
svg.append(f'<text class="tick" x="{L - 44}" y="20">진동 mm/s</text>')
svg.append(f'<text class="tick" x="{W - 8}" y="20" text-anchor="end">온도 ℃</text>')
upper_y = py_tmp(b_temp["기준선 상한"])
svg.append(f'<line class="limit" x1="{L}" x2="{W - R}" y1="{upper_y:.1f}" y2="{upper_y:.1f}"/>')
svg.append(f'<text class="note tmp" x="{L + 6}" y="{upper_y - 8:.1f}">온도 기준선 상한 {b_temp["기준선 상한"]:.1f}℃</text>')
svg.append(f'<path class="line vib-a" d="{path(series["설비A", "진동"], py_vib)}"/>')
svg.append(f'<path class="line vib-b" d="{path(series["설비B", "진동"], py_vib)}"/>')
svg.append(f'<path class="line tmp" d="{path(series["설비B", "온도"], py_tmp)}"/>')


def mark(cls, t, value, y, label, dx, dy, anchor):
    i = times.index(t)
    svg.append(f'<circle class="dot {cls}" cx="{px(i):.1f}" cy="{y(value):.1f}" r="6"/>')
    svg.append(f'<text class="note {cls}" x="{px(i) + dx:.1f}" y="{y(value) + dy:.1f}" text-anchor="{anchor}">{label}</text>')


peak = max(series["설비A", "진동"])
peak_t = times[series["설비A", "진동"].index(peak)]
mark("vib-a", peak_t, peak, py_vib, f"{peak_t} 한 번 튐 → 노이즈", 0, -12, "middle")
t = b_temp["추세 시작"]
mark("tmp", t, series["설비B", "온도"][times.index(t)], py_tmp, f"온도 추세 시작 {t}", 14, 40, "start")
t = b_vib["추세 시작"]
mark("vib-b", t, series["설비B", "진동"][times.index(t)], py_vib, f"진동 추세 시작 {t}", -6, 76, "middle")
svg.append("</svg>")

html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>노이즈 vs 추세</title>
<style>
:root {{ --bg:#fbfaf7; --ink:#20242c; --sub:#5d6470; --line:#dfdcd3; --a:#7a8391; --b:#0f6e78; --t:#c2410c; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#16191f; --ink:#eceef2; --sub:#a4abb8; --line:#333945; --a:#9aa3b1; --b:#4cc3cf; --t:#fb8c4e; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.6 -apple-system,"Malgun Gothic","Noto Sans KR",sans-serif; }}
main {{ max-width:760px; margin:0 auto; padding:32px 16px; }}
.eyebrow {{ margin:0; color:var(--sub); font-size:14px; }}
h1 {{ margin:6px 0 10px; font-size:clamp(24px,5vw,32px); line-height:1.3; }}
.summary {{ margin:0 0 20px; }}
.legend {{ display:flex; flex-wrap:wrap; gap:6px 18px; margin:0 0 8px; padding:0; list-style:none; font-size:14px; }}
.legend li::before {{ content:""; display:inline-block; width:18px; height:3px; margin-right:6px; vertical-align:middle; background:var(--c); }}
svg {{ display:block; width:100%; height:auto; }}
.grid {{ stroke:var(--line); }}
.limit {{ stroke:var(--t); stroke-dasharray:6 5; opacity:.75; }}
.line {{ fill:none; stroke-width:3; stroke-linejoin:round; }}
.line.vib-a {{ stroke:var(--a); }} .line.vib-b {{ stroke:var(--b); }} .line.tmp {{ stroke:var(--t); }}
.dot {{ stroke:var(--bg); stroke-width:2; }}
.dot.vib-a {{ fill:var(--a); }} .dot.vib-b {{ fill:var(--b); }} .dot.tmp {{ fill:var(--t); }}
.tick {{ fill:var(--sub); font-size:17px; }}
.note {{ font-size:17px; font-weight:600; }}
.note.vib-a {{ fill:var(--sub); }} .note.vib-b {{ fill:var(--b); }} .note.tmp {{ fill:var(--t); }}
.source {{ margin:18px 0 0; color:var(--sub); font-size:13px; }}
</style>
</head>
<body>
<main>
<p class="eyebrow">Day5 예지보전 · 실습용 가상 데이터</p>
<h1>정비 대상은 설비B다</h1>
<p class="summary">설비B는 온도가 {b_temp["추세 시작"]}, 진동이 {b_vib["추세 시작"]}부터 추세다. 평상 범위로 처음 잡힌 {first_normal}보다 {lead}분 빠르다. 설비A는 한 번 튄 노이즈다.</p>
<ul class="legend">
<li style="--c:var(--a)">설비A 진동</li>
<li style="--c:var(--b)">설비B 진동</li>
<li style="--c:var(--t)">설비B 온도</li>
</ul>
{"".join(svg)}
<p class="source">추세: 처음 12점 기준선의 평균 + 3 × 표준편차를 3번 연속 초과. 출처: keerhee/kma-auto-genai-3-1, data/Day5/{src.name} (가상 데이터).</p>
</main>
</body>
</html>
"""
Path("index.html").write_text(html, encoding="utf-8")

# 기준값 저장
expected = {"values": {
    "b_temp_start": {"value": b_temp["추세 시작"], "block": 1},
    "b_vib_start": {"value": b_vib["추세 시작"], "block": 1},
    "a_vib_judgement": {"value": a_vib["판정"], "block": 1},
    "lead_minutes": {"value": lead, "decimals": 0, "block": 1},
    "b_temp_upper": {"value": round(b_temp["기준선 상한"], 1), "decimals": 1, "block": 1},
}}
Path("expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")
for t in table:
    print(t)
print("first_normal", first_normal, "lead", lead)
