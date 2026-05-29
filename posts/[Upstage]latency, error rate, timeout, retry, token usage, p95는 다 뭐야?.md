# latency, error rate, timeout, retry, token usage, p95는 다 뭐야?

API나 DevOps 공부를 하다 보면 이런 말을 자주 본다.

```text id="cdytsy"
latency
error rate
timeout
retry
token usage
p95
```

처음 보면 다 따로 노는 단어처럼 보인다.

그런데 이 단어들은 전부 **서비스가 안정적으로 잘 돌아가는지 확인하기 위한 운영 지표와 개념**이다.

특히 OCR API, Embedding API, LLM API 같은 외부 AI API를 붙일 때 자주 등장한다.

---

# 먼저 전체 흐름부터 보자

내 서비스가 Solar LLM API를 호출한다고 해보자.

```text id="6nzipj"
사용자 질문 입력
    ↓
내 백엔드 서버
    ↓
Solar LLM API 호출
    ↓
Solar가 답변 생성
    ↓
내 서버가 응답 받음
    ↓
사용자에게 답변 보여줌
```

이때 DevOps 입장에서는 단순히 “답변이 나왔다”만 보면 안 된다.

이런 것들을 봐야 한다.

```text id="3ufipn"
얼마나 빨리 응답했는가?
실패는 얼마나 나는가?
너무 오래 걸려서 끊긴 요청은 없는가?
실패했을 때 다시 시도했는가?
토큰을 얼마나 썼는가?
대부분 사용자는 빠른데 일부 사용자는 너무 느리지 않은가?
```

이 질문들이 각각 아래 개념으로 이어진다.

```text id="hvhsip"
얼마나 빨리 응답했는가? → latency
실패는 얼마나 나는가? → error rate
너무 오래 걸려서 끊겼는가? → timeout
실패했을 때 다시 시도했는가? → retry
토큰을 얼마나 썼는가? → token usage
대부분은 빠른데 일부는 느린가? → p95
```

---

# 1. latency란?

`latency`는 지연 시간이다.

쉽게 말하면 **요청을 보낸 뒤 응답이 돌아올 때까지 걸린 시간**이다.

예를 들어 사용자가 질문을 보냈다.

```text id="ny46rb"
질문: OCR API가 뭐야?
```

내 서버가 Solar LLM API를 호출했다.

```text id="bt3jnk"
요청 보냄: 10:00:00
응답 받음: 10:00:03
```

그러면 latency는 3초다.

```text id="80pe4c"
latency = 응답 받은 시간 - 요청 보낸 시간
latency = 3초
```

즉, latency가 낮을수록 빠른 서비스고, 높을수록 느린 서비스다.

---

# latency는 왜 중요할까?

사용자는 느린 서비스를 싫어한다.

특히 챗봇이나 검색 서비스는 몇 초만 늦어져도 답답하게 느껴진다.

예를 들어:

```text id="n7dr6l"
0.3초 → 빠름
1초 → 괜찮음
3초 → 조금 느림
10초 → 답답함
30초 → 장애처럼 느껴짐
```

LLM API는 일반 API보다 latency가 길 수 있다.

왜냐하면 모델이 답변을 생성하는 시간이 필요하기 때문이다.

```text id="85dtjm"
일반 게시글 조회 API
→ DB에서 꺼내오면 끝

LLM API
→ 입력 읽기
→ 답변 생성
→ 토큰 단위로 출력
```

그래서 LLM 서비스에서는 latency 모니터링이 아주 중요하다.

---

# 2. error rate란?

`error rate`는 에러율이다.

쉽게 말하면 **전체 요청 중 실패한 요청의 비율**이다.

예를 들어 100번 API를 호출했는데 5번 실패했다.

```text id="zmmzyl"
전체 요청 수: 100
실패 요청 수: 5
```

그러면 error rate는 5%다.

```text id="4cmhlz"
error rate = 실패 요청 수 / 전체 요청 수
error rate = 5 / 100 = 5%
```

에러는 여러 종류가 있다.

```text id="r3q6ac"
400 Bad Request
→ 요청 형식이 잘못됨

401 Unauthorized
→ 인증 실패

403 Forbidden
→ 권한 없음

404 Not Found
→ 없는 주소 호출

429 Too Many Requests
→ 요청 제한 초과

500 Internal Server Error
→ 서버 내부 오류

503 Service Unavailable
→ 서버 사용 불가
```

운영에서는 단순히 “에러가 났다”가 아니라, **어떤 에러가 얼마나 나는지** 봐야 한다.

---

# error rate는 왜 중요할까?

에러율이 높으면 사용자가 정상적으로 서비스를 쓰지 못한다.

예를 들어 LLM API 호출 1000번 중 200번이 실패하면 꽤 심각하다.

```text id="aam2ou"
전체 요청: 1000
실패 요청: 200
error rate: 20%
```

이건 사용자 5명 중 1명은 실패를 경험할 수 있다는 뜻이다.

에러율이 갑자기 올라가면 이런 원인을 의심할 수 있다.

```text id="ld0koh"
API Key 만료
요청 형식 변경
외부 API 장애
rate limit 초과
네트워크 문제
서버 배포 오류
토큰 길이 초과
```

그래서 DevOps에서는 error rate를 알림 조건으로 자주 쓴다.

```text id="fksoj5"
5분 동안 error rate가 5% 이상이면 알림
10분 동안 500 에러가 급증하면 알림
429 에러가 늘면 rate limit 확인
```

---

# 3. timeout이란?

`timeout`은 **정해진 시간 안에 응답이 오지 않아서 요청을 끊는 것**이다.

예를 들어 내 서버가 외부 API를 호출할 때 이렇게 정했다고 하자.

```text id="wo1jyl"
최대 10초까지만 기다린다.
```

그런데 API 응답이 10초 안에 안 왔다.

```text id="ois602"
요청 보냄
1초...
2초...
3초...
...
10초...
응답 없음
```

그러면 내 서버는 더 이상 기다리지 않고 요청을 실패 처리한다.

이게 timeout이다.

```text id="ya8854"
10초 안에 응답이 안 오면 끊는다
→ timeout
```

---

# timeout은 왜 필요할까?

그냥 계속 기다리면 안 될까?

안 된다.

계속 기다리면 서버 자원이 묶인다.

예를 들어 요청 하나가 계속 안 끝나면, 그 요청을 처리하던 스레드나 커넥션이 계속 점유된다.

이런 요청이 많아지면 서버 전체가 느려질 수 있다.

```text id="w6gzid"
외부 API 응답 지연
→ 내 서버 요청들이 계속 대기
→ 커넥션/스레드 고갈
→ 전체 서비스 장애
```

그래서 timeout은 방어 장치다.

```text id="din18q"
너무 오래 걸리는 요청은 끊고
사용자에게 실패 응답을 주거나
나중에 다시 처리하게 만든다
```

LLM이나 OCR API는 처리 시간이 길 수 있기 때문에 timeout 설정이 특히 중요하다.

---

# 4. retry란?

`retry`는 재시도다.

API 호출이 실패했을 때, 바로 포기하지 않고 다시 요청하는 것이다.

예를 들어 외부 API 호출이 네트워크 문제로 한 번 실패했다.

```text id="6ne11r"
1번째 요청 → 실패
2번째 요청 → 성공
```

이때 2번째 요청을 retry라고 한다.

왜 재시도가 필요할까?

일부 에러는 순간적인 문제일 수 있기 때문이다.

```text id="eeu2nd"
네트워크 순간 끊김
외부 API 일시적 과부하
잠깐 발생한 502/503
일시적 timeout
```

이런 경우에는 잠깐 뒤에 다시 요청하면 성공할 수 있다.

---

# retry를 무조건 많이 하면 좋을까?

아니다.

재시도를 무식하게 많이 하면 오히려 장애를 키울 수 있다.

예를 들어 외부 API가 이미 힘든 상태다.

그런데 모든 서버가 실패할 때마다 계속 재시도한다.

```text id="4w1weo"
요청 실패
→ 재시도
→ 또 실패
→ 또 재시도
→ 외부 API 더 과부하
→ 장애 악화
```

그래서 retry는 조심해서 해야 한다.

보통은 이런 식으로 한다.

```text id="fg7ktz"
최대 3번까지만 재시도
재시도 사이에 대기 시간 둠
같은 간격이 아니라 점점 늘림
```

예를 들면:

```text id="z8wui3"
1번째 실패
→ 1초 후 재시도

2번째 실패
→ 2초 후 재시도

3번째 실패
→ 4초 후 재시도
```

이렇게 재시도 간격을 점점 늘리는 방식을 **exponential backoff**라고 한다.

---

# 재시도하면 안 되는 에러도 있다

모든 에러가 retry 대상은 아니다.

예를 들어 API Key가 틀렸다.

```text id="cbhq8d"
401 Unauthorized
```

이건 다시 요청해도 계속 실패한다.

요청 형식이 잘못됐다.

```text id="20is2m"
400 Bad Request
```

이것도 재시도한다고 해결되지 않는다.

반면 이런 에러는 재시도를 고려할 수 있다.

```text id="97yqa8"
timeout
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
일시적 네트워크 오류
```

그래서 retry 정책은 이렇게 나눠야 한다.

```text id="71eikh"
재시도 가능
→ 일시적 장애, timeout, 5xx 일부

재시도 불필요
→ 인증 실패, 권한 없음, 요청 형식 오류
```

---

# 5. token usage란?

`token usage`는 LLM API에서 사용한 토큰 양이다.

LLM은 문장을 글자 단위로 그대로 보는 게 아니라, token이라는 단위로 나눠서 처리한다.

예를 들어:

```text id="eg1q2v"
OCR API가 뭐야?
```

이 문장은 내부적으로 몇 개의 토큰으로 쪼개져 처리된다.

정확한 쪼개짐은 모델마다 다르지만, 중요한 건 이거다.

```text id="bydvqx"
입력이 길수록 token이 많아진다
출력이 길수록 token이 많아진다
token이 많을수록 비용과 시간이 늘 수 있다
```

LLM API 응답에는 보통 이런 정보가 들어간다.

```json id="xrm99x"
{
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 300,
    "total_tokens": 1500
  }
}
```

뜻은 이렇다.

```text id="35791o"
prompt_tokens
→ 입력에 사용된 토큰 수

completion_tokens
→ 모델이 답변 생성에 사용한 토큰 수

total_tokens
→ 전체 사용 토큰 수
```

---

# token usage는 왜 중요할까?

LLM API는 보통 토큰 사용량이 비용과 연결된다.

RAG에서는 특히 token usage가 커질 수 있다.

왜냐하면 질문만 보내는 게 아니라, 검색된 문서 chunk도 같이 보내기 때문이다.

예를 들어:

```text id="fn4oxa"
사용자 질문:
OCR API가 뭐야?

검색된 문서 context:
chunk 1...
chunk 2...
chunk 3...
chunk 4...
chunk 5...
```

이렇게 context를 많이 넣으면 prompt_tokens가 증가한다.

그래서 운영에서는 이런 고민을 해야 한다.

```text id="lv9dls"
chunk를 몇 개까지 넣을까?
각 chunk 길이를 얼마나 줄일까?
max_tokens를 얼마로 제한할까?
긴 문서는 요약해서 넣을까?
사용자별 사용량 제한을 둘까?
```

token usage를 안 보면 비용이 갑자기 커질 수 있다.

```text id="uipmj5"
프롬프트가 길어짐
→ prompt_tokens 증가
→ 응답 시간 증가
→ 비용 증가
```

그래서 LLM 서비스에서는 token usage가 운영 지표가 된다.

---

# 6. p95란?

`p95`는 95퍼센타일이다.

말이 어렵지만 쉽게 말하면 **전체 요청 중 95%가 이 시간 안에 끝났다는 기준값**이다.

예를 들어 API 요청 100개가 있다고 하자.

각 요청의 latency를 빠른 순서대로 정렬한다.

```text id="s5zcg5"
1번 요청: 0.1초
2번 요청: 0.2초
3번 요청: 0.2초
...
95번 요청: 2.8초
...
100번 요청: 10초
```

이때 95번째 요청의 latency가 p95 latency다.

```text id="g70m2b"
p95 latency = 2.8초
```

이 말은:

```text id="z9axme"
전체 요청의 95%는 2.8초 안에 끝났다
나머지 5%는 2.8초보다 오래 걸렸다
```

라는 뜻이다.

---

# 평균 latency만 보면 안 되는 이유

평균만 보면 문제가 숨을 수 있다.

예를 들어 요청 10개의 latency가 이렇다고 하자.

```text id="ul1ipl"
0.5초
0.5초
0.5초
0.5초
0.5초
0.5초
0.5초
0.5초
0.5초
10초
```

평균은:

```text id="43n950"
(0.5*9 + 10) / 10 = 1.45초
```

평균만 보면 “나쁘지 않은데?”라고 생각할 수 있다.

하지만 실제로는 한 사용자가 10초를 기다렸다.

운영에서는 이런 느린 요청들이 중요하다.

이걸 tail latency라고도 볼 수 있다.

그래서 p95, p99 같은 지표를 본다.

```text id="5xu2do"
p50
→ 절반의 요청이 이 시간 안에 끝남

p95
→ 95%의 요청이 이 시간 안에 끝남

p99
→ 99%의 요청이 이 시간 안에 끝남
```

LLM API에서는 평균보다 p95가 더 중요할 때가 많다.

왜냐하면 대부분은 괜찮아도 일부 요청이 너무 오래 걸리면 사용자 경험이 망가지기 때문이다.

---

# 이 지표들은 서로 연결되어 있다

이 개념들은 따로따로가 아니다.

예를 들어 Solar LLM API latency가 증가한다.

```text id="55fiwb"
latency 증가
```

그러면 timeout이 늘 수 있다.

```text id="z1u3xf"
응답이 늦음
→ 설정한 시간 안에 못 받음
→ timeout 증가
```

timeout이 늘면 error rate도 증가한다.

```text id="zrwdab"
timeout 증가
→ 실패 요청 증가
→ error rate 증가
```

실패가 늘면 retry가 발생한다.

```text id="yqhof7"
실패
→ retry
→ 요청 수 증가
```

retry가 너무 많으면 외부 API가 더 힘들어진다.

```text id="e38ztf"
retry 증가
→ API 호출량 증가
→ 더 느려짐
→ latency 더 증가
```

RAG context를 너무 많이 넣으면 token usage가 증가한다.

```text id="1p5ybz"
context 길어짐
→ prompt token 증가
→ 처리 시간 증가
→ latency 증가
→ 비용 증가
```

그래서 운영에서는 이런 식으로 같이 본다.

```text id="cbdzkv"
token usage가 늘었나?
→ latency도 늘었나?
→ timeout도 늘었나?
→ error rate도 늘었나?
→ retry가 장애를 키우고 있나?
```

---

# 예시: RAG 서비스에서 문제가 생겼을 때

문서 Q&A 서비스가 있다고 해보자.

사용자가 질문하면 내부에서는 이렇게 돈다.

```text id="f2sh6o"
질문 입력
→ 질문 임베딩
→ 벡터 검색
→ context 구성
→ Solar LLM API 호출
→ 답변 반환
```

어느 날 사용자가 말한다.

```text id="tljzl4"
답변이 너무 느려요.
가끔 실패해요.
```

이때 DevOps는 감으로 보면 안 된다.

지표를 봐야 한다.

```text id="faxczq"
1. latency 확인
   → 전체적으로 느린가?

2. p95 latency 확인
   → 일부 요청만 심하게 느린가?

3. error rate 확인
   → 실패율이 올라갔는가?

4. timeout 확인
   → 오래 걸려서 끊긴 요청이 많은가?

5. retry 확인
   → 재시도가 과하게 발생하고 있는가?

6. token usage 확인
   → 프롬프트가 너무 길어졌는가?
```

이렇게 봐야 원인을 좁힐 수 있다.

예를 들어 token usage가 갑자기 늘었다.

```text id="55x66m"
평균 total_tokens 1,500
→ 평균 total_tokens 7,000
```

그럼 원인은 RAG context를 너무 많이 넣었을 수 있다.

```text id="zgy1wx"
검색 chunk 개수 증가
chunk 크기 증가
프롬프트 템플릿 변경
대화 히스토리를 너무 많이 포함
```

그러면 해결은 이런 식이다.

```text id="pxfjlk"
top_k 줄이기
chunk 크기 조정
대화 히스토리 요약
max_tokens 제한
긴 문서 context 압축
```

---

# 면접에서는 이렇게 말하면 좋다

DevOps 관점에서 LLM API나 OCR API를 운영할 때는 단순히 호출 성공 여부만 보는 것이 아니라, latency, error rate, timeout, retry, token usage, p95 latency 같은 지표를 함께 봐야 한다고 생각합니다.

latency는 요청 후 응답까지 걸린 시간이고, error rate는 전체 요청 중 실패한 비율입니다. timeout은 정해진 시간 안에 응답이 오지 않아 요청을 끊는 것이고, retry는 일시적 실패에 대해 다시 시도하는 전략입니다. token usage는 LLM API에서 입력과 출력에 사용된 토큰 수로, 비용과 지연 시간에 직접적인 영향을 줄 수 있습니다. p95 latency는 전체 요청 중 95%가 어느 시간 안에 끝났는지를 보여주는 지표로, 평균으로는 보이지 않는 느린 요청을 파악하는 데 유용합니다.

특히 RAG 서비스에서는 context를 많이 넣으면 token usage가 증가하고, 그로 인해 latency와 비용이 늘 수 있습니다. latency가 길어지면 timeout이 증가하고, timeout이 많아지면 error rate가 올라가며, retry가 과도하면 오히려 장애를 키울 수 있기 때문에 이 지표들을 연결해서 보는 것이 중요하다고 생각합니다.

---

# 한 문장으로 정리하면

```text id="d84nmu"
latency     → 얼마나 느린가
error rate  → 얼마나 실패하는가
timeout     → 너무 오래 걸려서 끊겼는가
retry       → 실패 후 다시 시도했는가
token usage → LLM 토큰을 얼마나 썼는가
p95         → 대부분은 괜찮아도 느린 요청이 얼마나 심한가
```

이 지표들은 전부 “서비스가 잘 살아있고, 사용자에게 안정적으로 응답하고 있는지”를 보기 위한 도구다.

DevOps는 이 값들을 보고 판단한다.

```text id="d2s64t"
지금 장애인가?
느린 원인이 어디인가?
재시도를 더 해야 하나, 줄여야 하나?
비용이 왜 늘었나?
사용자가 체감하는 속도는 괜찮은가?
```

결국 운영에서 중요한 건 하나다.

**서버가 켜져 있는가가 아니라, 사용자가 안정적으로 쓸 수 있는가**를 보는 것이다.
