# 업스테이지는 왜 API를 다 따로 만들었을까?

업스테이지를 이해할 때 중요한 포인트가 있다.

업스테이지는 단순히 “LLM 하나 만든 회사”라기보다는, **문서 기반 AI 서비스를 만들 때 필요한 기능들을 각각 API 형태로 제공하는 회사**에 가깝다.

예를 들면 이런 식이다.

```text id="tikb01"
문서 읽기
→ OCR / Document Parse API

문서에서 필요한 값 뽑기
→ Information Extract API

문장을 숫자 벡터로 바꾸기
→ Embedding API

질문에 답변 생성하기
→ Solar LLM API

답변이 근거에 맞는지 확인하기
→ Groundedness Checker
```

업스테이지 cookbook에도 Chat, Document Parse, Document OCR, Information Extraction, Embedding API가 각각 따로 소개되어 있다. 즉, 업스테이지는 문서 AI와 LLM 서비스를 하나의 덩어리로만 제공하는 게 아니라, 필요한 기능을 각각 API로 호출해서 조립할 수 있게 만든다. ([GitHub][1])

---

# “API를 각자 만들었다”는 말의 의미

처음 들으면 헷갈릴 수 있다.

“API를 각자 만들었다”는 말은 이런 뜻에 가깝다.

```text id="pbd4ah"
OCR도 따로 API가 있고
Document Parse도 따로 API가 있고
Embedding도 따로 API가 있고
Solar LLM도 따로 API가 있다
```

즉, RAG나 문서 자동화 시스템을 만들 때 필요한 기능을 하나의 블랙박스로 묶어버린 게 아니라, **각 단계별로 호출 가능한 API로 나누어 제공한다**는 뜻이다.

예를 들어 내가 회사 내부 문서 검색 챗봇을 만든다고 해보자.

전체 흐름은 이렇게 된다.

```text id="13y4mn"
PDF / 이미지 / 문서 업로드
        ↓
Document Parse 또는 OCR API
        ↓
텍스트 추출
        ↓
청킹
        ↓
Embedding API
        ↓
벡터DB 저장
        ↓
사용자 질문
        ↓
질문 Embedding
        ↓
벡터 검색
        ↓
Solar LLM API
        ↓
답변 생성
```

여기서 업스테이지가 해주는 부분은 여러 개로 나뉜다.

```text id="fm86op"
문서를 읽는 API
텍스트를 벡터로 바꾸는 API
답변을 생성하는 API
근거성을 확인하는 API
```

그래서 “각자 API를 만들었다”는 말은, **문서 처리부터 LLM 답변 생성까지 필요한 부품들을 각각 API 제품으로 제공한다**는 뜻으로 이해하면 된다.

---

# 1. OCR API: 이미지에서 글자 뽑기

OCR API는 이미지나 스캔 문서 안에 있는 글자를 읽어주는 API다.

예를 들어 사용자가 이런 파일을 올린다.

```text id="q092d6"
신분증 이미지
계약서 스캔본
영수증 사진
보험 청구서
은행 서류
```

그러면 OCR API는 이미지 안의 글자를 읽어서 텍스트로 바꿔준다.

```text id="2ur4sc"
이미지/PDF
  ↓
OCR API
  ↓
텍스트 추출 결과
```

응답은 보통 이런 느낌이다.

```json id="g12qfu"
{
  "pages": [
    {
      "page": 1,
      "text": "이름: 홍길동\n생년월일: 2000.01.01",
      "words": [
        {
          "text": "홍길동",
          "confidence": 0.98,
          "boundingBox": {
            "x": 120,
            "y": 80,
            "width": 70,
            "height": 24
          }
        }
      ]
    }
  ]
}
```

OCR API의 핵심은 이것이다.

```text id="gi4ps2"
이미지를 텍스트로 바꾼다
글자의 위치를 찾는다
인식 신뢰도를 준다
```

업스테이지 문서 OCR은 스캔 양식과 이미지에서 텍스트를 추출하는 기능으로 설명되고, 한글·한자·저품질 스캔도 지원하는 방향으로 소개되어 있다. ([Upstage Console][2])

---

# 2. Document Parse API: 문서를 LLM이 읽기 좋게 바꾸기

OCR이 “글자 읽기”에 가깝다면, Document Parse는 한 단계 더 나아간다.

단순히 글자만 뽑는 게 아니라, 문서 구조를 살려서 바꿔준다.

예를 들어 PDF 안에는 이런 것들이 있다.

```text id="86ewmt"
제목
본문
표
차트
이미지
각주
다단 구성
페이지 번호
```

그냥 OCR만 하면 텍스트가 순서 없이 섞일 수 있다.

하지만 Document Parse는 문서를 LLM이 읽기 좋은 형태로 바꿔준다.

```text id="jyh6gu"
PDF / 스캔 이미지 / 슬라이드 / 스프레드시트
        ↓
Document Parse API
        ↓
HTML / Markdown 같은 구조화된 텍스트
```

예를 들면 이런 식이다.

```markdown id="nx29cw"
# 보험 약관

## 제1조 목적

이 약관은 ...

| 항목 | 보장 금액 |
|---|---|
| 입원비 | 100,000원 |
| 수술비 | 1,000,000원 |
```

이게 중요한 이유는 RAG 때문이다.

RAG에서는 문서를 검색해서 LLM에게 넣어야 하는데, 문서 구조가 깨지면 답변 품질도 떨어진다.

업스테이지 Document Parse는 PDF, 스캔 이미지, 표, 차트 같은 복잡한 문서를 HTML이나 Markdown처럼 LLM이 처리하기 쉬운 구조화된 형식으로 변환하는 제품으로 설명된다. ([Upstage AI][3])

---

# 3. Information Extract API: 필요한 값만 뽑기

문서에서 전체 텍스트를 다 가져오는 것보다, 특정 값만 필요한 경우도 많다.

예를 들어 보험 청구서라면 이런 값이 중요할 수 있다.

```text id="uh2okc"
이름
생년월일
진료일
병원명
청구 금액
계좌번호
```

계약서라면 이런 값이 필요할 수 있다.

```text id="5s6164"
계약자
계약 시작일
계약 종료일
계약 금액
위약금 조항
```

이런 값을 뽑는 기능이 Information Extraction이다.

흐름은 이렇게 볼 수 있다.

```text id="on36na"
문서
  ↓
OCR / Document Parse
  ↓
Information Extract API
  ↓
필요한 필드만 JSON으로 추출
```

예상 응답은 이런 식이다.

```json id="gl5hho"
{
  "name": "홍길동",
  "birthDate": "2000-01-01",
  "hospitalName": "OO병원",
  "claimAmount": 120000
}
```

즉, OCR이 “글자를 읽는 것”이라면, Information Extract는 **업무에 필요한 항목을 구조화해서 뽑는 것**이다.

---

# 4. Embedding API: 문장을 숫자 벡터로 바꾸기

RAG에서 가장 헷갈리는 부분이 임베딩이다.

임베딩은 문장을 숫자 벡터로 바꾸는 작업이다.

예를 들어 이런 문장이 있다.

```text id="0th3r6"
OCR API는 이미지나 PDF에서 텍스트를 추출하는 기능입니다.
```

Embedding API에 넣으면 이런 숫자 배열이 나온다.

```text id="ldvvyh"
[0.12, -0.45, 0.88, 0.03, ...]
```

이 숫자 배열을 벡터라고 한다.

왜 굳이 숫자로 바꿀까?

컴퓨터가 문장의 의미적 유사도를 계산하려면 숫자 형태가 필요하기 때문이다.

```text id="p5bwjf"
"OCR API가 뭐야?"
"이미지에서 글자를 뽑는 기술"

두 문장은 단어가 완전히 같지는 않지만 의미는 비슷하다.
```

Embedding API는 이런 의미적 유사도를 계산할 수 있도록 문장을 벡터로 바꿔준다.

업스테이지 블로그에서는 RAG의 핵심 요소를 벡터DB, 문서를 벡터로 임베딩하는 embedding model, 답변을 생성하는 LLM이라고 설명한다. 또한 Solar Embedding은 문서 벡터화를 위한 embedding 모델로 소개된다. ([Upstage AI][4])

---

# 5. Solar LLM API: 답변 생성하기

Solar LLM API는 사용자의 질문과 문맥을 받아 답변을 생성하는 API다.

예를 들어 RAG에서는 검색된 문서를 Solar LLM에게 같이 넣는다.

```text id="57m0be"
[검색된 문서]
OCR API는 이미지나 PDF에서 텍스트를 추출하는 기능입니다.

[사용자 질문]
OCR API는 뭐야?
```

그러면 Solar LLM API가 답변을 생성한다.

```text id="sqsm3z"
OCR API는 이미지나 PDF 문서에서 텍스트를 추출하는 API입니다.
스캔 문서, 영수증, 계약서 같은 비정형 문서를 디지털 텍스트로 바꾸는 데 사용됩니다.
```

즉, Solar LLM API는 RAG 파이프라인의 마지막 생성 단계에 붙는다.

```text id="zjqy46"
검색된 근거 문서
  ↓
Solar LLM API
  ↓
최종 답변
```

업스테이지는 Solar LLM을 RAG에 특화된 LLM으로 소개하며, Solar Embedding과 Solar LLM은 OpenAI package와 호환되고 LangChain, LlamaIndex와도 연동된다고 설명한다. ([Upstage AI][4])

---

# 6. Groundedness Checker: 답변이 근거에 맞는지 확인하기

LLM은 답변을 잘 만들지만, 가끔 없는 말을 만들어낼 수 있다.

이걸 hallucination, 즉 환각이라고 부른다.

그래서 RAG에서는 이런 질문이 중요하다.

```text id="w9zis5"
LLM이 만든 답변이 실제 검색된 문서 근거와 맞는가?
```

Groundedness Checker는 이 부분을 확인하는 역할로 이해하면 된다.

흐름은 이렇게 볼 수 있다.

```text id="t20wg3"
검색된 문서
  ↓
Solar LLM 답변 생성
  ↓
Groundedness Checker
  ↓
답변이 근거에 기반했는지 확인
```

면접에서 말할 때는 이렇게 표현하면 좋다.

```text id="lgyxp9"
RAG에서는 검색된 문서를 기반으로 답변을 생성하지만, LLM이 근거에 없는 내용을 생성할 수 있습니다.
그래서 답변이 context에 grounded되어 있는지 확인하는 단계가 필요합니다.
```

업스테이지는 RAG 구성 요소로 Document AI, embedding models, Solar LLM, Groundedness Checker를 함께 언급한다. ([Upstage AI][4])

---

# RAG 흐름으로 다시 묶어보기

이제 업스테이지 API들을 RAG 흐름에 맞춰 다시 정리해보자.

```text id="j81nij"
1. 문서가 들어온다
   ↓
2. Document Parse / OCR API로 텍스트를 뽑는다
   ↓
3. 텍스트를 chunk로 자른다
   ↓
4. Embedding API로 chunk를 벡터로 바꾼다
   ↓
5. 벡터DB에 저장한다
   ↓
6. 사용자가 질문한다
   ↓
7. 질문도 Embedding API로 벡터화한다
   ↓
8. 벡터DB에서 비슷한 chunk를 검색한다
   ↓
9. 검색된 chunk와 질문을 Solar LLM API에 보낸다
   ↓
10. 답변을 생성한다
   ↓
11. Groundedness Checker로 근거성을 확인한다
```

여기서 업스테이지가 제공하는 API를 표시하면 이렇다.

```text id="jo2ns3"
문서 읽기
→ Upstage Document OCR / Document Parse

문서 벡터화
→ Upstage Embedding

답변 생성
→ Upstage Solar LLM

근거성 확인
→ Groundedness Checker
```

반대로 우리가 직접 만들어야 하는 부분도 있다.

```text id="qzt2mj"
파일 업로드 서버
청킹 로직
벡터DB 저장 로직
검색 API
사용자 인증
화면
로그/모니터링
배포/운영
```

즉, 업스테이지가 모든 서비스를 통째로 대신 만들어준다기보다는, **AI 기능에 해당하는 핵심 부품을 API로 제공한다**고 보는 게 맞다.

---

# 왜 이렇게 나눠서 API로 제공할까?

이렇게 기능을 나눠두면 장점이 많다.

## 1. 필요한 기능만 골라 쓸 수 있다

어떤 회사는 OCR만 필요할 수 있다.

어떤 회사는 이미 문서 텍스트가 있어서 Embedding과 LLM만 필요할 수 있다.

어떤 회사는 RAG 전체를 만들고 싶을 수 있다.

API가 나뉘어 있으면 필요한 것만 골라 쓸 수 있다.

```text id="kbpxjt"
문서 읽기만 필요
→ OCR API만 사용

문서 검색이 필요
→ Parse + Embedding 사용

문서 Q&A가 필요
→ Parse + Embedding + Solar LLM 사용
```

---

## 2. 각 단계 성능을 따로 개선할 수 있다

RAG 시스템에서 답변이 이상하면 원인이 하나가 아닐 수 있다.

```text id="apbcw1"
문서 파싱이 잘못됐나?
청킹이 이상한가?
임베딩 검색이 틀렸나?
LLM 프롬프트가 문제인가?
근거 확인이 부족한가?
```

API가 나뉘어 있으면 각 단계를 따로 테스트할 수 있다.

예를 들어:

```text id="wdkzdj"
OCR 결과만 확인
Embedding 검색 결과만 확인
Solar 답변만 확인
Groundedness 결과만 확인
```

이렇게 나눠서 보면 어디가 문제인지 찾기 쉽다.

---

## 3. DevOps 관점에서 모니터링하기 좋다

운영에서는 “전체 서비스가 느리다”보다 “어느 단계가 느린지”가 중요하다.

API가 단계별로 나뉘어 있으면 이런 식으로 볼 수 있다.

```text id="jmz7bj"
Document Parse latency
Embedding latency
Vector search latency
Solar LLM latency
Groundedness check latency
```

예를 들어 사용자가 “답변이 너무 느려요”라고 했을 때, 원인이 LLM인지, 벡터 검색인지, 문서 파싱인지 따로 봐야 한다.

DevOps 입장에서는 각 API 호출마다 이런 메트릭을 남기는 게 중요하다.

```text id="zqspvk"
요청 수
성공률
실패율
평균 latency
p95 latency
timeout 수
재시도 횟수
토큰 사용량
비용
```

---

## 4. 장애 대응이 쉬워진다

하나의 거대한 기능으로 묶여 있으면 어디서 터졌는지 찾기 어렵다.

하지만 API가 나뉘어 있으면 장애 범위를 좁힐 수 있다.

```text id="sinxtm"
OCR API 장애
→ 신규 문서 처리만 지연

Embedding API 장애
→ 신규 색인/검색 품질 영향

Solar LLM API 장애
→ 답변 생성 실패

Vector DB 장애
→ 검색 실패
```

이렇게 분리해서 보면 장애 대응도 더 현실적으로 할 수 있다.

---

# 면접에서는 이렇게 말하면 좋다

업스테이지가 API를 각자 만들었다는 말은, 문서 기반 AI 서비스에 필요한 기능을 하나의 통합 블랙박스로만 제공하는 것이 아니라, OCR, Document Parse, Embedding, Solar LLM, Information Extraction, Groundedness Checker처럼 단계별 API로 제공한다는 의미로 이해했습니다.

예를 들어 RAG 시스템을 만든다면 먼저 OCR이나 Document Parse API로 PDF나 이미지 문서를 구조화된 텍스트로 변환하고, 그 텍스트를 chunk로 나눈 뒤 Embedding API로 벡터화해서 벡터DB에 저장합니다. 이후 사용자의 질문도 임베딩해서 관련 chunk를 검색하고, 검색된 context를 Solar LLM API에 넣어 답변을 생성합니다. 필요하다면 Groundedness Checker로 답변이 실제 근거에 기반했는지도 확인할 수 있습니다.

DevOps 관점에서는 이 구조가 중요하다고 생각합니다. 각 기능이 API로 분리되어 있으면 단계별 latency, error rate, timeout, retry, token usage, 비용을 따로 모니터링할 수 있고, 장애가 났을 때 OCR 문제인지, embedding 문제인지, LLM 문제인지 빠르게 분리해서 볼 수 있기 때문입니다.

---

# 한 문장으로 정리하면

업스테이지가 API를 각자 만들었다는 건 **문서 AI와 RAG에 필요한 기능들을 OCR, Parse, Embedding, LLM, Groundedness 같은 독립 API로 나누어 제공한다는 뜻**이다.

그래서 개발자는 이 API들을 레고처럼 조립해서 서비스를 만든다.

```text id="s782ee"
문서를 읽는 API
+ 문장을 벡터로 바꾸는 API
+ 비슷한 문서를 찾는 벡터DB
+ 답변을 생성하는 LLM API
+ 답변 근거를 확인하는 API
= 문서 기반 AI 서비스 / RAG 서비스
```

결국 업스테이지의 API 구조를 이해한다는 건 단순히 “API 호출법을 안다”가 아니다.

**문서가 들어와서, 읽히고, 쪼개지고, 벡터화되고, 검색되고, 답변으로 생성되는 전체 파이프라인에서 각 API가 어느 위치에 붙는지 이해하는 것**이다.

[1]: https://github.com/UpstageAI/cookbook "GitHub - UpstageAI/cookbook: Upstage api examples and guides · GitHub"
[2]: https://console.upstage.ai/docs/capabilities/parse/document-ocr?utm_source=chatgpt.com "Extract Text from Scans | Upstage OCR API"
[3]: https://upstage.ai/products/document-parse "Upstage Document Parse"
[4]: https://upstage.ai/blog/en/building-rag-system-using-solar-llm-and-mongodb-atlas "Building end-to-end RAG system using Solar LLM and MongoDB Atlas"
