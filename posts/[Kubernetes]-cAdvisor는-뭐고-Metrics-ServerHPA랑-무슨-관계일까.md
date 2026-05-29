---
title: "[KUBERNETES] cAdvisor는 뭐고, Metrics Server/HPA랑 무슨 관계일까?"
source: "https://velog.io/@yorange50/KUBERNETES-cAdvisor는-뭐고-Metrics-ServerHPA랑-무슨-관계일까"
published: "2026-05-19T11:22:19.454Z"
tags: ""
backup_date: "2026-05-29T14:52:52.721514"
---

Kubernetes에서 리소스 모니터링을 공부하다 보면 `cAdvisor`, `Metrics Server`, `kubectl top`, `HPA` 같은 단어가 같이 나온다. 처음 보면 다 비슷하게 “CPU랑 Memory 보는 것”처럼 느껴지는데, 실제로는 역할이 조금씩 다르다. 이 글에서는 cAdvisor가 무엇인지, Kubernetes 안에서 어디에 있는지, 그리고 Metrics Server와 HPA까지 어떤 흐름으로 연결되는지 정리한다.

---

# 1. cAdvisor란?

`cAdvisor`는 **Container Advisor**의 줄임말이다.

한 문장으로 정리하면 다음과 같다.

```text
cAdvisor는 컨테이너의 CPU, Memory, Network, Disk 사용량을 수집하는 도구다.
```

컨테이너가 실행되면 계속해서 리소스를 사용한다.

```text
CPU 사용량
Memory 사용량
Network 송수신량
Filesystem 사용량
컨테이너 상태
```

cAdvisor는 이런 컨테이너 단위의 리소스 사용량을 수집한다.

```text
Container
   ↓
cAdvisor
   ↓
resource metrics 수집
```

즉 cAdvisor는 “컨테이너가 지금 얼마나 바쁜지”를 관찰하는 역할을 한다.

---

# 2. Kubernetes에서 cAdvisor는 어디에 있을까?

Kubernetes에서는 보통 cAdvisor를 따로 설치해서 쓰기보다, **kubelet 안에 포함된 기능**으로 접하게 된다.

각 Node에는 kubelet이 실행되고 있다.

```text
Node
 ├── kubelet
 │    └── cAdvisor 기능
 ├── Pod
 │    └── Container
 └── Pod
      └── Container
```

kubelet은 해당 Node에서 Pod와 컨테이너가 잘 실행되도록 관리한다. 그리고 그 과정에서 컨테이너의 리소스 사용량도 알고 있어야 한다.

이때 kubelet 내부에서 컨테이너 리소스 사용량을 수집하는 기반이 cAdvisor라고 보면 된다.

```text
각 Node의 kubelet
   ↓
해당 Node의 컨테이너 리소스 사용량 수집
   ↓
CPU / Memory / Network / Disk metrics 제공
```

그래서 Kubernetes에서 Pod 리소스 사용량을 조회하거나, Prometheus가 컨테이너 메트릭을 수집할 때 cAdvisor 계열의 데이터가 중요한 기반이 된다.

---

# 3. cAdvisor가 수집하는 대표 메트릭

cAdvisor는 컨테이너 단위의 다양한 메트릭을 제공한다.

대표적으로 이런 것들이 있다.

```text
container_cpu_usage_seconds_total
container_memory_usage_bytes
container_network_receive_bytes_total
container_network_transmit_bytes_total
container_fs_usage_bytes
```

각각 대략 이런 의미다.

```text
container_cpu_usage_seconds_total
= 컨테이너가 사용한 CPU 시간

container_memory_usage_bytes
= 컨테이너가 사용 중인 메모리 양

container_network_receive_bytes_total
= 컨테이너가 받은 네트워크 바이트 수

container_network_transmit_bytes_total
= 컨테이너가 보낸 네트워크 바이트 수

container_fs_usage_bytes
= 컨테이너 파일시스템 사용량
```

운영 환경에서는 이런 메트릭을 Prometheus가 수집하고, Grafana에서 대시보드로 시각화하는 경우가 많다.

---

# 4. Prometheus와 cAdvisor의 관계

Prometheus는 모니터링 시스템이다. 직접 컨테이너 내부를 들여다보는 것이 아니라, 메트릭을 노출하는 endpoint를 주기적으로 긁어간다. 이것을 scrape이라고 한다.

Kubernetes에서는 보통 다음과 같은 흐름이 된다.

```text
Container
   ↓
cAdvisor / kubelet
   ↓
Prometheus scrape
   ↓
Grafana 시각화
```

즉 Prometheus가 컨테이너 리소스 사용량을 수집하려면, 그 앞단에서 컨테이너 메트릭을 제공하는 대상이 필요하다. 그 역할을 kubelet/cAdvisor가 한다.

정리하면 다음과 같다.

```text
cAdvisor
= 컨테이너 리소스 사용량을 수집하고 노출하는 쪽

Prometheus
= 그 메트릭을 주기적으로 수집하고 저장하는 쪽

Grafana
= 저장된 메트릭을 보기 좋게 시각화하는 쪽
```

---

# 5. Metrics Server와 cAdvisor의 차이

cAdvisor를 공부하다 보면 `Metrics Server`도 같이 나온다.

둘은 비슷해 보이지만 역할이 다르다.

```text
cAdvisor
= 컨테이너 리소스 사용량을 수집하는 기반

Metrics Server
= Kubernetes API에서 리소스 사용량을 조회할 수 있게 제공하는 컴포넌트
```

흐름으로 보면 다음과 같다.

```text
Container
   ↓
cAdvisor / kubelet
   ↓
Metrics Server
   ↓
kubectl top
   ↓
HPA
```

우리가 자주 쓰는 명령어가 있다.

```bash
kubectl top pod
kubectl top node
```

이 명령어는 Metrics Server가 있어야 동작한다.

즉 `kubectl top`이 직접 cAdvisor를 보는 것이 아니라, Metrics Server가 kubelet으로부터 리소스 사용량을 가져오고, 그 데이터를 Kubernetes API를 통해 보여주는 구조다.

---

# 6. kubectl top은 어디서 데이터를 가져올까?

`kubectl top pod`를 실행하면 Pod의 CPU/Memory 사용량을 볼 수 있다.

```bash
kubectl top pod
```

Node 사용량은 다음처럼 본다.

```bash
kubectl top node
```

이때 데이터 흐름은 대략 이렇다.

```text
컨테이너 리소스 사용량 발생
   ↓
kubelet/cAdvisor가 수집
   ↓
Metrics Server가 kubelet에서 수집
   ↓
kubectl top이 Metrics API를 통해 조회
```

그래서 Metrics Server가 없으면 다음과 같은 명령어가 제대로 동작하지 않을 수 있다.

```bash
kubectl top pod
kubectl top node
```

이 경우에는 Metrics Server가 설치되어 있는지 확인해야 한다.

```bash
kubectl get pod -n kube-system
```

---

# 7. HPA와 cAdvisor의 관계

HPA는 Horizontal Pod Autoscaler의 약자다.

Pod 개수를 자동으로 늘리거나 줄이는 리소스다.

예를 들어 CPU 사용률이 높아지면 Deployment의 replica 수를 늘릴 수 있다.

```text
CPU 사용률 증가
   ↓
HPA가 감지
   ↓
Deployment replicas 증가
   ↓
Pod 개수 증가
```

그런데 HPA가 CPU 사용률을 판단하려면 리소스 사용량 데이터가 필요하다.

그 데이터 흐름은 다음과 같다.

```text
Container
   ↓
cAdvisor / kubelet
   ↓
Metrics Server
   ↓
HPA
   ↓
Deployment scale 조정
```

즉 cAdvisor는 HPA가 직접 조작하는 대상은 아니지만, HPA 판단에 필요한 리소스 데이터의 출발점에 가깝다.

---

# 8. 전체 흐름으로 이해하기

cAdvisor, Metrics Server, kubectl top, HPA를 한 번에 연결하면 다음과 같다.

```text
1. 컨테이너가 CPU/Memory를 사용한다.

2. kubelet 안의 cAdvisor 기능이 컨테이너 리소스 사용량을 수집한다.

3. Metrics Server가 각 Node의 kubelet으로부터 리소스 사용량을 가져온다.

4. kubectl top 명령어는 Metrics Server가 제공하는 값을 보여준다.

5. HPA는 Metrics Server의 값을 보고 Deployment replica 수를 조절한다.
```

그림으로 보면 다음과 같다.

```text
Container
   ↓
kubelet / cAdvisor
   ↓
Metrics Server
   ↓
Metrics API
   ↓
kubectl top

또는

Container
   ↓
kubelet / cAdvisor
   ↓
Metrics Server
   ↓
HPA
   ↓
Deployment replicas 조정
```

---

# 9. HPA 예시 흐름

예를 들어 `php-apache` Deployment가 있고, HPA가 CPU 사용률 기준으로 설정되어 있다고 해보자.

```text
php-apache Pod CPU 사용률 증가
   ↓
cAdvisor/kubelet이 리소스 사용량 수집
   ↓
Metrics Server가 해당 값을 가져감
   ↓
HPA가 CPU 사용률 확인
   ↓
replicas 1개에서 8개로 증가
```

이때 HPA를 삭제해도 Deployment가 자동으로 원래 replica 수로 돌아가는 것은 아니다.

HPA는 “스케일 조절기”일 뿐이고, 실제 Pod를 유지하는 것은 Deployment다.

```text
HPA = replica 수를 자동으로 바꾸는 조절기
Deployment = 실제 Pod를 만드는 공장
```

따라서 HPA가 Deployment를 8개로 늘린 뒤 HPA를 삭제하면, Deployment의 replicas 값은 8로 남아 있을 수 있다.

```text
HPA 삭제
   ↓
Deployment replicas: 8 그대로 유지
   ↓
Pod 8개 계속 실행
```

이때 Pod를 줄이고 싶으면 Deployment를 직접 scale해야 한다.

```bash
kubectl scale deployment php-apache --replicas=1
```

완전히 지우고 싶으면 Deployment를 삭제한다.

```bash
kubectl delete deployment php-apache
```

---

# 10. cAdvisor를 직접 띄울 수도 있을까?

Docker 환경에서는 cAdvisor 컨테이너를 직접 실행할 수도 있다.

예시는 다음과 같다.

```bash
docker run \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  gcr.io/cadvisor/cadvisor:latest
```

그러면 브라우저에서 다음 주소로 컨테이너 리소스 사용량을 볼 수 있다.

```text
http://localhost:8080
```

하지만 Kubernetes에서는 보통 cAdvisor를 직접 띄워서 보기보다는, kubelet 내부 기능, Metrics Server, Prometheus, Grafana 흐름으로 접하는 경우가 많다.

---

# 11. CKA 관점에서 알아야 할 정도

CKA에서 cAdvisor 자체를 깊게 설치하거나 설정하는 문제가 핵심으로 나오지는 않는다.

하지만 다음 흐름은 알고 있어야 한다.

```text
kubectl top이 왜 안 되지?
→ Metrics Server가 없거나 정상 동작하지 않을 수 있음

HPA가 왜 unknown이지?
→ Metrics Server에서 CPU/Memory 지표를 못 가져올 수 있음

Pod 리소스 사용량은 어디서 시작되지?
→ kubelet/cAdvisor 계열에서 수집됨
```

CKA에서는 직접적으로 더 중요한 명령어는 다음이다.

```bash
kubectl top pod
kubectl top node
kubectl get hpa
kubectl describe hpa <hpa-name>
kubectl get pod -n kube-system
```

그리고 troubleshooting할 때는 이런 식으로 본다.

```bash
kubectl get hpa
kubectl describe hpa <hpa-name>
kubectl top pod
kubectl top node
kubectl get pod -n kube-system
```

---

# 12. 한 줄 정리

cAdvisor는 컨테이너의 CPU, Memory, Network, Disk 사용량을 수집하는 도구다. Kubernetes에서는 보통 kubelet 안에 포함된 기능으로 동작하고, Metrics Server는 이 데이터를 Kubernetes API에서 사용할 수 있게 제공한다. `kubectl top`과 HPA는 Metrics Server를 통해 리소스 사용량을 확인한다.

마지막으로 전체 관계를 한 번 더 정리하면 다음과 같다.

```text
cAdvisor
= 컨테이너 리소스 사용량 수집

kubelet
= Node에서 Pod와 컨테이너를 관리하고 cAdvisor 기반 메트릭 제공

Metrics Server
= kubelet에서 리소스 사용량을 가져와 Kubernetes Metrics API로 제공

kubectl top
= Metrics Server 데이터를 사람이 조회하는 명령어

HPA
= Metrics Server 데이터를 보고 Deployment replica 수를 자동 조절
```

결국 흐름은 이거다.

```text
Container
   ↓
cAdvisor / kubelet
   ↓
Metrics Server
   ↓
kubectl top / HPA
```

이렇게 보면 cAdvisor는 직접 눈에 잘 보이지는 않지만, Kubernetes 리소스 모니터링의 아래쪽에서 중요한 기반 역할을 하는 컴포넌트라고 이해할 수 있다.
