---
title: "[알고리즘] 버킷 소트(Bucket Sort)란? — O(n) 정렬이 가능한 이유"
source: "https://velog.io/@yorange50/알고리즘-버킷-소트Bucket-Sort란-On-정렬이-가능한-이유"
published: "2026-05-11T06:12:25.516Z"
tags: ""
backup_date: "2026-05-29T14:52:52.766043"
---

코딩테스트를 풀다 보면 이런 말을 자주 본다.

```text
정렬하면 O(n log n)
버킷 소트 쓰면 O(n)
```

특히:

* Top K Frequent Elements
* Counting 문제
* Frequency 기반 문제

에서 자주 등장한다.

처음 보면:

```text
"아니 정렬이 어떻게 O(n)이 나와?"
```

싶다.

오늘은 버킷 소트가 왜 빠른지,
언제 쓰는지,
그리고 실제 코테에서 어떻게 활용되는지 정리해보자.

---

# 1. 일반 정렬의 한계

보통 우리는 이렇게 정렬한다.

```python
nums = [5, 1, 4, 2]

nums.sort()
```

내부적으로는:

* TimSort
* QuickSort
* MergeSort

같은 비교 기반 정렬이 사용된다.

비교 기반 정렬은 평균적으로:

```text
O(n log n)
```

보다 빨라질 수 없다.

왜냐면:

```text
1과 5 비교
2와 4 비교
...
```

계속 "비교"를 해야 하기 때문이다.

---

# 2. 그런데 버킷 소트는 비교를 안 한다

버킷 소트 핵심은:

```text
"값을 특정 칸(bucket)에 바로 넣는다"
```

이다.

예를 들어:

```python
nums = [3, 1, 2, 3, 2]
```

이 있을 때:

```text
1은 1번 칸
2는 2번 칸
3은 3번 칸
```

이런 식으로 바로 넣는다.

즉:

```text
비교 X
위치 계산 O
```

이 차이 때문에 빨라진다.

---

# 3. 가장 쉬운 예시 — Counting Sort 느낌

예를 들어 숫자 범위가 작다고 해보자.

```python
nums = [4, 2, 2, 1, 3]
```

우리는 배열 하나를 만든다.

```python
bucket = [0] * 5
```

의미:

```text
index = 숫자
value = 등장 횟수
```

초기 상태:

```text
[0, 0, 0, 0, 0]
```

숫자 세기:

```python
for num in nums:
    bucket[num] += 1
```

결과:

```text
[0, 1, 2, 1, 1]
```

의미:

```text
1 → 1번 등장
2 → 2번 등장
3 → 1번 등장
4 → 1번 등장
```

이제 순서대로 꺼내면 정렬 끝.

---

# 4. 왜 O(n)인가?

흐름을 보자.

## 숫자 세기

```python
for num in nums:
```

→ O(n)

## bucket 순회

```python
for i in range(len(bucket)):
```

→ O(k)

(k = 숫자 범위)

그래서 전체:

```text
O(n + k)
```

숫자 범위가 작으면 거의 O(n)에 가까워진다.

---

# 5. 코테에서 자주 나오는 형태

진짜 중요한 건 이 부분이다.

버킷 소트는 "정렬용"보다:

```text
빈도(Frequency) 문제
```

에서 엄청 많이 나온다.

대표 문제:

```text
Top K Frequent Elements
```

예시:

```python
nums = [1,1,1,2,2,3]
k = 2
```

등장 횟수:

```text
1 -> 3번
2 -> 2번
3 -> 1번
```

우리는:

```text
빈도 기준 정렬
```

을 해야 한다.

---

# 6. 일반 정렬 풀이

보통 이렇게 푼다.

```python
dictt = {}

for num in nums:
    dictt[num] = dictt.get(num, 0) + 1

arr = sorted(dictt.items(), key=lambda x:x[1], reverse=True)
```

하지만 여기서:

```python
sorted(...)
```

때문에:

```text
O(n log n)
```

이 나온다.

---

# 7. 버킷 소트 풀이

핵심 아이디어:

```text
등장 횟수를 index로 사용
```

예를 들어:

```text
3번 등장한 숫자들
2번 등장한 숫자들
1번 등장한 숫자들
```

이렇게 묶는다.

코드:

```python
class Solution:
    def topKFrequent(self, nums, k):

        count = {}

        for num in nums:
            count[num] = count.get(num, 0) + 1

        bucket = [[] for _ in range(len(nums) + 1)]

        for num, freq in count.items():
            bucket[freq].append(num)

        result = []

        for freq in range(len(bucket)-1, 0, -1):

            for num in bucket[freq]:
                result.append(num)

                if len(result) == k:
                    return result
```

---

# 8. 왜 빠른가?

여기서는:

```text
정렬을 안 했다
```

대신:

```text
빈도별 칸에 넣었다
```

그래서:

```text
count 계산 → O(n)
bucket 채우기 → O(n)
bucket 순회 → O(n)
```

전체:

```text
O(n)
```

---

# 9. 단점도 있다

버킷 소트는 무조건 좋은 게 아니다.

## 메모리를 더 쓴다

```python
bucket = [[] for _ in range(len(nums)+1)]
```

이런 추가 공간 필요.

즉:

```text
공간복잡도 O(n)
```

## 범위가 너무 크면 비효율적

예를 들어:

```text
1 ~ 10억
```

이런 숫자 범위면 bucket 생성 자체가 불가능하다.

그래서:

```text
범위가 제한적일 때
```

강력하다.

---

# 10. 언제 버킷 소트를 떠올려야 하나?

이 키워드 나오면 의심해보자.

```text
빈도
frequency
top k
counting
등장 횟수
숫자 범위 제한
```

특히:

```text
Top K Frequent
```

는 거의 대표적인 버킷 소트 문제다.

---

# 마무리

버킷 소트 핵심은 하나다.

```text
비교하지 말고 위치로 분류하자
```

그래서:

```text
비교 기반 정렬 O(n log n)
```

을 넘어서:

```text
O(n)
```

에 가까운 성능을 만들 수 있다.

코테에서는 특히:

* 빈도 계산
* Top K
* Counting 문제

에서 엄청 자주 등장하므로 꼭 익숙해지는 게 좋다.
