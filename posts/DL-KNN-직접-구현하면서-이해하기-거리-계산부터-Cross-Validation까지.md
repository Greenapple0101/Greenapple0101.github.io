---
title: "[Pytorch] KNN 직접 구현하면서 이해하기: 거리 계산부터 Cross Validation까지"
source: "https://velog.io/@yorange50/DL-KNN-직접-구현하면서-이해하기-거리-계산부터-Cross-Validation까지"
published: "2026-05-07T03:53:25.584Z"
tags: ""
backup_date: "2026-05-29T14:52:52.773941"
---

PyTorch로 **K-Nearest Neighbor, KNN 분류기**를 직접 구현해보았다.

KNN은 머신러닝 알고리즘 중에서도 구조가 꽤 단순한 편이다.
학습 단계에서 모델이 가중치를 업데이트하지 않는다.
대신 학습 데이터를 그대로 기억해두고, 새로운 데이터가 들어오면 기존 데이터들과의 거리를 계산해서 가장 가까운 이웃들의 라벨을 보고 예측한다.

즉 KNN의 핵심은 다음과 같다.

```text
1. 학습 데이터를 저장한다.
2. 테스트 데이터와 학습 데이터 사이의 거리를 계산한다.
3. 가장 가까운 k개의 학습 데이터를 찾는다.
4. 그 k개가 가진 라벨 중 가장 많은 라벨을 예측값으로 사용한다.
```

---

## 1. KNN은 “학습”보다 “비교”가 핵심이다

보통 딥러닝 모델은 학습 과정에서 weight를 업데이트한다.
하지만 KNN은 다르다.

```python
self.x_train = x_train.view(x_train.shape[0], -1)
self.y_train = y_train
```

`KnnClassifier`의 생성자를 보면 학습 데이터를 그냥 저장한다.
여기서 중요한 점은 이미지 데이터를 그대로 비교하기 어렵기 때문에 먼저 펼쳐준다는 것이다.

예를 들어 CIFAR-10 이미지는 보통 다음과 같은 형태다.

```text
(num_data, 3, 32, 32)
```

여기서 `3`은 RGB 채널이고, `32 x 32`는 이미지 크기다.

KNN에서는 이미지의 공간 구조를 따로 학습하지 않는다.
그냥 하나의 긴 벡터로 펼쳐서 비교한다.

```text
(3, 32, 32) → (3072)
```

즉 이미지 한 장을 3072개의 숫자로 이루어진 벡터로 보는 것이다.

---

## 2. 거리 계산 구현 1: Two Loops

가장 직관적인 방식은 학습 데이터와 테스트 데이터를 하나씩 비교하는 것이다.

```python
for i in range(num_train):
    for j in range(num_test):
        dists[i, j] = torch.sum((x_train_flat[i] - x_test_flat[j]) ** 2)
```

이 방식은 이해하기 쉽다.

```text
학습 데이터 1번과 테스트 데이터 1번 거리 계산
학습 데이터 1번과 테스트 데이터 2번 거리 계산
...
학습 데이터 N번과 테스트 데이터 M번 거리 계산
```

거리 계산식은 제곱 유클리드 거리다.

```text
distance = sum((x_train - x_test)^2)
```

하지만 문제는 느리다는 것이다.
학습 데이터가 5만 개, 테스트 데이터가 1만 개라면 반복문이 엄청 많이 돈다.

```text
num_train × num_test 만큼 반복
```

그래서 이 방식은 “원리를 이해하기 위한 구현”에 가깝다.

---

## 3. 거리 계산 구현 2: One Loop

두 번째 방식은 반복문을 하나만 사용한다.

```python
for i in range(num_train):
    dists[i] = torch.sum((x_train_flat[i] - x_test_flat) ** 2, dim=1)
```

여기서는 학습 데이터 하나를 잡고, 모든 테스트 데이터와의 거리를 한 번에 계산한다.

즉 구조가 이렇게 바뀐다.

```text
Two Loops:
학습 데이터 i 하나, 테스트 데이터 j 하나씩 비교

One Loop:
학습 데이터 i 하나, 모든 테스트 데이터와 한 번에 비교
```

PyTorch의 텐서 연산을 활용하기 때문에 훨씬 빠르다.
반복문이 하나 줄어들었고, 내부 계산은 PyTorch가 벡터화해서 처리한다.

---

## 4. 거리 계산 구현 3: No Loops

가장 중요한 구현은 반복문을 아예 없앤 방식이다.

```python
x_train_squared = torch.sum(x_train_flat ** 2, dim=1).view(-1, 1)
x_test_squared = torch.sum(x_test_flat ** 2, dim=1).view(1, -1)

dists = x_train_squared + x_test_squared - 2 * torch.mm(x_train_flat, x_test_flat.t())
```

여기서는 다음 공식을 사용한다.

```text
(x - y)^2 = x^2 + y^2 - 2xy
```

벡터 거리로 보면 다음과 같다.

```text
||x - y||^2 = ||x||^2 + ||y||^2 - 2xy
```

이 방식이 중요한 이유는 모든 학습 데이터와 모든 테스트 데이터 사이의 거리를 행렬 연산 한 번으로 계산할 수 있기 때문이다.

결과로 나오는 `dists`의 shape는 다음과 같다.

```text
(num_train, num_test)
```

즉 `dists[i, j]`는 다음 의미다.

```text
i번째 학습 데이터와 j번째 테스트 데이터 사이의 거리
```

---

## 5. predict_labels: 가까운 k개를 보고 라벨 예측하기

거리 계산이 끝났다면 이제 예측을 해야 한다.

```python
_, knn_indices = torch.topk(dists[:, i], k=k, largest=False)
```

여기서 `dists[:, i]`는 i번째 테스트 데이터와 모든 학습 데이터 사이의 거리다.

`torch.topk(..., largest=False)`를 사용하면 가장 작은 거리, 즉 가장 가까운 데이터 k개를 찾을 수 있다.

```python
knn_labels = y_train[knn_indices]
y_pred[i] = knn_labels.bincount().argmax()
```

가까운 k개의 라벨을 가져온 뒤, 가장 많이 등장한 라벨을 예측값으로 사용한다.

예를 들어 k=5이고 가까운 이웃들의 라벨이 다음과 같다면,

```text
[3, 3, 5, 3, 1]
```

가장 많이 나온 라벨은 `3`이므로 예측값은 `3`이 된다.

이게 KNN의 majority voting이다.

---

## 6. KnnClassifier 클래스 구조

코드에서는 KNN을 함수만으로 구현하지 않고, 클래스로도 정리했다.

```python
class KnnClassifier:
```

이 클래스는 크게 세 가지 역할을 한다.

```text
1. 학습 데이터 저장
2. 테스트 데이터 예측
3. 정확도 계산
```

---

## 7. **init**: 학습 데이터를 기억하기

```python
def __init__(self, x_train, y_train):
    self.x_train = x_train.view(x_train.shape[0], -1)
    self.y_train = y_train
```

KNN은 별도의 학습 과정이 없기 때문에 생성자에서 데이터를 저장하는 것이 사실상 학습이다.

여기서도 이미지를 1차원 벡터로 펼친다.

```text
이미지 텐서 → 벡터
```

KNN은 CNN처럼 이미지의 위치 정보나 패턴을 학습하지 않는다.
그냥 숫자 벡터끼리 거리가 가까운지를 본다.

---

## 8. predict: 테스트 데이터 예측하기

```python
dists = torch.cdist(x_test, self.x_train, p=2)
```

여기서는 직접 거리 공식을 구현하지 않고 `torch.cdist`를 사용했다.

`torch.cdist`는 두 텐서 사이의 pairwise distance를 계산해준다.

```text
x_test와 x_train 사이의 모든 거리 계산
```

그다음 가까운 k개를 찾는다.

```python
knn_indices = torch.topk(dists, k=k, dim=1, largest=False).indices
```

그리고 해당 인덱스의 라벨을 가져온다.

```python
knn_labels = self.y_train[knn_indices]
```

마지막으로 가장 많이 등장한 라벨을 선택한다.

```python
y_test_pred = torch.mode(knn_labels, dim=1).values
```

즉 전체 흐름은 다음과 같다.

```text
테스트 데이터 입력
→ 학습 데이터와 거리 계산
→ 가장 가까운 k개 찾기
→ k개 라벨 확인
→ 가장 많이 나온 라벨로 예측
```

---

## 9. check_accuracy: 예측 정확도 확인하기

```python
y_test_pred = self.predict(x_test, k=k)
num_correct = (y_test == y_test_pred).sum().item()
accuracy = 100.0 * num_correct / num_samples
```

정확도 계산은 단순하다.

```text
맞춘 개수 / 전체 개수 × 100
```

예를 들어 100개 중 35개를 맞췄다면 정확도는 35%다.

```python
print(f"Got {num_correct} / {num_samples} correct; accuracy is {accuracy:.2f}%")
```

이 함수는 모델이 어느 정도 맞추는지 바로 확인할 수 있게 해준다.

---

## 10. Cross Validation: 좋은 k 찾기

KNN에서 가장 중요한 하이퍼파라미터는 `k`다.

```text
k = 몇 개의 이웃을 볼 것인가?
```

k가 너무 작으면 주변 데이터 하나하나에 민감해진다.
k가 너무 크면 너무 많은 이웃을 참고해서 애매한 예측을 할 수 있다.

그래서 여러 k를 실험해보고 가장 좋은 k를 골라야 한다.

코드에서는 다음 k 후보들을 사용한다.

```python
k_choices = [1, 3, 5, 8, 10, 12, 15, 20, 50, 100]
```

---

## 11. knn_cross_validate 구조

```python
x_train_folds = torch.chunk(x_train, num_folds)
y_train_folds = torch.chunk(y_train, num_folds)
```

먼저 학습 데이터를 여러 조각으로 나눈다.
기본값은 5개 fold다.

```text
전체 학습 데이터
→ fold 1
→ fold 2
→ fold 3
→ fold 4
→ fold 5
```

그다음 각 fold를 한 번씩 검증 데이터로 사용한다.

예를 들어 5-fold cross validation이면 다음과 같다.

```text
1회차: fold 1 검증, fold 2~5 학습
2회차: fold 2 검증, fold 1,3,4,5 학습
3회차: fold 3 검증, fold 1,2,4,5 학습
4회차: fold 4 검증, fold 1,2,3,5 학습
5회차: fold 5 검증, fold 1~4 학습
```

이 과정을 각 k마다 반복한다.

```python
for k in k_choices:
    for fold in range(num_folds):
```

즉 `k=1`일 때 5번 평가하고,
`k=3`일 때 5번 평가하고,
`k=5`일 때 5번 평가하는 식이다.

결과는 다음 형태로 저장된다.

```python
k_to_accuracies[k].append(accuracy)
```

예시로 보면 이런 느낌이다.

```text
{
  1: [0.25, 0.27, 0.26, 0.24, 0.28],
  3: [0.29, 0.30, 0.28, 0.31, 0.29],
  5: [0.30, 0.32, 0.31, 0.29, 0.30]
}
```

---

## 12. knn_get_best_k: 가장 좋은 k 선택하기

교차검증 결과가 나오면 평균 정확도가 가장 높은 k를 선택한다.

```python
mean_accuracy = sum(accuracies) / len(accuracies)
```

그리고 현재까지 가장 좋은 평균 정확도와 비교한다.

```python
if mean_accuracy > best_mean_accuracy:
    best_k = k
```

만약 평균 정확도가 같다면 더 작은 k를 고른다.

```python
or (mean_accuracy == best_mean_accuracy and k < best_k)
```

이 기준은 과제 조건에도 맞고, 너무 큰 k를 불필요하게 선택하지 않게 해준다.

---

## 13. 전체 흐름 정리

이번 KNN 구현의 전체 흐름은 다음과 같다.

```text
1. 이미지 데이터를 벡터로 펼친다.
2. 학습 데이터와 테스트 데이터 사이의 거리를 계산한다.
3. 가까운 k개의 학습 데이터를 찾는다.
4. 그 라벨들 중 가장 많이 나온 라벨을 예측값으로 사용한다.
5. 정확도를 계산한다.
6. cross validation으로 가장 좋은 k를 고른다.
```

함수 기준으로 보면 이렇게 나눌 수 있다.

| 함수/클래스                        | 역할                    |
| ----------------------------- | --------------------- |
| `compute_distances_two_loops` | 이중 반복문으로 거리 계산        |
| `compute_distances_one_loop`  | 반복문 하나와 벡터 연산으로 거리 계산 |
| `compute_distances_no_loops`  | 행렬 연산으로 거리 계산         |
| `predict_labels`              | 가까운 k개의 라벨로 예측        |
| `KnnClassifier`               | KNN 분류기 클래스           |
| `check_accuracy`              | 예측 정확도 계산             |
| `knn_cross_validate`          | 여러 k에 대해 교차검증         |
| `knn_get_best_k`              | 가장 좋은 k 선택            |

---

## 14. 핵심은 “알고리즘”보다 “벡터화”였다

처음에는 KNN 자체가 핵심처럼 보인다.
하지만 코드를 뜯어보면 더 중요한 포인트가 있다.

바로 **같은 계산을 얼마나 효율적으로 하느냐**다.

Two loops 방식은 이해하기 쉽지만 느리다.
One loop 방식은 조금 더 빠르다.
No loops 방식은 행렬 연산을 활용해서 훨씬 효율적이다.

즉 이번 구현의 진짜 학습 포인트는 이거다.

```text
KNN의 원리 이해
+ PyTorch 텐서 연산 방식 이해
+ 반복문을 벡터화로 바꾸는 감각 익히기
```

딥러닝이나 머신러닝 코드를 짤 때는 단순히 답이 맞는 코드보다,
데이터가 커져도 감당 가능한 코드가 중요하다.

그래서 KNN은 단순한 알고리즘이지만,
텐서 연산과 벡터화 감각을 익히기에 좋은 예제라고 볼 수 있다.
