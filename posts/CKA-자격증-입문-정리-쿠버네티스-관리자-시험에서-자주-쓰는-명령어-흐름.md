---
title: "[CKA] 쿠버네티스 관리자 시험에서 자주 쓰는 명령어 흐름"
source: "https://velog.io/@yorange50/CKA-자격증-입문-정리-쿠버네티스-관리자-시험에서-자주-쓰는-명령어-흐름"
published: "2026-05-04T03:52:27.233Z"
tags: ""
backup_date: "2026-05-29T14:52:52.779015"
---

CKA는 Certified Kubernetes Administrator의 약자로, 쿠버네티스 클러스터를 운영하고 관리할 수 있는지를 검증하는 실기형 자격증이다. 단순히 개념을 외우는 시험이라기보다는, 실제 터미널 환경에서 `kubectl` 명령어를 사용해 리소스를 만들고, 수정하고, 장애를 해결하는 능력을 본다. 그래서 CKA 공부를 시작할 때는 쿠버네티스 이론과 함께 “명령어를 어떻게 사용하는지”를 익히는 것이 중요하다.

---

## 1. CKA에서 중요한 기본 관점

CKA는 개발자가 애플리케이션 코드를 작성하는 시험이 아니다. 쿠버네티스 클러스터 안에서 애플리케이션이 잘 배포되고, 정상적으로 통신하고, 장애가 났을 때 원인을 찾아 복구할 수 있는지를 보는 시험이다.

즉, 핵심은 다음 흐름이다.

```bash
상태 확인 → 원인 파악 → YAML 수정 → 적용 → 검증
```

예를 들어 Pod가 실행되지 않는다면 먼저 `kubectl get pods`로 상태를 보고, `kubectl describe pod`로 이벤트를 확인하고, 필요하다면 YAML을 수정한 뒤 다시 적용한다. 이 흐름이 CKA의 기본 문제 풀이 방식이다.

---

## 2. 시험장에서 가장 먼저 세팅하는 명령어

CKA에서는 `kubectl`을 매우 자주 입력하게 된다. 그래서 보통 `kubectl`을 `k`로 줄여서 사용한다.

```bash
alias k=kubectl
```

YAML 파일을 빠르게 생성하기 위한 옵션도 자주 사용한다.

```bash
export do="--dry-run=client -o yaml"
```

이렇게 설정해두면 리소스를 바로 생성하지 않고 YAML 파일 형태로 출력할 수 있다.

예를 들어 nginx Pod의 YAML을 만들고 싶다면 다음처럼 입력한다.

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

alias와 환경변수를 설정했다면 더 짧게 쓸 수 있다.

```bash
k run nginx --image=nginx $do > pod.yaml
```

CKA에서는 이런 식으로 명령어를 짧게 쓰는 습관이 꽤 중요하다. 시험 시간이 제한되어 있기 때문이다.

---

## 3. 쿠버네티스 상태 확인 명령어

가장 기본은 `get`이다. 현재 클러스터에 어떤 리소스가 있는지 확인할 때 사용한다.

```bash
kubectl get pods
kubectl get nodes
kubectl get deployments
kubectl get services
kubectl get namespaces
```

전체 네임스페이스의 Pod를 보고 싶다면 `-A` 옵션을 붙인다.

```bash
kubectl get pods -A
```

더 자세한 정보를 보고 싶을 때는 `-o wide`를 사용한다.

```bash
kubectl get pods -o wide
kubectl get nodes -o wide
```

`-o wide`를 붙이면 Pod가 어느 노드에 떠 있는지, IP는 무엇인지 등을 함께 볼 수 있다.

---

## 4. 리소스 상세 확인: describe

`get`이 목록 확인이라면, `describe`는 상세 분석이다.

```bash
kubectl describe pod <pod-name>
kubectl describe node <node-name>
kubectl describe service <service-name>
kubectl describe deployment <deployment-name>
```

특히 Pod가 `Pending`, `CrashLoopBackOff`, `ImagePullBackOff` 상태일 때는 `describe`가 매우 중요하다.

```bash
kubectl describe pod nginx
```

여기서 아래쪽의 `Events` 부분을 보면 왜 실행이 안 되는지 힌트가 나온다.

예를 들어 이미지 이름이 잘못되었거나, 리소스가 부족하거나, PVC가 바인딩되지 않았거나, 스케줄링 가능한 노드가 없다는 메시지를 볼 수 있다.

CKA에서 장애 문제를 풀 때는 거의 항상 다음 순서로 본다.

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

## 5. Pod 생성 명령어

Pod는 쿠버네티스에서 컨테이너를 실행하는 가장 작은 단위다.

nginx Pod를 바로 생성하려면 다음 명령어를 사용한다.

```bash
kubectl run nginx --image=nginx
```

하지만 시험에서는 바로 생성하기보다 YAML 파일로 뽑아서 수정하는 경우가 많다.

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

그다음 파일을 수정한다.

```bash
vi pod.yaml
```

수정한 YAML을 적용한다.

```bash
kubectl apply -f pod.yaml
```

Pod 삭제는 다음과 같다.

```bash
kubectl delete pod nginx
```

강제로 바로 삭제하고 싶을 때는 다음 명령어를 쓴다.

```bash
kubectl delete pod nginx --force --grace-period=0
```

---

## 6. Deployment 생성과 관리

실무에서는 Pod를 직접 하나씩 띄우기보다 Deployment를 사용한다. Deployment는 Pod를 여러 개 유지하고, 업데이트와 롤백을 관리하는 리소스다.

Deployment 생성:

```bash
kubectl create deployment nginx --image=nginx
```

replica 수를 지정해서 생성:

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

YAML로 생성:

```bash
kubectl create deployment nginx --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml
```

replica 수 변경:

```bash
kubectl scale deployment nginx --replicas=5
```

이미지 변경:

```bash
kubectl set image deployment/nginx nginx=nginx:1.25
```

롤아웃 상태 확인:

```bash
kubectl rollout status deployment/nginx
```

롤아웃 히스토리 확인:

```bash
kubectl rollout history deployment/nginx
```

롤백:

```bash
kubectl rollout undo deployment/nginx
```

Deployment는 CKA에서 매우 자주 나온다. 특히 replica 변경, 이미지 변경, 롤백은 손에 익혀두는 것이 좋다.

---

## 7. Service 생성과 확인

Service는 Pod에 접근할 수 있게 해주는 네트워크 리소스다. Pod는 삭제되고 다시 생성될 수 있기 때문에 IP가 바뀔 수 있다. 그래서 고정된 접근 지점으로 Service를 사용한다.

Deployment를 Service로 노출:

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

NodePort 타입으로 노출:

```bash
kubectl expose deployment nginx --type=NodePort --port=80 --target-port=80
```

Service 확인:

```bash
kubectl get svc
kubectl describe svc nginx
```

Service가 잘 연결되지 않을 때는 label과 selector를 확인해야 한다.

```bash
kubectl get pods --show-labels
kubectl describe svc <service-name>
```

Service의 selector와 Pod의 label이 일치하지 않으면 트래픽이 Pod로 가지 않는다. CKA에서 자주 나오는 장애 유형이다.

---

## 8. 로그와 디버깅 명령어

Pod 로그 확인:

```bash
kubectl logs <pod-name>
```

실시간 로그 확인:

```bash
kubectl logs -f <pod-name>
```

이전 컨테이너 로그 확인:

```bash
kubectl logs <pod-name> --previous
```

Pod 안으로 들어가기:

```bash
kubectl exec -it <pod-name> -- sh
```

bash가 있는 이미지라면 다음도 가능하다.

```bash
kubectl exec -it <pod-name> -- bash
```

Pod 내부에서 명령어만 실행할 수도 있다.

```bash
kubectl exec <pod-name> -- cat /etc/resolv.conf
```

디버깅용 임시 Pod를 띄울 때는 busybox나 curl 이미지를 자주 사용한다.

```bash
kubectl run busybox --image=busybox --restart=Never -it --rm -- sh
```

```bash
kubectl run curl --image=curlimages/curl -it --rm -- sh
```

Service 통신 테스트는 다음처럼 할 수 있다.

```bash
wget -qO- http://<service-name>
curl http://<service-name>
```

---

## 9. Namespace 관련 명령어

Namespace는 쿠버네티스 리소스를 논리적으로 나누는 공간이다.

Namespace 생성:

```bash
kubectl create namespace dev
```

Namespace 목록 확인:

```bash
kubectl get ns
```

특정 Namespace에 Pod 생성:

```bash
kubectl run nginx --image=nginx -n dev
```

특정 Namespace의 Pod 확인:

```bash
kubectl get pods -n dev
```

현재 context의 기본 Namespace 변경:

```bash
kubectl config set-context --current --namespace=dev
```

이렇게 설정하면 매번 `-n dev`를 붙이지 않아도 된다.

---

## 10. ConfigMap과 Secret

ConfigMap은 설정값을 저장하는 리소스다.

```bash
kubectl create configmap app-config --from-literal=APP_ENV=prod
```

파일에서 ConfigMap 생성:

```bash
kubectl create configmap app-config --from-file=app.properties
```

Secret은 비밀번호나 토큰 같은 민감한 값을 저장할 때 사용한다.

```bash
kubectl create secret generic db-secret --from-literal=username=admin --from-literal=password=1234
```

Secret 확인:

```bash
kubectl get secret
kubectl describe secret db-secret
kubectl get secret db-secret -o yaml
```

Secret 값은 base64로 인코딩되어 있다. 디코딩은 다음처럼 한다.

```bash
echo '<base64-value>' | base64 -d
```

---

## 11. Label과 Selector

Label은 리소스에 붙이는 태그다. Service, Deployment, NetworkPolicy 등에서 특정 Pod를 선택할 때 사용한다.

라벨 추가:

```bash
kubectl label pod nginx app=web
```

라벨 확인:

```bash
kubectl get pods --show-labels
```

라벨 기준 조회:

```bash
kubectl get pods -l app=web
```

라벨 삭제:

```bash
kubectl label pod nginx app-
```

Service가 Pod를 찾지 못할 때는 대부분 selector와 label이 맞지 않는 경우가 많다.

---

## 12. Node 관리 명령어

Node 목록 확인:

```bash
kubectl get nodes
```

Node 상세 확인:

```bash
kubectl describe node <node-name>
```

특정 노드에 더 이상 Pod가 스케줄링되지 않게 막기:

```bash
kubectl cordon <node-name>
```

다시 스케줄링 허용:

```bash
kubectl uncordon <node-name>
```

노드 점검을 위해 Pod를 비우기:

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

CKA에서 `cordon`, `uncordon`, `drain`은 운영자 관점에서 매우 중요하다. 실제로 노드를 점검하거나 업그레이드할 때 사용하는 명령어이기 때문이다.

---

## 13. Taint와 Toleration

Taint는 특정 노드에 아무 Pod나 올라오지 못하게 막는 기능이다.

Taint 추가:

```bash
kubectl taint nodes <node-name> key=value:NoSchedule
```

Taint 제거:

```bash
kubectl taint nodes <node-name> key=value:NoSchedule-
```

Taint가 걸린 노드에 Pod를 배치하려면 Pod에 toleration을 추가해야 한다.

```yaml
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

---

## 14. RBAC 명령어

RBAC는 권한 관리다. 누가 어떤 리소스에 어떤 동작을 할 수 있는지 제어한다.

ServiceAccount 생성:

```bash
kubectl create serviceaccount dev-sa
```

Role 생성:

```bash
kubectl create role pod-reader --verb=get,list,watch --resource=pods
```

RoleBinding 생성:

```bash
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:dev-sa
```

권한 확인:

```bash
kubectl auth can-i get pods
kubectl auth can-i delete pods
kubectl auth can-i get pods --as=system:serviceaccount:default:dev-sa
```

CKA에서는 “이 ServiceAccount가 Pod를 조회할 수 있게 하라” 같은 문제가 나올 수 있다. 이때 Role, RoleBinding, ServiceAccount의 관계를 이해해야 한다.

---

## 15. Storage: PV와 PVC

쿠버네티스에서 저장소를 사용할 때는 PV와 PVC를 사용한다.

PV 확인:

```bash
kubectl get pv
```

PVC 확인:

```bash
kubectl get pvc
```

StorageClass 확인:

```bash
kubectl get storageclass
```

PVC 예시:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

PVC가 정상적으로 바인딩되었는지 확인한다.

```bash
kubectl describe pvc my-pvc
```

Pod가 Pending 상태라면 PVC가 바인딩되지 않았는지도 확인해야 한다.

---

## 16. NetworkPolicy

NetworkPolicy는 Pod 간 네트워크 접근을 제어하는 리소스다.

NetworkPolicy 확인:

```bash
kubectl get networkpolicy
kubectl describe networkpolicy <name>
```

전체 Ingress 차단 예시:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

특정 label을 가진 Pod에서만 접근 허용:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-client
spec:
  podSelector:
    matchLabels:
      app: server
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: client
    ports:
    - protocol: TCP
      port: 80
```

CKA에서 NetworkPolicy는 어렵게 느껴질 수 있지만, 기본 구조는 단순하다.

```bash
어떤 Pod를 보호할 것인가?
어떤 방향의 트래픽을 제어할 것인가?
누구의 접근을 허용할 것인가?
어떤 포트를 열 것인가?
```

이 네 가지만 보면 된다.

---

## 17. etcd 백업과 복구

etcd는 쿠버네티스 클러스터의 상태 정보를 저장하는 핵심 저장소다. CKA에서 etcd 백업과 복구는 매우 중요한 주제다.

먼저 etcdctl API 버전을 설정한다.

```bash
export ETCDCTL_API=3
```

etcd snapshot 저장:

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

snapshot 상태 확인:

```bash
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db
```

복구:

```bash
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore
```

복구 후에는 보통 etcd static pod 설정 파일을 수정한다.

```bash
vi /etc/kubernetes/manifests/etcd.yaml
```

여기서 `--data-dir` 경로를 복구한 디렉터리로 바꾼다.

---

## 18. Control Plane 장애 확인

Control Plane 컴포넌트들은 보통 static pod로 관리된다.

static pod manifest 위치:

```bash
ls /etc/kubernetes/manifests
```

주요 파일:

```bash
/etc/kubernetes/manifests/kube-apiserver.yaml
/etc/kubernetes/manifests/kube-scheduler.yaml
/etc/kubernetes/manifests/kube-controller-manager.yaml
/etc/kubernetes/manifests/etcd.yaml
```

kubelet 상태 확인:

```bash
systemctl status kubelet
```

kubelet 로그 확인:

```bash
journalctl -u kubelet
journalctl -u kubelet -f
```

kubelet 재시작:

```bash
systemctl restart kubelet
```

Control Plane 장애 문제에서는 YAML 파일의 오타, 인증서 경로 오류, 포트 설정 오류 등이 자주 원인이 된다.

---

## 19. JSONPath

JSONPath는 원하는 값만 뽑아낼 때 사용한다.

Pod 이름만 출력:

```bash
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
```

특정 Pod의 IP 출력:

```bash
kubectl get pod <pod-name> -o jsonpath='{.status.podIP}'
```

Node 이름만 출력:

```bash
kubectl get nodes -o jsonpath='{.items[*].metadata.name}'
```

처음에는 어렵지만, 시험에서 특정 값만 출력하라는 문제가 나올 수 있으므로 기본 형태는 익혀두는 것이 좋다.

---

## 20. CKA 공부할 때 명령어를 외우는 방식

CKA 명령어는 무작정 외우기보다 상황별로 외우는 것이 좋다.

Pod가 안 뜬다:

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

Service가 연결되지 않는다:

```bash
kubectl get svc
kubectl describe svc <service-name>
kubectl get pods --show-labels
kubectl get endpoints
```

Deployment를 수정해야 한다:

```bash
kubectl edit deployment <deployment-name>
kubectl rollout status deployment/<deployment-name>
```

Node를 점검해야 한다:

```bash
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node-name>
```

권한을 확인해야 한다:

```bash
kubectl auth can-i get pods
kubectl auth can-i get pods --as=system:serviceaccount:default:dev-sa
```

---

## 21. CKA 입문자가 먼저 익혀야 할 우선순위

CKA를 처음 공부한다면 모든 명령어를 한 번에 외우려고 하면 안 된다. 우선순위를 잡는 것이 좋다.

첫 번째는 `kubectl get`, `describe`, `logs`, `exec`이다.
이 네 가지는 거의 모든 문제의 시작점이다.

두 번째는 Pod, Deployment, Service 생성이다.
쿠버네티스의 기본 리소스를 만들고 연결하는 능력이 필요하다.

세 번째는 YAML 수정이다.
CKA는 명령어만으로 끝나는 문제가 많지 않다. 결국 YAML을 수정해야 한다.

네 번째는 Node 관리다.
`cordon`, `drain`, `uncordon`, `taint`, `toleration`은 운영자 시험답게 자주 중요하게 다뤄진다.

다섯 번째는 RBAC, NetworkPolicy, Storage, etcd 백업/복구다.
이 부분은 처음에는 어렵지만 CKA 합격을 위해 반드시 잡아야 한다.

---

## 22. 시험장에서 자주 쓰는 치트키 모음

```bash
alias k=kubectl
export do="--dry-run=client -o yaml"
```

```bash
k get po -A
k get no
k get svc
k get deploy
k describe po <pod-name>
k logs <pod-name>
k exec -it <pod-name> -- sh
```

```bash
k run nginx --image=nginx $do > pod.yaml
k create deploy nginx --image=nginx --replicas=3 $do > deploy.yaml
k expose deploy nginx --port=80 --target-port=80 $do > svc.yaml
```

```bash
k apply -f file.yaml
k delete -f file.yaml
k edit deploy <deployment-name>
```

```bash
k rollout status deploy/<deployment-name>
k rollout undo deploy/<deployment-name>
k scale deploy <deployment-name> --replicas=3
```

```bash
k get events --sort-by=.metadata.creationTimestamp
```

---

## 마무리

CKA는 쿠버네티스를 “알고 있다”를 넘어서 “직접 운영할 수 있다”를 증명하는 시험이다. 그래서 개념 정리도 중요하지만, 결국 손에 익은 명령어와 장애 해결 흐름이 더 중요하다.

입문 단계에서는 모든 리소스를 완벽하게 이해하려고 하기보다, 다음 흐름을 반복해서 연습하는 것이 좋다.

```bash
리소스 생성
상태 확인
문제 발생
describe/logs/events 확인
YAML 수정
다시 적용
정상 동작 검증
```

이 흐름이 익숙해지면 CKA 공부가 단순 암기가 아니라 실제 DevOps 운영 역량으로 연결된다. 특히 DevOps 직무를 준비한다면 CKA 공부는 단순 자격증 준비가 아니라, 쿠버네티스 기반 배포·운영·장애 대응 역량을 쌓는 과정으로 볼 수 있다.
