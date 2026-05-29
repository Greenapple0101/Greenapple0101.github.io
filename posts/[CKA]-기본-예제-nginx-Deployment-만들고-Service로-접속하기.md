---
title: "CKA 기본 예제: nginx Deployment 만들고 Service로 접속하기"
source: "https://velog.io/@yorange50/CKA-기본-예제-nginx-Deployment-만들고-Service로-접속하기"
published: "2026-05-04T04:32:57.716Z"
tags: ""
backup_date: "2026-05-29T14:52:52.778334"
---

## 목표

쿠버네티스 클러스터 안에 nginx 웹서버를 띄우고, Service를 통해 접근 가능한지 확인한다.

최종 구조는 다음과 같다.

```text
Service
  ↓
nginx Pod 3개
  ↑
Deployment가 관리
```

---

## 1. Deployment 생성

먼저 nginx 이미지를 사용하는 Deployment를 만든다.

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

이 명령어의 의미는 다음과 같다.

```text
nginx라는 이름의 Deployment를 만들고
nginx 이미지를 사용하며
Pod를 3개 유지하라
```

---

## 2. 생성 확인

```bash
kubectl get deployment
```

또는 줄여서:

```bash
kubectl get deploy
```

예상 출력:

```text
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
nginx   3/3     3            3           20s
```

Pod도 확인한다.

```bash
kubectl get pods
```

예상 출력:

```text
NAME                     READY   STATUS    RESTARTS   AGE
nginx-xxxxxxx-abcde      1/1     Running   0          30s
nginx-xxxxxxx-fghij      1/1     Running   0          30s
nginx-xxxxxxx-klmno      1/1     Running   0          30s
```

여기서 중요한 점은 우리가 Pod를 직접 3개 만든 게 아니라는 것이다.

```text
Deployment가 ReplicaSet을 만들고
ReplicaSet이 Pod 3개를 유지한다
```

---

## 3. Service 생성

Pod는 IP가 바뀔 수 있으므로 Service를 붙인다.

```bash
kubectl expose deployment nginx --port=80 --target-port=80
```

의미는 다음과 같다.

```text
nginx Deployment에 연결되는 Service를 만들고
Service의 80번 포트를
Pod의 80번 포트로 연결하라
```

---

## 4. Service 확인

```bash
kubectl get service
```

또는 줄여서:

```bash
kubectl get svc
```

예상 출력:

```text
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP   ...
nginx        ClusterIP   10.100.12.34    <none>        80/TCP    10s
```

여기서 nginx Service의 타입은 기본적으로 `ClusterIP`다.

```text
ClusterIP = 클러스터 내부에서만 접근 가능한 Service
```

즉, 외부 브라우저에서 바로 접속하는 용도는 아니고, 클러스터 내부 Pod들이 접근하는 주소다.

---

## 5. Service가 Pod와 연결됐는지 확인

```bash
kubectl describe service nginx
```

여기서 확인할 부분은 `Selector`와 `Endpoints`다.

예시:

```text
Selector: app=nginx
Endpoints: 10.244.1.3:80,10.244.2.4:80,10.244.3.5:80
```

이렇게 Endpoints가 보이면 Service가 Pod들을 잘 찾고 있다는 뜻이다.

만약 Endpoints가 비어 있으면 보통 이 문제다.

```text
Service selector와 Pod label이 안 맞음
```

이건 CKA에서 진짜 자주 나오는 포인트다.

---

## 6. 클러스터 내부에서 접속 테스트

ClusterIP Service는 외부에서 바로 접근하지 못하므로, 테스트용 Pod를 하나 띄워서 내부에서 접근해본다.

```bash
kubectl run test --image=busybox --restart=Never -it --rm -- wget -qO- http://nginx
```

정상이라면 nginx HTML이 출력된다.

```html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
</html>
```

이게 나오면 성공이다.

---

## 7. 현재 구조 확인

```bash
kubectl get all
```

출력에는 대략 이런 것들이 보인다.

```text
pod/nginx-...
service/nginx
deployment.apps/nginx
replicaset.apps/nginx-...
```

구조로 보면 이렇다.

```text
Deployment
   ↓
ReplicaSet
   ↓
Pod 3개

Service
   ↓
Pod 3개로 트래픽 전달
```

조금 더 실무식으로 보면:

```text
내부 클라이언트 Pod
   ↓
nginx Service
   ↓
nginx Pod 1
nginx Pod 2
nginx Pod 3
```

---

## 8. 장애 상황 실습: Pod 하나 삭제하기

Pod 하나를 일부러 삭제해본다.

먼저 Pod 이름 확인:

```bash
kubectl get pods
```

하나 삭제:

```bash
kubectl delete pod <pod-name>
```

다시 확인:

```bash
kubectl get pods
```

그러면 삭제한 Pod 대신 새로운 Pod가 다시 생긴다.

이유는 Deployment가 replica 3개를 유지하고 있기 때문이다.

```text
원하는 상태: Pod 3개
현재 상태: Pod 2개
쿠버네티스: 하나 다시 생성
```

이게 쿠버네티스의 핵심이다.

```text
현재 상태를 원하는 상태로 맞춘다
```

---

## 9. Replica 개수 변경하기

이번에는 Pod 개수를 3개에서 5개로 늘린다.

```bash
kubectl scale deployment nginx --replicas=5
```

확인:

```bash
kubectl get pods
```

Pod가 5개로 늘어난다.

다시 2개로 줄이기:

```bash
kubectl scale deployment nginx --replicas=2
```

확인:

```bash
kubectl get pods
```

---

## 10. 이미지 업데이트하기

nginx 이미지를 특정 버전으로 바꿔본다.

```bash
kubectl set image deployment/nginx nginx=nginx:1.25
```

롤아웃 상태 확인:

```bash
kubectl rollout status deployment/nginx
```

히스토리 확인:

```bash
kubectl rollout history deployment/nginx
```

문제가 생겼다고 가정하고 롤백:

```bash
kubectl rollout undo deployment/nginx
```

이 흐름도 CKA에서 중요하다.

```text
이미지 변경
롤아웃 확인
문제 발생 시 롤백
```

---

## 11. YAML로 뽑아보기

CKA에서는 명령어로 바로 만드는 것보다 YAML을 수정해야 하는 경우가 많다.

Deployment YAML 출력:

```bash
kubectl get deployment nginx -o yaml > nginx-deploy.yaml
```

Service YAML 출력:

```bash
kubectl get service nginx -o yaml > nginx-svc.yaml
```

파일 수정:

```bash
vi nginx-deploy.yaml
```

수정 후 적용:

```bash
kubectl apply -f nginx-deploy.yaml
```

---

## 12. 삭제하기

실습이 끝났으면 리소스를 삭제한다.

```bash
kubectl delete service nginx
kubectl delete deployment nginx
```

확인:

```bash
kubectl get all
```

---

# 전체 명령어 요약

```bash
kubectl create deployment nginx --image=nginx --replicas=3
kubectl get deploy
kubectl get pods
kubectl expose deployment nginx --port=80 --target-port=80
kubectl get svc
kubectl describe svc nginx
kubectl run test --image=busybox --restart=Never -it --rm -- wget -qO- http://nginx
kubectl delete pod <pod-name>
kubectl get pods
kubectl scale deployment nginx --replicas=5
kubectl set image deployment/nginx nginx=nginx:1.25
kubectl rollout status deployment/nginx
kubectl rollout undo deployment/nginx
kubectl delete svc nginx
kubectl delete deploy nginx
```

---

# 이 예제로 익히는 핵심 개념

```text
Deployment는 Pod를 직접 관리하지 않고 ReplicaSet을 통해 Pod 개수를 유지한다.

replicas: 3이면 Pod 3개를 계속 유지하려고 한다.

Pod 하나가 죽어도 Deployment가 다시 만든다.

Service는 Pod IP가 바뀌어도 접근할 수 있는 고정 주소 역할을 한다.

Service는 selector와 label을 기준으로 Pod를 찾는다.

ClusterIP Service는 클러스터 내부에서만 접근된다.

kubectl describe service를 보면 Endpoints로 연결된 Pod IP를 확인할 수 있다.

kubectl rollout 명령어로 배포 상태 확인과 롤백이 가능하다.
```

---

# 한 줄로 정리

```text
Deployment로 nginx Pod 3개를 띄우고, Service로 묶은 뒤, 내부 테스트 Pod에서 http://nginx 로 접속해보는 예제
```

이 예제 하나만 제대로 이해해도 CKA의 기본 흐름인 **배포 → 노출 → 확인 → 장애 테스트 → 복구 확인**을 잡을 수 있다.
