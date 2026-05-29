맞아. 순서는 거의 이렇게 보면 돼.

```text
문서
→ 청킹
→ 임베딩
→ 벡터화
→ 벡터DB 저장
→ 검색
→ LLM 답변 생성
```

근데 엄밀히 말하면 **임베딩 = 벡터화**에 가까워.
그래서 더 정확히 쓰면 이거야.

```text
문서 수집
→ 청킹
→ 임베딩(벡터화)
→ 벡터DB 저장
→ 검색
→ LLM 생성
```

---

# 1. 청킹이 뭐냐

청킹은 긴 문서를 작은 조각으로 자르는 거야.

예를 들어 PDF 하나가 이렇게 있다고 해보자.

```text
Upstage는 AI 기술을 활용하여 비즈니스 문제를 해결하는 회사입니다.
OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다.
Solar는 Upstage의 LLM입니다.
Document Parse는 문서를 구조화하는 기능입니다.
```

이걸 통째로 LLM이나 검색 시스템에 넣으면 너무 길고 비효율적이니까 조각으로 나눔.

```text
chunk 1:
Upstage는 AI 기술을 활용하여 비즈니스 문제를 해결하는 회사입니다.

chunk 2:
OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다.

chunk 3:
Solar는 Upstage의 LLM입니다.

chunk 4:
Document Parse는 문서를 구조화하는 기능입니다.
```

이게 청킹.

즉, **문서를 검색하기 좋은 단위로 쪼개는 작업**이야.

---

# 2. 임베딩/벡터화가 뭐냐

컴퓨터는 문장의 의미를 그대로 이해하지 못해.

그래서 문장을 숫자 배열로 바꿔야 해.

예를 들어:

```text
"OCR은 이미지에서 텍스트를 추출하는 기술이다"
```

이 문장을 임베딩 모델에 넣으면 이런 숫자 벡터가 나옴.

```text
[0.12, -0.45, 0.88, 0.03, ...]
```

이 숫자 배열이 벡터야.

이렇게 문장을 숫자 벡터로 바꾸는 과정이 **임베딩**이고, 말 그대로 표현하면 **벡터화**야.

그래서:

```text
임베딩한다 = 문장을 벡터로 바꾼다
벡터화한다 = 문장을 숫자 배열로 바꾼다
```

거의 같은 말로 봐도 돼.

---

# 3. 벡터DB 저장이 뭐냐

청크를 벡터로 바꿨으면 저장해야 해.

그냥 DB에 텍스트만 저장하는 게 아니라, 이런 식으로 저장함.

```json
{
  "chunk_id": 1,
  "text": "OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다.",
  "embedding": [0.12, -0.45, 0.88, 0.03],
  "metadata": {
    "source": "upstage_doc.pdf",
    "page": 3
  }
}
```

즉, 벡터DB에는 보통 이 세 가지가 들어감.

```text
원문 chunk
임베딩 vector
metadata
```

metadata는 출처, 페이지 번호, 문서 이름 같은 부가 정보야.

---

# 4. 사용자가 질문하면 어떻게 되냐

예를 들어 사용자가 이렇게 질문해.

```text
OCR API는 뭘 하는 거야?
```

그러면 이 질문도 임베딩함.

```text
"OCR API는 뭘 하는 거야?"
→ [0.11, -0.39, 0.91, 0.05, ...]
```

그리고 벡터DB 안에 있는 청크 벡터들과 비교함.

```text
질문 벡터
vs
chunk 1 벡터
chunk 2 벡터
chunk 3 벡터
...
```

가장 의미가 비슷한 chunk를 찾음.

예를 들면 이런 chunk가 검색됨.

```text
OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다.
OCR API는 문서를 입력받아 텍스트와 좌표, confidence score를 반환합니다.
```

그 다음 이 검색 결과를 LLM에게 같이 넣어줌.

```text
아래 문서를 참고해서 답변해줘.

[검색된 문서]
OCR API는 문서를 입력받아 텍스트와 좌표, confidence score를 반환합니다.

[질문]
OCR API는 뭘 하는 거야?
```

그러면 LLM이 답변을 생성함.

이 전체 구조가 RAG야.

---

# 그럼 “각자 API를 만들었다”는 게 뭐냐

이 말은 보통 RAG 파이프라인의 각 단계를 **분리된 기능/API endpoint로 만들었다**는 뜻이야.

예를 들어 하나의 백엔드 서버 안에 이런 API들을 만들어둘 수 있어.

```text
POST /documents/upload
→ 문서 업로드 API

POST /documents/chunk
→ 문서 청킹 API

POST /embeddings
→ 텍스트 임베딩 API

POST /vector-store/upsert
→ 벡터DB 저장 API

POST /search
→ 유사 문서 검색 API

POST /generate
→ LLM 답변 생성 API

POST /rag/query
→ 검색 + 생성 한 번에 처리하는 RAG API
```

즉, “RAG를 만들었다”가 내부적으로는 여러 기능으로 쪼개져 있을 수 있다는 말이야.

---

# 예시로 보면 더 쉬움

## 1. 문서 업로드 API

```http
POST /documents/upload
```

요청:

```text
file: upstage_intro.pdf
```

응답:

```json
{
  "document_id": "doc_001",
  "status": "uploaded"
}
```

이 API는 문서를 받아서 저장함.

---

## 2. 청킹 API

```http
POST /documents/doc_001/chunks
```

응답:

```json
{
  "document_id": "doc_001",
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "text": "Upstage는 AI 기술을 활용하여..."
    },
    {
      "chunk_id": "chunk_002",
      "text": "OCR은 이미지나 PDF에서..."
    }
  ]
}
```

이 API는 문서를 잘라서 chunk 목록을 만듦.

---

## 3. 임베딩 API

```http
POST /embeddings
```

요청:

```json
{
  "texts": [
    "OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다."
  ]
}
```

응답:

```json
{
  "embeddings": [
    [0.12, -0.45, 0.88, 0.03]
  ]
}
```

이 API는 텍스트를 숫자 벡터로 바꿔줌.

여기서 이 API는 내가 직접 모델을 띄워서 만든 API일 수도 있고, Upstage나 OpenAI 같은 외부 임베딩 API를 호출하는 wrapper일 수도 있어.

---

## 4. 벡터 저장 API

```http
POST /vector-store/upsert
```

요청:

```json
{
  "chunk_id": "chunk_001",
  "text": "OCR은 이미지나 PDF에서 텍스트를 추출하는 기술입니다.",
  "embedding": [0.12, -0.45, 0.88, 0.03],
  "metadata": {
    "document_id": "doc_001",
    "page": 1
  }
}
```

응답:

```json
{
  "status": "stored"
}
```

이 API는 벡터DB에 chunk와 embedding을 저장함.

---

## 5. 검색 API

```http
POST /search
```

요청:

```json
{
  "query": "OCR API는 뭐야?",
  "top_k": 3
}
```

내부 동작:

```text
질문을 임베딩함
→ 벡터DB에서 비슷한 chunk 검색
→ top_k개 반환
```

응답:

```json
{
  "results": [
    {
      "chunk_id": "chunk_002",
      "text": "OCR API는 문서에서 텍스트를 추출하는 API입니다.",
      "score": 0.91
    }
  ]
}
```

---

## 6. 답변 생성 API

```http
POST /generate
```

요청:

```json
{
  "question": "OCR API는 뭐야?",
  "context": [
    "OCR API는 문서에서 텍스트를 추출하는 API입니다."
  ]
}
```

응답:

```json
{
  "answer": "OCR API는 이미지나 PDF 문서에서 텍스트를 추출하고, 필요하면 좌표나 신뢰도까지 반환하는 API입니다."
}
```

이 API는 Solar 같은 LLM을 호출해서 답변을 생성함.

---

## 7. 최종 RAG API

실제 사용자는 위 과정을 하나하나 호출하지 않을 수도 있어.

사용자 입장에서는 그냥 이 API 하나만 호출함.

```http
POST /rag/query
```

요청:

```json
{
  "question": "OCR API는 뭐야?"
}
```

서버 내부에서는 자동으로 이렇게 돌림.

```text
질문 받기
→ 질문 임베딩
→ 벡터DB 검색
→ 관련 chunk 가져오기
→ Solar LLM API 호출
→ 답변 반환
```

응답:

```json
{
  "answer": "OCR API는 이미지나 PDF에서 텍스트를 추출하는 API입니다.",
  "sources": [
    {
      "document_id": "doc_001",
      "chunk_id": "chunk_002",
      "score": 0.91
    }
  ]
}
```

---

# 그러니까 “각자 API를 만들었다”의 의미

이 말은 이런 뜻일 가능성이 커.

```text
청킹하는 기능도 API로 만들고
임베딩하는 기능도 API로 만들고
검색하는 기능도 API로 만들고
생성하는 기능도 API로 만들었다
```

즉, RAG 시스템을 하나의 거대한 코드 덩어리로 만든 게 아니라, 각 기능을 호출 가능한 endpoint로 분리했다는 뜻.

예를 들면 FastAPI에서 이렇게 나눌 수 있음.

```python
@app.post("/chunk")
def chunk_document(request):
    ...

@app.post("/embed")
def embed_text(request):
    ...

@app.post("/search")
def search_documents(request):
    ...

@app.post("/generate")
def generate_answer(request):
    ...

@app.post("/rag/query")
def rag_query(request):
    ...
```

이렇게 하면 장점이 있어.

```text
각 단계별 테스트가 쉬움
어디서 실패했는지 찾기 쉬움
청킹만 바꿔보기 쉬움
임베딩 모델만 교체하기 쉬움
검색 성능만 따로 평가하기 쉬움
모니터링 지표를 단계별로 볼 수 있음
```

---

# 면접용으로 말하면 이렇게

> RAG 파이프라인은 문서를 청킹하고, 각 chunk를 임베딩해서 벡터DB에 저장한 뒤, 사용자 질문이 들어오면 질문도 임베딩해서 유사한 chunk를 검색하고, 그 검색 결과를 LLM에 context로 넣어 답변을 생성하는 구조입니다. 여기서 “각 단계별 API를 만들었다”는 것은 청킹, 임베딩, 검색, 생성 기능을 각각 독립적인 endpoint로 분리했다는 의미로 이해했습니다. 예를 들어 `/chunk`, `/embed`, `/search`, `/generate`, `/rag/query` 같은 API를 만들 수 있고, 이렇게 나누면 단계별 테스트와 모니터링, 장애 추적, 모델 교체가 쉬워집니다.

더 짧게 말하면:

> 청킹은 문서를 자르는 단계, 임베딩은 그 조각을 숫자 벡터로 바꾸는 단계, 검색은 질문 벡터와 비슷한 문서 벡터를 찾는 단계, 생성은 찾은 문서를 LLM에 넣어 답변을 만드는 단계입니다. 각자 API를 만들었다는 건 이 기능들을 하나의 코드 안에 뭉치지 않고, 각각 호출 가능한 API endpoint로 분리했다는 뜻입니다.
