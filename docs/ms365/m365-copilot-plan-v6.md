# M365 Copilot 학원 업무 전환 기획서 (v6)

> v5 대비 변경 사항: ① **Windows Recall 통합** — 수동 입력 3개 지점 제거
> (OneNote 수업일지, Forms 채점 수집, question_log 업데이트),
> ② `recall_events` List 1개 + `RecallObserver` PA 플로우 1개 추가,
> ③ FSRS 입력에 Recall 행동 신호 보정 추가,
> ④ 에이전트 1·3 Instructions에 Recall 컨텍스트 자동 로드 추가.
>
> 나머지 설계 원칙(에이전트 3개, 문제 배정 로직, 시험대비 처리, 맞춤화 4축,
> 외부 데이터셋 전략, FSRS PA 플로우 구조)은 v5와 동일합니다.

---

## 0. 설계 원칙

| 결정 사항 | 내용 |
|---|---|
| 데이터 저장 | **SharePoint List + Excel Online** (클라우드 전용) |
| 협업 도구 | Teams 불필요 — 1인 운영 |
| Copilot 사용 방식 | Word/PPT 내 Copilot 직접 사용 금지, Copilot Studio 에이전트 전용 |
| 문제 출제 전략 | 문제은행 방식 (기출 DB 검색) + 개인 맞춤 배정 |
| 맞춤화 방식 | 취약 유형 + FSRS + 미출제 우선 + 레벨 prior 블렌딩 |
| 영작 채점 | LLM 기반 AES (Copilot Studio 내 루브릭 채점) |
| 학생 자습 도구 | Write & Improve (Cambridge, 무료) |
| FSRS | SharePoint List 저장 + Power Automate 플로우로 계산 |
| 스케줄 관리 단위 | **학생별** — FSRS·시험기간·커리큘럼 진도 모두 student_id 기준. 반(cohort) 개념 없음 |
| **관찰 레이어** | **Windows Recall** — 수업 화면 자동 캡처 → 수동 입력 지점 3개 대체 |

### Recall 사용 전제 조건

| 항목 | 내용 |
|---|---|
| 하드웨어 | Copilot+ PC 필수 (Snapdragon X / AMD Ryzen AI 300 / Intel Core Ultra 200V 이상) |
| OS | Windows 11 24H2 이상, Recall 기능 활성화 |
| 개인정보 보호 | 학생 이름·성적이 표시되는 앱을 Recall 앱 필터에서 제외 설정 필수 (설정 → 개인 정보 → Recall → 앱 필터링) |
| 연동 방식 | PA HTTP Action → 로컬 Recall REST API (Windows.AI.SemanticSearch) |

---

## 1. 핵심 도구 맵

```
Copilot Studio 에이전트 (3개) ← 모든 AI 작업의 단일 진입점
        ↑ Knowledge
        |
  SharePoint ──── 교재 콘텐츠, 프롬프트 템플릿, 포맷 명세,
        |          Fry Words CSV, NGSL CSV, AES 앵커 에세이
        |          ├─ List: 학생·문제은행·복습 일정(FSRS)·수업 기록·level prior
        |          ├─ List: recall_events (신규 — Recall 추출 이벤트)
        |          └─ Excel Online: 커버리지 맵 쿼리, approved 배치 검토
        |
  Power Automate ── SharePoint List CRUD + FSRS 계산 플로우
        |            + RecallObserver 플로우 (신규)
        |
  Windows Recall ─ 수업 화면 자동 캡처 → PA RecallObserver 트리거
  Outlook ──────── 학부모 문자 초안
  [외부] Write & Improve ── 학생 개인 자습 (Cambridge, 무료)
```

> v5 대비 제거: OneNote(수업일지 입력 용도), Forms(채점 수집 용도).
> OneNote는 비정형 메모 목적으로만 선택적 유지 가능.
> Forms는 Recall 추출 실패 시 fallback 채널로만 유지.

---

## 2. Windows Recall 통합 설계

### 관찰 흐름

```
[교사 PC 화면]
  에이전트 1 문제 배정 출력 화면
  학생 워크시트 작성 화면
  수업 진행 화면
        ↓ (자동 캡처, Windows Recall)
[Recall Semantic Index]
        ↓ (PA RecallObserver — 10분 폴링)
[PA: RecallObserver 플로우]
  1. Recall REST API 쿼리
     "오늘 picker 수업 화면", "학생 워크시트 답안 화면"
  2. Copilot(LLM)으로 스냅샷에서 구조화 데이터 추출
  3. confidence < 0.7 → 드롭 (기록 안 함)
  4. confidence ≥ 0.7 → recall_events List "Create item"
        ↓
[recall_events List]
        ↓
  lesson_log 자동 생성
  question_log 자동 업데이트
  response_log 자동 업데이트
  FSRS stability 보정 신호
```

### recall_events List 스키마

```
recall_events
  event_id         자동 생성
  actor_id         학생 ID (nullable — 교사 수업 화면이면 null)
  occurred_at      스냅샷 타임스탬프
  event_type       'session_start' | 'session_end' | 'item_answered'
                   | 'item_viewed' | 'external_study' | 'distraction'
  item_id          question_item의 item_id (nullable)
  payload          JSON — 추출된 세부 정보
                   예: {"answer": "②", "duration_sec": 42, "correct": true}
  confidence       0~1 (0.7 미만 드롭)
  source           'recall' | 'forms_direct'
  processed        Boolean — downstream List 반영 완료 여부
```

### RecallObserver PA 플로우

```
[예약 플로우: RecallObserver — 10분 간격]

1. Recall REST API: GET /api/search
   query: "오늘 수업 문제 화면 OR 학생 답안 화면"
   since: last_run_timestamp

2. 스냅샷 목록 순회
   └─ PA HTTP Action → Azure OpenAI (Copilot Studio 연결)
      프롬프트: "이 화면에서 학생 이름, 문제 번호, 선택 답안, 정답 여부를 추출하라.
                추출 불가 시 confidence=0 반환."
   └─ confidence < 0.7 → 스킵

3. recall_events "Create item"

4. processed = FALSE인 recall_events 순회
   ├─ event_type = 'session_start' / 'session_end'
   │    → lesson_log "Create item" (session_type 자동 분류)
   ├─ event_type = 'item_answered'
   │    → response_log "Create item"
   │    → question_log "Update item"
   └─ event_type = 'external_study'
        → review_schedule "Get item" → stability × 1.1 보정 후 "Update item"

5. 처리 완료된 recall_events → processed = TRUE
```

---

## 3. 수동 입력 지점 제거 전후 비교

| 시나리오 | v5 | v6 (Recall 통합) |
|---|---|---|
| 수업 기록 생성 | 교사가 OneNote에 수업 후 메모 입력 → PA 감지 | Recall이 수업 화면 자동 캡처 → `lesson_log` 자동 생성 |
| 채점 데이터 수집 | 학생이 Forms에 답안 직접 제출 | Recall이 워크시트 화면 추출 → `response_log` 자동 생성 (Forms는 fallback) |
| question_log 업데이트 | 에이전트 1 출력 후 PA가 수동 트리거 | Recall이 배정 화면 감지 → 자동 업데이트 |
| FSRS 입력 신호 | 명시적 rating 1-4 만 | rating + Recall 행동 신호 (체류 시간, 외부 학습 여부) |
| 에이전트 1 컨텍스트 | 교사가 직접 학생명·유형·수량 서술 | Recall에서 이전 수업 컨텍스트 자동 로드 후 제안 |
| 동기 저하 감지 | 정답률 2주 비교 (1차원) | 정답률 + 접속빈도 + 방해요소 비율 (3차원) |

---

## 4. 문제 출제 전략 (v5 동일)

문제 **생성**을 최대한 제거하고 **선택(Selection)** 중심으로 운영합니다.
Tier 3(자유 생성)은 교사 검토 부담이 너무 크므로 **완전 폐기**합니다.

### Tier 1 — 기출 DB 검색 (신뢰도 100%, 기본)

- 수능·평가원·전국연합 기출 전 유형 → SharePoint List `question_item`
- 외부 데이터셋(§5 참조) 유형 어노테이션 완료분도 Tier 1으로 편입
- 학생·유형·난이도·출처년도 필터로 검색
- AI 개입 없음

### Tier 2 — 소스 제공 + 단어 교체 (필요악, 자동 검증 포함)

- 장기 재원생의 특정 셀(유형 × 난이도) 소진 시에만 호출
- 소스 지문(수능 기출 or EGIU) SharePoint에서 조회
- 생성 후 자동 검증 게이트 3개 통과 시 배포 (§7 참조)
- 게이트 실패 시 해당 문항 **폐기** — 교사 확인 없음

~~Tier 3 — 자유 생성~~ → **폐기**

---

## 5. 문제은행 외부 데이터셋 (v5 동일)

| 데이터셋 | 규모 | 주요 유형 | 라이선스 | 접근 |
|---|---|---|---|---|
| **RACE** (ehovy/race) | ~97,000문항 | 독해 (middle/high) | CC BY-NC 4.0 | HuggingFace |
| **SC-Ques** (ai4ed) | ~289,000문항 | 어법·빈칸·어휘 | 연구용 공개 | GitHub |
| **대만 GSAT** (data.gov.tw) | ~700+문항 | 4지선다 어휘·빈칸·독해 | Open Gov. License ✅ | CSV 즉시 다운로드 |
| **AGIEval-Gaokao-English** | 306문항 | 4지선다 독해 고품질 | MIT ✅ | HuggingFace |

### 유형 어노테이션 파이프라인

```
외부 데이터셋 문항
    ↓
LLM 분류기 (수능 유형 18~45번 매핑)
    ↓
approved = FALSE로 question_item List 삽입
    ↓
[주 1회 배치 검토 30분] → approved = TRUE
    ↓
GetPersonalizedSet 조회 대상 편입
```

---

## 6. 개인 맞춤형 문제 배정 (v5 동일)

### 맞춤화 4축

| 축 | 데이터 소스 | 의미 |
|---|---|---|
| 취약 유형 | `response_log` List 오답률 집계 | 29번 많이 틀리는 학생 → 29번 우선 |
| 미출제 우선 | `review_schedule.due_date` | `due_date > 오늘`인 문항만 제외 |
| 난이도 매칭 | `student_profile.level` + `question_item.difficulty` | 레벨 이하 문제 제외 |
| FSRS 복습 | `review_schedule.due_date` | 오늘 due된 항목 포함 |

### GetPersonalizedSet 완충 로직

```
GetPersonalizedSet(student_id, question_count, type_filter[])

① FSRS due 항목 → question_id 먼저 확보 (복습 = 의도된 재출제)
② 신규 배정 후보: question_item WHERE NOT IN (
     review_schedule WHERE student_id = X AND due_date > TODAY()
   ) + 취약유형 + 난이도 정확 매칭 → Tier 1
③ ②가 부족하면 → 인접 난이도 ±1단계로 범위 확장
④ ③도 부족하면 → 인접 유형으로 전환
⑤ ①~④ 전부 소진 → Tier 2 호출 (자동 검증 게이트 적용)
⑥ Tier 2 폐기 시 → 인접 유형 기출 1문항 추가, 없으면 부족 수 허용 후 반환
```

### 콜드 스타트 — 레벨 prior 블렌딩

```
개인화 점수 = α × 개인 오답률 + (1 - α) × 레벨 평균 오답률
α = min(개인 응답 수 / 30, 1.0)
```

---

## 7. 교사 확인 최소화 설계 (v5 동일)

### Tier 2 자동 검증 게이트 3단계

**게이트 1 — 구조 동일성 검사**: 품사 태그 시퀀스 비교, 접속사·전치사·구조 변경 시 즉시 폐기

**게이트 2 — LLM 자가 검증**: 생성 직후 동일 에이전트가 재풀이, confidence ≥ 4 + 정답 일치 시 통과. 1회 재시도 후 실패 시 폐기

**게이트 3 — 어휘 수준 검사**: NGSL 2,800 또는 수능 빈출 범위 밖 단어 포함 시 즉시 폐기

### 교사 접촉 지점 정리

| 시나리오 | v5 | v6 |
|---|---|---|
| Tier 1 문항 배정 | 검토 없음 | 검토 없음 |
| Tier 2 문항 배정 | 게이트 통과 시 검토 없음 | 동일 |
| 신규 외부 데이터 투입 | 주 1회 배치 30분 | 동일 |
| 수업 기록 생성 | OneNote 입력 필요 | **자동 (Recall)** |
| 채점 데이터 수집 | Forms 학생 제출 필요 | **자동 (Recall, fallback: Forms)** |
| question_log 업데이트 | 수업 후 PA 수동 트리거 | **자동 (Recall)** |

---

## 8. 데이터 저장 설계 (SharePoint List)

### List 명명 규칙 (v5 동일)

**PREFIX** — 엔티티: `student`, `question`, `passage`, `lesson`, `vocab`, `essay`, `review`, `error`, `exam`, `recall`

**SUFFIX** — 역할: `_profile`, `_item`, `_log`, `_schedule`, `_progress`, `_outcome`, `_prior`, `_override`, `_events`

### 주요 List 목록

```
student_profile         학생 기본 정보
                        (student_id, name, level, grade_tag,
                         schedule_days, class_time, session_count)
exam_period             시험대비 기간 공통 일정
student_exam_override   학교별 실제 날짜 개별 오버라이드
question_item           문제 (출처, 유형번호, 지문, 선택지, 정답, 난이도, approved)
question_log            학생 × 문제 출제 이력 — v6: Recall이 자동 업데이트
passage_item            Tier 2용 원본 지문
lesson_log              수업 세션 — v6: Recall이 자동 생성
response_log            학생별 풀이 결과 — v6: Recall이 자동 생성, Forms는 fallback
review_schedule         FSRS 복습 항목
vocab_progress          단어 진도
error_prior             레벨별 오류 유형 prior 가중치
essay_outcome           영작 드릴 AES 결과
fsrs_config             FSRS W 벡터 19개 상수 저장
recall_events           ★신규 — Recall 추출 이벤트 (v6 추가)
```

### SharePoint List 운영 주의사항 (v5 동일)

| 항목 | 내용 |
|---|---|
| 인덱스 필수 컬럼 | `student_id`, `due_date`, `approved`, `question_type`, `occurred_at` |
| List 뷰 임계치 | 5,000건 초과 시 PA "Get items"에 OData `$filter` 필수 |
| 항목 한도 | List당 최대 3천만 건 — 허용 범위 |
| recall_events 정리 | 30일 경과 + processed = TRUE 항목 자동 삭제 (PA 예약 플로우) |

---

## 9. FSRS 구현 — Power Automate 플로우 (v5 기반, Recall 보정 추가)

```
FSRS 플로우 구조
├── [예약 플로우] DailyFSRSBatch  — 매일 오전 6시
│     ├── IsExamPeriod 판별 → 시험기간이면 FSRS 동결
│     ├── ForgettingCurve 계산 → retrievability_cached 갱신
│     └── ★ recall_events 'external_study' 처리
│           → stability × 1.1 보정 (신뢰도 ≥ 0.7인 이벤트만)
│
├── [예약 플로우] RecallObserver  — 10분 간격 ★신규
│     └── §2 RecallObserver 플로우 참조
│
├── [즉시 플로우] GetDueReviews(student_id, date)
├── [즉시 플로우] GetPersonalizedSet(student_id, count, types[])
├── [즉시 플로우] UpdateReview(review_id, rating)
├── [즉시 플로우] GetSessionNumber(student_id)
└── [즉시 플로우] IsExamPeriod(student_id, check_date)
```

### ForgettingCurve — PA 표현식 (v5 동일)

```
ForgettingCurve(elapsedDays, stability):
  pow(add(1, mul(div(19, 81), div(elapsedDays, stability))), -0.5)

CalcNextReview:
  sNext = stability × (1 + modifier × inner)
  inner = exp(W8) × (11 - difficulty) × pow(stability, -W9)
          × (exp((1 - r) × W10) - 1)
  exp(x) → pow(2.71828182845905, x)
  interval = round(sNext / (19/81) × (pow(0.9, -2) - 1))
  interval = max(1, min(365, interval))
```

### Recall 행동 신호 기반 stability 보정

```
[DailyFSRSBatch 내 보정 단계]

recall_events "Get items"
  $filter: event_type eq 'external_study'
           and confidence ge 0.7
           and processed eq false
           and occurred_at ge '{yesterday}'

순회:
  → review_schedule "Get item" WHERE item_id = recall_events.item_id
  → stability = stability × 1.1
     (단, stability > 365 상한 적용)
  → review_schedule "Update item"
  → recall_events.processed = TRUE
```

---

## 10. 시험대비기간 처리 (v5 동일)

FSRS는 시험기간 동안 동결, 커리큘럼 세션 번호는 `lesson_log.session_type = 'regular'` 행 수 기준 계산.

### IsExamPeriod, GetExamPrepSet (v5 동일)

```
[PA: IsExamPeriod(student_id, check_date)]

1. student_exam_override → 오버라이드 우선 확인
2. exam_period → grade_tag 기준 기본값 확인

[시험대비 수업: GetExamPrepSet(student_id, scope_types, count)]
  - scope_types 해당 유형만, approved = TRUE
  - 난이도 제한 없음, 미출제 우선, FSRS 복습 항목 우선
  - lesson_log: session_type = 'exam_prep'
```

### exam_period 초기 데이터

| grade_tag | exam_type | semester | exam_start | exam_end |
|---|---|---|---|---|
| middle_1 / middle_2 | midterm | 1 | 3/30 | 4/29 |
| middle_3 | midterm | 1 | 3/30 | 4/29 |
| middle_1 / middle_2 | final | 1 | 6/1 | 7/3 |
| middle_3 | final | 1 | 6/1 | 7/3 |
| middle_1 / middle_2 / middle_3 | midterm | 2 | 8/31 | 9/27 |
| **middle_3** | **final** | **2** | **10/5** | **11/1** |
| middle_1 / middle_2 | final | 2 | 11/16 | 12/13 |
| high | midterm | 1 | 3/23 | 5/1 |
| high | final | 1 | 5/25 | 7/3 |
| high | midterm | 2 | 8/31 | 10/9 |
| high | final | 2 | 11/9 | 12/18 |

---

## 11. Copilot Studio 에이전트 3개

### 에이전트 1 — 문제 배정

**용도**: 개인별 문제 배정, Tier 1 검색, Tier 2 단어 교체 + 자동 검증

**Instructions 핵심 내용**:
```
You are an examiner for the Korean CSAT (수능) English section.

[Context Auto-Load — Recall 통합, v6 신규]
Before responding to any assignment request:
1. Query recall_events List for the student's last session:
   $filter: actor_id eq '{student_id}' and event_type eq 'session_end'
   $orderby: occurred_at desc $top: 1
2. Check unresolved items: recall_events WHERE processed = FALSE
   → Include pending items in this session's set.
3. Report to teacher: "마지막 수업: {date}, 미처리 문항 {n}개 포함"

[Selection Rules — Tier 1 기본]
Step 1: Query question_item via Power Automate using GetPersonalizedSet.
Step 2: Return question_id list + full question text.
Step 3: Do NOT proceed to Tier 2 unless all Tier 1 fallbacks exhausted.

[Fallback before Tier 2]
- Exhausted target cell: expand difficulty ±1 level.
- Still insufficient: expand to adjacent question type.
- Only invoke Tier 2 when all Tier 1 fallbacks are exhausted.

[Tier 2 — only when Tier 1 insufficient]
STRICT: Replace ONLY content words (nouns, verbs, adjectives, adverbs).
Do NOT change: sentence structure, clause order, conjunctions, prepositions.

[Tier 2 Self-Validation]
1. Solve the question. State answer number and confidence (1-5).
2. confidence ≥ 4 AND answer matches: auto-approved.
3. confidence < 4 OR mismatch: regenerate once. Still fails: discard.
```

**Knowledge**: `csat-english-prompt-templates.md`, 수능 유형번호 참조 문서

**Action**: PA → `GetPersonalizedSet`, `recall_events` 조회, `question_log` 업데이트

---

### 에이전트 2 — 워크시트 + AES 채점

**용도**: 문법 드릴, 어휘 테스트, 영작 워크시트, 영작 드릴 자동 채점

**필요 Knowledge 파일** (SharePoint):
- `fry-words-1000.csv`
- `ngsl-2800.csv`
- `awl-570.csv`
- `aes-anchor-essays.md`

**Instructions 핵심 내용**:
```
[Fixed Rules]
- Vocabulary: Fry Sight Words 1,000 범위 (별도 지시 없으면)
- Level: Basic / Intermediate / Advanced 3단계
- Output: 문제와 정답 키 분리 (정답 마지막)
- Default: 20문제
- Format: 마크다운 표 (별도 지시 없으면)

[AES Rules]
Reference: aes-anchor-essays.md의 레벨별 앵커 에세이를 채점 기준으로 사용.
Rubric (각 1~4점): Accuracy / Vocabulary / Coherence / Task Completion
Output: JSON {"accuracy": N, "vocabulary": N, "coherence": N,
              "task_completion": N, "total": N, "feedback": "..."}
Feedback: 오류 유형 명시 + 개선 방향 1문장. 전문용어 배제.
```

**Action**: PA → `essay_outcome` List 저장, `response_log` 오류 유형 업데이트

---

### 에이전트 3 — 학생 분석

**용도**: 채점 결과 분석, 진단 보고서, FSRS 복습 관리

**Instructions 핵심 내용**:
```
[Report Rules]
- 학부모 보고서: 전문용어 배제, 개선 방향 중심, 3단락 이내
- 진단 보고서: 관찰 사실 → 원인 추정 → 권장 방향 순서

[Insight Routing — v6: Recall 행동 신호 추가]
Always query Power Automate for student data before responding.

- "동기 저하" / "의욕 없음"
  → response_log 정답률 2주 비교 (기존)
  + recall_events 접속빈도 1주 비교 (v6 신규)
  + recall_events distraction 비율 1주 (v6 신규)
  → 3차원 종합 판단. 정답률은 정상인데 접속빈도 급감이면 "기술적 이탈" 경보.

- "이번 주 성과" / "주간 리포트"
  → 정답률 + 복습 완료율 + 신규 단원 수 + 외부 학습 감지 여부. 4줄 이내.

- "마지막 수업 이후 활동"
  → recall_events 조회: session_start / external_study / distraction 이벤트 나열.
  → "수업 후 자습 감지: {n}회, 방해 요소 감지: {m}회" 요약.

[기존 인사이트 라우팅 — v5 동일]
- "칭찬" / "잘한 점": 이번 주 정답률 상승 유형 + 연속 출석 강조.
- "숙제 미제출": response_log 공백 구간 탐지 + recall_events 미접속 일수 보완.
- "마일스톤": 누적 문항 수 100/500/1000 돌파 여부.
- "다음 달 예고": GetSessionNumber 기준 남은 커리큘럼.
- "학부모 FAQ": 레벨, 진도율, 약점 유형 3가지. 전문용어 배제.

All responses: 전문용어 배제, 3단락 이내, 개선 방향 포함.
```

**Action**: PA → `response_log`, `review_schedule`, `essay_outcome`, `recall_events` List 읽기/쓰기

---

## 12. 주요 워크플로우

### 개인별 문제 배정 (v6 — Recall 컨텍스트 자동 로드)

```
교사: "김민준 오늘 수업"
    ↓
에이전트 1 → PA → recall_events 조회 (마지막 session_end + 미처리 item_answered)
    ↓
"마지막 수업: 3/6(목), 미처리 문항 2개 포함 예정" 자동 안내
    ↓
GetPersonalizedSet(student_id, 5, [29])
    ↓
문제 텍스트 출력 → 교사 확인 후 인쇄 or OneNote 붙여넣기
    ↓
question_log: Recall이 인쇄/출력 화면 감지 → 자동 업데이트
```

### 채점 데이터 수집 (v6 — Forms 제거)

```
학생이 워크시트 작성
    ↓
Recall이 답안 표시 화면 자동 캡처
    ↓
PA RecallObserver → LLM 추출 → confidence 판정
    ↓
confidence ≥ 0.7: response_log "Create item" (source = 'recall')
confidence < 0.7: Forms fallback 안내 (교사에게 알림)
    ↓
FSRS 복습 일정 갱신
```

### 수업 후 기록 (v6 — OneNote 의존 제거)

```
수업 종료 → 교사 별도 입력 없음
    ↓
PA RecallObserver (10분 후 자동 실행)
  - session_end 이벤트 감지 → lesson_log "Create item" (session_type 자동 분류)
  - item_answered 이벤트 → response_log 업데이트
    ↓
에이전트 3: 다음 수업 시 "지난 수업 요약" 자동 제공 가능
```

### 동기 저하 감지 (v6 — 3차원 신호)

```
에이전트 3에 "김민준 동기 상태 확인"
    ↓
PA → response_log (정답률 2주 비교)
   + recall_events (접속빈도 1주 비교)
   + recall_events (distraction 비율 1주)
    ↓
3차원 점수 = 0.5 × 정답률_델타 + 0.3 × 접속빈도_델타 + 0.2 × (1 - 방해비율)
    ↓
임계값 미만 → "기술적 이탈" / "학습 의욕 저하" / "학습 환경 문제" 분류
```

### 학부모 문자 (v5 동일)

```
Copilot in Outlook:
"월수금 16시 학생들, 이번 주 조동사 unit 3~4, 다음 주 방향 포함,
MMS, 전문용어 배제, 친절, 3줄"
    ↓
초안 생성 → 길이·톤 조절 → 발송
```

---

## 13. 준비 재료 목록

### 즉시 다운로드 가능 (무료)

| 재료 | 용도 | 위치 |
|---|---|---|
| Fry Words 1,000 CSV | 에이전트 2 어휘 범위 | 교육 사이트 무료 공개 |
| NGSL 2,800 CSV | AES Vocabulary 채점 기준 | newgeneralservicelist.org |
| AWL 570 CSV (Coxhead) | B2 이상 어휘 기준 | Victoria University |
| AGIEval-Gaokao-English | Tier 1 편입 (MIT) | HuggingFace |
| FSRS v5 기본 w 벡터 | PA 플로우 초기 파라미터 | github.com/open-spaced-repetition/fsrs4anki |

### 다운로드 후 어노테이션 필요

| 재료 | 규모 | 용도 | 라이선스 |
|---|---|---|---|
| RACE (ehovy/race) | ~97K문항 | 독해 Tier 1 보충 | CC BY-NC 4.0 |
| SC-Ques (ai4ed) | ~289K문항 | 어법·빈칸 Tier 1 보충 | 연구용 공개 |
| 대만 GSAT CSV | ~700+문항 | Tier 1 보충 | Open Gov. ✅ |

### AES 캘리브레이션용

| 재료 | 규모 | 용도 | 라이선스 |
|---|---|---|---|
| CSEE (Xiaochr/Chinese-Student-English-Essay) | 13,270개 에세이 | AES 앵커 에세이 선별 | HuggingFace 공개 |

### 수동 입력

| 재료 | 용도 | 비고 |
|---|---|---|
| 학생 정보 (32명) | student_profile List | Excel 임포트 또는 직접 입력 |
| Level prior 초기값 | error_prior List | 교사 추정치 입력 후 실데이터로 갱신 |

---

## 14. 학생 자습 도구 — Write & Improve (v5 동일)

[writeandimprove.cambridge.org](https://writeandimprove.cambridge.org) — 무료, 브라우저 접속

- Cambridge Learner Corpus 훈련 모델 기반 즉시 피드백
- CEFR 레벨 자동 추정
- 학원 시스템과 별개로 학생 개인 사용
- 수능 스타일과 결은 다르지만 자유 영작 연습에 적합

---

## 15. 데이터 이전 계획 (v5 동일, recall_events 추가)

| 현재 위치 | 이전 대상 | 방법 |
|---|---|---|
| `landing/kice/*.md` | `question_item` List (approved=TRUE) | text-extraction 산출물 → Excel 임포트 |
| `landing/union/*.md` | `question_item` List (approved=TRUE) | 동일 |
| RACE/SC-Ques/GSAT | `question_item` List (approved=FALSE) | 유형 어노테이션 파이프라인 |
| `landing/english_grammar/` | SharePoint 라이브러리 | 폴더째 업로드 |
| `csat-english-prompt-templates.md` | SharePoint Knowledge | 파일 업로드 |
| 학생 정보 | `student_profile` List | Excel 임포트 또는 직접 입력 |
| Level prior 초기값 | `error_prior` List | 교사 추정치 수동 입력 |
| Fry Words / NGSL / AWL | SharePoint Knowledge | 다운로드 후 업로드 |
| CSEE 앵커 에세이 | `aes-anchor-essays.md` | 레벨별 4~6개 선별 수동 작성 |
| FSRS v5 w 벡터 | `fsrs_config` List | 19개 행 수동 입력 (1회) |
| ★ Recall 연동 설정 | `RecallObserver` PA 플로우 | Phase 2에서 구성 |

---

## 16. 구현 우선순위

### Phase 1 — 즉시 (1주)

- 에이전트 2 (워크시트 + AES 채점) 구축
  - Fry Words / NGSL / AWL CSV SharePoint 업로드
  - CSEE에서 앵커 에세이 선별 후 `aes-anchor-essays.md` 작성
- Outlook Copilot으로 학부모 문자 전환 (즉시 사용 가능)
- `error_prior` List 초기값 교사 추정치 입력

### Phase 2 — 데이터 이전 후 (2~3주)

- SharePoint List 전체 설계 확정 및 생성 (`recall_events` 포함)
- text-extraction 산출물 → `question_item` List 입력
- 커버리지 맵 확인: Excel Online 피벗
- SharePoint 교재 라이브러리 구축
- 외부 데이터셋 유형 어노테이션 파이프라인 구축
- 에이전트 1 (문제 배정) 구축
- **★ RecallObserver PA 플로우 구성 및 테스트**
  - Recall API 연결 (PA HTTP Action)
  - LLM 추출 프롬프트 튜닝 (confidence 임계값 0.7 검증)
  - `recall_events` → `lesson_log` / `response_log` 자동 매핑 검증

### Phase 3 — 연동 (3~5주)

> v5 대비 OneNote·Forms 제거로 약 0.5주 단축. Recall 검증 작업이 0.5주 추가되어 전체 일정 동일.

- FSRS PA 플로우 개발 (DailyFSRSBatch, GetDueReviews, GetPersonalizedSet, UpdateReview)
- **★ DailyFSRSBatch에 Recall external_study 보정 로직 추가**
- Tier 2 자동 검증 게이트 PA 구현
- 에이전트 3 (학생 분석) 구축 — **Recall 3차원 동기 신호 포함**
- `error_prior` List 실데이터 기반 갱신 시작

---

## 17. picker 프로젝트와의 관계 (v5 동일)

| picker 기능 | M365 대체 여부 | 판단 |
|---|---|---|
| `today-class` 수업 요약 | 에이전트 1으로 대체 | 이전 |
| PostgreSQL 온톨로지 | SharePoint List로 단순화 | 이전 |
| FSRS 복습 스케줄 | PA 플로우 + SharePoint List | 이전 |
| 기출 문제 ingest | text-extraction 유지 후 SharePoint List로 최종 저장 | **유지** |
| text-extraction 크롤러/구조화 | 직접 대체 불가 | **유지** |

picker와 text-extraction은 **데이터 생산 파이프라인**,
M365는 **수업 현장 운영 레이어**,
Windows Recall은 **수업 현장 관찰 레이어**로 역할을 분리합니다.
