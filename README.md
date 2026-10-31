# 예지보전 실습판: 노이즈 vs 추세 — learn-pdm-lite-ljy

설비A·B의 센서 데이터에서 한 번의 튐과 꾸준한 상승을 구분해 정비할 설비를 고르는 10분 강의다. 수업은 Claude Code 스킬 `/learn-pdm-lite-ljy`가 진행한다 (Skills as Curriculum). 이 강의는 ljy가 course-forge로 직접 만들었다.

- **결과 대시보드**: https://jonglee46-bot.github.io/learn-pdm-lite-ljy/
- 처음이면 [GUIDE.md](GUIDE.md)부터. 기본 환경은 Claude 데스크톱 앱(Code 탭). VS Code는 GUIDE 부록 B

## 설치 — 한 줄

Claude Code 입력칸에 붙여 넣는다.

```
npx skills add jonglee46-bot/learn-pdm-lite-ljy --agent claude-code --global --yes 를 실행해 줘
```

새 세션에서 `/learn-pdm-lite-ljy`를 입력하면 수업이 시작된다. zip을 받았다면 GUIDE.md 2단계대로 설치한다.

## 블록

| Block | 주제 | 끝나면 생기는 것 |
|---|---|---|
| 0 | 준비 | 작업 폴더, 데이터, env_check.txt |
| 1 | 노이즈 vs 추세 | 판정 표, 그래프 한 장 (퀴즈 1문항) |
| 2 | 공개 | 대시보드 주소와 설치 한 줄 |

## 수업 방식

| 구분 | 내용 |
|---|---|
| 목표 — AI Native | AI에게 맡기는 것이 기본인 방식으로 일한다 |
| 방법 — Skills as Curriculum | 스킬이 블록마다 설명 → 실습 → STOP → 확인·퀴즈를 진행한다 |
| 형식 — 자율학습 | 강사 없이 자기 속도로, 퀴즈로 스스로 점검한다 |

## 원본 강의와 데이터 출처

| 자료 | 출처 | 구분 |
|---|---|---|
| 본 강의 덱 | keerhee/kma-auto-genai-3-1, `Day5_예지보전/Day5_3_Main_자동차예지보전AI활용.pdf` | 강의 자료 |
| 판정 규칙 | keerhee/kma-auto-genai-3-1, `보충교재/Day5_예지보전/06_예지보전_따라하기_II/PdM_Prompts_II.md` | 강의 자료 |
| 실습판 구성 | keerhee/kma-auto-genai-3-1, `보충교재/Day6_최종프로젝트/06_커리큘럼만드는스킬/최종패키지/1_Day5_Course_Forge/` | 강의 자료 |
| 센서 데이터 | keerhee/kma-auto-genai-3-1, `data/Day5/Day5_설비센서_50건_가상.csv` | 가상 데이터 |

## 개정 이력

| 날짜 | 바뀐 점 |
|---|---|
| 2026-10-31 | 첫 판 |

## 만든 방법

- `/course-forge`로 만들었다. 제작 기록(원본 요약·커리큘럼·검수 결과)은 `forge/`에 있다.
- 출처: 원본 강의 저장소 https://github.com/keerhee/kma-auto-genai-3-1
