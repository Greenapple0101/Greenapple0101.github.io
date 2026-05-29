---
title: "[CKA] 쿠버네티스 공식문서, 시험장에서 어떻게 써먹어야 할까?"
source: "https://velog.io/@yorange50/CKA-쿠버네티스-공식문서-시험장에서-어떻게-써먹어야-할까"
published: "2026-05-19T15:43:27.639Z"
tags: ""
backup_date: "2026-05-29T14:52:52.721030"
---

CKA는 암기 시험이라기보다는 **공식문서를 빠르게 찾아서 필요한 YAML과 명령어를 정확히 가져다 쓰는 시험**에 가깝다.
그래서 Kubernetes 개념을 아는 것도 중요하지만, 실제 시험에서는 이런 능력이 더 중요하다.

```text
문제를 읽는다
→ 어떤 리소스인지 판단한다
→ 공식문서에서 비슷한 예제를 찾는다
→ YAML을 복붙한다
→ 문제 조건에 맞게 수정한다
→ kubectl로 검증한다
```

Kubernetes 공식문서는 시험 중 접근 가능한 자료이기 때문에, 평소부터 “공식문서를 읽는 법”보다 **공식문서를 찾고 고쳐 쓰는 법**에 익숙해져야 한다.

---

## 1. 공식문서를 외우려고 하면 안 된다

공식문서는 양이 너무 많다.
Pod, Deployment, Service, Ingress, Gateway API, NetworkPolicy, ConfigMap, Secret, Storage, RBAC, Troubleshooting까지 전부 외우는 건 비효율적이다.

CKA에서 중요한 건 이거다.

```text
정확한 페이지를 빨리 찾는 능력
예제 YAML을 빨리 찾는 능력
불필요한 설명을 버리고 필요한 필드만 가져오는 능력
```

예를 들어 Service 문제가 나오면 Service 개념 전체를 읽는 게 아니라, 공식문서에서 `Service` 예제 YAML을 찾고 `type`, `selector`, `ports`, `targetPort`, `nodePort` 같은 필드만 문제에 맞게 바꾸면 된다. Kubernetes 공식문서에서도 Service는 Pod 여러 개로 실행되는 네트워크 애플리케이션을 노출하는 방법이라고 설명한다. ([Kubernetes][1])

---

## 2. CKA에서 자주 쓰는 공식문서 위치

시험장에서 가장 많이 보게 되는 곳은 크게 네 군데다.

```text
1. kubectl Quick Reference
2. kubectl Reference
3. Concepts
4. Tasks
```

---

## 3. kubectl Quick Reference

가장 먼저 익숙해져야 하는 페이지는 `kubectl Quick Reference`다.
여기에는 자주 쓰는 kubectl 명령어와 플래그가 모여 있다. 공식문서 기준으로 현재 v1.36 기준 명령어가 정리되어 있다. ([Kubernetes][2])

검색 키워드:

```text
kubectl quick reference
```

여기서 자주 찾는 것:

```bash
kubectl get
kubectl describe
kubectl logs
kubectl exec
kubectl apply
kubectl delete
kubectl config
kubectl create
kubectl run
kubectl expose
```

시험장에서 명령어가 헷갈리면 무조건 이 페이지를 먼저 보면 된다.

예를 들어 Pod를 빠르게 만들고 YAML만 뽑고 싶다면:

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml
```

Deployment YAML을 만들고 싶다면:

```bash
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml
```

Service YAML을 만들고 싶다면:

```bash
kubectl expose deployment nginx --port=80 --target-port=80 --dry-run=client -o yaml
```

이런 명령어는 외우면 좋지만, 안 외웠더라도 Quick Reference에서 찾을 수 있어야 한다.

---

## 4. kubectl Reference

`kubectl Reference`는 특정 명령어의 옵션을 자세히 보고 싶을 때 쓴다.
공식문서의 kubectl reference에는 `run`, `expose`, `get`, `describe` 같은 기본 명령어부터 앱을 검사하고 관리하는 명령어들이 정리되어 있다. ([Kubernetes][3])

검색 키워드:

```text
kubectl reference
kubectl create deployment
kubectl expose
kubectl rollout
kubectl set image
```

예를 들어 Deployment 이미지를 바꾸는 문제가 나오면:

```bash
kubectl set image deployment/nginx nginx=nginx:1.25
```

롤아웃 상태를 확인해야 하면:

```bash
kubectl rollout status deployment/nginx
```

이전 버전으로 되돌려야 하면:

```bash
kubectl rollout undo deployment/nginx
```

명령어의 세부 옵션이 기억 안 날 때는 Reference를 찾으면 된다.

---

## 5. Concepts 문서는 개념 확인용

`Concepts`는 리소스가 뭔지 헷갈릴 때 본다.

예를 들어 이런 것들이다.

```text
Pod
Deployment
ReplicaSet
Service
Ingress
Gateway API
NetworkPolicy
PersistentVolume
PersistentVolumeClaim
ConfigMap
Secret
Namespace
Node
```

개념 문서는 시험장에서 처음부터 끝까지 읽는 용도가 아니다.
대신 “이 리소스가 어떤 필드를 갖는지”, “대략 어떤 구조인지” 확인하는 용도다.

예를 들어 Service가 헷갈리면:

```text
Kubernetes Service
```

를 검색한다.

Pod 상태가 `Pending`, `Running`, `Succeeded`, `Failed` 중 어디에 있는지 헷갈리면 `Pod Lifecycle` 문서를 보면 된다. 공식문서는 Pod가 Pending에서 시작해, 컨테이너가 정상 시작되면 Running으로 이동하고, 종료 결과에 따라 Succeeded 또는 Failed가 된다고 설명한다. ([Kubernetes][4])

---

## 6. Tasks 문서는 YAML 예제 찾기용

CKA에서 진짜 중요한 건 `Tasks` 문서다.

Concepts는 설명이 많고, Tasks는 실습 예제가 많다.
시험에서는 예제가 더 중요하다.

검색 키워드 예시:

```text
kubernetes configure pod container
kubernetes configmap pod
kubernetes secret pod
kubernetes resource requests limits
kubernetes liveness readiness probe
kubernetes service account pod
kubernetes network policy
kubernetes persistent volume claim
```

공식문서의 `Configure Pods and Containers` 섹션은 Pod와 컨테이너 설정 작업을 다루며, CPU/Memory 리소스 설정 같은 주제를 포함한다. ([Kubernetes][5])

예를 들어 리소스 제한 문제가 나오면 검색창에 이렇게 친다.

```text
resource requests limits kubernetes
```

찾아야 할 YAML 모양은 보통 이런 식이다.

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

시험장에서는 이 구조를 직접 처음부터 쓰는 것보다, 공식문서 예제를 찾아서 복붙한 뒤 수정하는 게 훨씬 안전하다.

---

## 7. 공식문서 검색창에 뭘 쳐야 하나?

검색어는 길게 치면 오히려 안 좋다.
문제 문장을 그대로 검색하지 말고, 핵심 리소스와 동작만 뽑아서 검색해야 한다.

예시:

| 문제에서 보이는 말          | 검색어                                   |
| ------------------- | ------------------------------------- |
| Pod에 환경변수 추가        | `env pod kubernetes`                  |
| ConfigMap을 Pod에 마운트 | `configmap volume pod kubernetes`     |
| Secret을 환경변수로 사용    | `secret env pod kubernetes`           |
| readinessProbe 설정   | `readiness probe kubernetes`          |
| livenessProbe 설정    | `liveness probe kubernetes`           |
| CPU/Memory 제한       | `resource requests limits kubernetes` |
| ServiceAccount 연결   | `service account pod kubernetes`      |
| NetworkPolicy 작성    | `network policy kubernetes`           |
| PVC 생성              | `persistent volume claim kubernetes`  |
| NodePort Service    | `nodeport service kubernetes`         |
| Gateway API         | `gateway api httproute kubernetes`    |

핵심은 이거다.

```text
리소스명 + 하고 싶은 작업 + kubernetes
```

---

## 8. 공식문서에서 복붙해도 되나?

된다.
오히려 그렇게 해야 한다.

다만 그대로 붙여넣으면 안 되고, 문제 조건에 맞게 바꿔야 한다.

예를 들어 공식문서에서 이런 Service 예제를 가져왔다고 하자.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app.kubernetes.io/name: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```

문제 조건이 이렇다면:

```text
Service 이름: nginx-svc
selector: app=nginx
port: 80
targetPort: 80
type: NodePort
nodePort: 30080
```

이렇게 고쳐야 한다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
```

복붙의 핵심은 **구조를 가져오고, 값은 문제 조건으로 바꾸는 것**이다.

---

## 9. 공식문서 볼 때 버려야 하는 부분

공식문서에는 시험장에서 필요 없는 설명도 많다.
특히 긴 개념 설명, 배경 설명, 주의사항을 다 읽고 있으면 시간이 부족해진다.

시험장에서 봐야 하는 부분은 주로 이거다.

```text
YAML 예제
kubectl 명령어 예제
필드 이름
옵션 이름
주의해야 할 required field
```

예를 들어 NetworkPolicy 문제라면 개념 설명을 오래 읽는 것보다 아래 필드 구조를 빨리 찾아야 한다.

```yaml
podSelector:
policyTypes:
ingress:
egress:
from:
to:
ports:
```

Storage 문제라면 아래 구조를 찾아야 한다.

```yaml
PersistentVolume
PersistentVolumeClaim
storageClassName
accessModes
resources.requests.storage
```

---

## 10. 공식문서 활용 루틴

CKA 공부할 때는 매 문제를 이렇게 풀어보는 게 좋다.

```text
1. 문제에서 리소스 종류 찾기
2. 공식문서에서 관련 예제 검색
3. YAML 복사
4. name, namespace, image, selector, port 수정
5. kubectl apply -f
6. kubectl get / describe로 확인
7. curl, logs, exec 등으로 검증
```

예시:

```bash
kubectl apply -f nginx-service.yaml
kubectl get svc
kubectl describe svc nginx-svc
kubectl get endpoints nginx-svc
curl <접속주소>
```

쿠버네티스는 리소스를 만들었다고 끝이 아니다.
항상 검증까지 해야 한다.

---

## 11. 시험장에서 자주 쓰는 검증 명령어

```bash
kubectl get pods
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- sh
kubectl get svc
kubectl get endpoints
kubectl get deploy
kubectl rollout status deploy/<name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

Namespace가 있으면 항상 `-n`을 붙인다.

```bash
kubectl get pods -n nginx-static
kubectl describe cm nginx-config -n nginx-static
kubectl rollout restart deployment nginx-static -n nginx-static
```

CKA 문제는 namespace가 숨어 있는 경우가 많다.
문제에 `in the nginx-static namespace` 같은 말이 있으면 모든 명령어에 `-n nginx-static`을 붙여야 한다.

---

## 12. 공식문서보다 빠른 방법: kubectl로 YAML 생성하기

공식문서 검색보다 더 빠른 경우도 있다.

Pod 생성:

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

Deployment 생성:

```bash
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml
```

Service 생성:

```bash
kubectl expose deployment nginx --port=80 --target-port=80 --dry-run=client -o yaml > svc.yaml
```

ConfigMap 생성:

```bash
kubectl create configmap nginx-config \
  --from-literal=key=value \
  --dry-run=client -o yaml > cm.yaml
```

Secret 생성:

```bash
kubectl create secret generic my-secret \
  --from-literal=password=1234 \
  --dry-run=client -o yaml > secret.yaml
```

이 방식은 시험장에서 매우 강력하다.

```text
공식문서에서 YAML 구조 찾기
vs
kubectl로 기본 YAML 생성 후 수정하기
```

둘 다 할 줄 알아야 한다.

---

## 13. edit을 써도 되는 경우

작은 수정은 `kubectl edit`이 빠르다.

예를 들어 ConfigMap 하나 수정:

```bash
kubectl edit configmap nginx-config -n nginx-static
```

Deployment 이미지 수정:

```bash
kubectl edit deployment nginx -n default
```

하지만 복잡한 YAML을 많이 바꿔야 하면 파일로 빼는 게 낫다.

```bash
kubectl get deploy nginx -o yaml > deploy.yaml
vi deploy.yaml
kubectl apply -f deploy.yaml
```

단, 기존 리소스를 `get -o yaml`로 뽑으면 `status`, `resourceVersion`, `uid`, `managedFields` 같은 불필요한 필드가 많이 들어간다.
시험장에서는 가능하면 직접 만든 깔끔한 YAML이나 `--dry-run=client -o yaml`로 만든 YAML을 수정하는 쪽이 안전하다.

---

## 14. CKA 대비 공식문서 공부법

그냥 공식문서를 읽으면 안 된다.
문제 상황을 하나 정하고, 그걸 공식문서에서 찾아서 해결하는 식으로 공부해야 한다.

예를 들어 오늘 공부 주제가 Service라면:

```text
ClusterIP Service 만들기
NodePort Service 만들기
selector 안 맞아서 endpoints 비는 상황 확인하기
targetPort 틀려서 curl 안 되는 상황 확인하기
```

이렇게 직접 해봐야 한다.

공식문서 공부는 “읽기”가 아니라 “찾기 훈련”이다.

---

## 15. 내가 추천하는 CKA 공식문서 활용 순서

```text
1단계: kubectl Quick Reference 익숙해지기
2단계: Pod / Deployment / Service 예제 찾기
3단계: ConfigMap / Secret / Probe / Resource 예제 찾기
4단계: Storage / NetworkPolicy / RBAC 예제 찾기
5단계: 문제 풀 때마다 검색어를 기록하기
6단계: 자주 쓰는 YAML 구조는 손에 익히기
```

특히 CKA 직전에는 개념을 새로 공부하기보다, 공식문서에서 아래 항목들을 빠르게 찾는 연습을 하는 게 좋다.

```text
Pod command/args
env
volumeMounts
ConfigMap
Secret
readinessProbe
livenessProbe
resources
Service
Ingress
Gateway API
NetworkPolicy
PV/PVC
ServiceAccount
Role/RoleBinding
Node selector
Taint/Toleration
```

---

## 16. 결론

CKA에서 공식문서는 단순 참고자료가 아니다.
사실상 시험장에서 같이 쓰는 도구다.

중요한 건 “공식문서를 많이 읽었다”가 아니라:

```text
내가 원하는 예제를 30초 안에 찾을 수 있는가
찾은 YAML을 문제 조건에 맞게 고칠 수 있는가
적용 후 kubectl로 검증할 수 있는가
```

이다.

CKA 준비는 결국 이 흐름에 익숙해지는 과정이다.

```text
검색한다
복붙한다
수정한다
적용한다
검증한다
```

이 루틴이 손에 익으면, 모르는 문제가 나와도 당황하지 않고 공식문서에서 답을 끌어올 수 있다.

[1]: https://kubernetes.io/docs/concepts/services-networking/service/?utm_source=chatgpt.com "Service"
[2]: https://kubernetes.io/docs/reference/kubectl/quick-reference/?utm_source=chatgpt.com "kubectl Quick Reference"
[3]: https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands?utm_source=chatgpt.com "Kubectl Reference Docs"
[4]: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/?utm_source=chatgpt.com "Pod Lifecycle"
[5]: https://kubernetes.io/docs/tasks/configure-pod-container/?utm_source=chatgpt.com "Configure Pods and Containers"
