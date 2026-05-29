---
title: "[Argo CD] Healthy, Synced가 떴다는 건 무슨 뜻일까?"
source: "https://velog.io/@yorange50/Argo-CD-Healthy-Synced%EA%B0%80-%EB%96%B4%EB%8B%A4%EB%8A%94-%EA%B1%B4-%EB%AC%B4%EC%8A%A8-%EB%9C%BB%EC%9D%BC%EA%B9%8C"
published: "Thu, 28 May 2026 23:41:20 GMT"
backup_date: "2026-05-29T14:51:00.482441"
---

지금 화면은 **Argo CD로 Kubernetes 애플리케이션 배포가 성공한 상태** 라고 보면 된다.

한 줄로 요약하면 이거다.

> GitHub에 있는 Kubernetes manifest를 Argo CD가 읽어서, Kubernetes 클러스터 안에 Service, Deployment, Ingress를 정상적으로 만들었고, 현재 상태도 문제없음

* * *

# 1\. 지금 만든 애플리케이션 이름

![](https://velog.velcdn.com/images/yorange50/post/e6badf7f-5daf-4095-8497-e5074b18bf97/image.png)

화면에 보이는 Application 이름은 `osc`다.
    
    
    Application: osc
    Project: default
    Repository: https://github.com/Greenapple0101/demo_gitops.git
    Target Revision: main
    Path: vas
    Destination: in-cluster
    Namespace: vas

이 말은 Argo CD가 이런 식으로 동작한다는 뜻이다.
    
    
    GitHub repo: demo_gitops
    브랜치: main
    경로: vas
    안에 있는 YAML 파일들 읽기
    ↓
    현재 Kubernetes 클러스터에 적용
    ↓
    namespace: vas에 리소스 생성

즉, `demo_gitops` 저장소의 `vas` 폴더 안에 있는 YAML들이 실제 쿠버네티스 클러스터에 배포된 상태다.

* * *

# 2\. Healthy는 무슨 뜻일까?

화면에 계속 이렇게 뜬다.
    
    
    APP HEALTH
    Healthy

이건 **쿠버네티스 리소스들이 정상 상태** 라는 뜻이다.

예를 들어 Deployment라면 원하는 개수만큼 Pod가 잘 떠 있어야 하고, Service라면 정상적으로 연결 대상이 있어야 하고, Ingress도 리소스 자체가 문제없이 생성되어 있어야 한다.

지금 Argo CD가 보기에는 앱 상태가 정상이다.
    
    
    Healthy = Kubernetes 쪽에서 리소스가 잘 살아 있음

* * *

# 3\. Synced는 무슨 뜻일까?

화면에 이렇게 보인다.
    
    
    SYNC STATUS
    Synced to main (e6e7936)

이건 **GitHub에 있는 manifest 상태와 실제 Kubernetes 클러스터 상태가 일치한다는 뜻** 이다.

GitOps에서 제일 중요한 개념이 이거다.
    
    
    GitHub에 정의된 상태 = 원하는 상태
    Kubernetes에 실제 적용된 상태 = 현재 상태

Argo CD는 이 둘을 비교한다.

둘이 같으면:
    
    
    Synced

둘이 다르면:
    
    
    OutOfSync

지금은 `Synced`니까 GitHub의 `main` 브랜치에 있는 `e6e7936` 커밋 내용이 클러스터에 그대로 반영된 상태다.

* * *

# 4\. Sync OK는 무슨 뜻일까?

화면 오른쪽에 이렇게 보인다.
    
    
    LAST SYNC
    Sync OK to e6e7936

이건 마지막 동기화 작업이 성공했다는 뜻이다.

그리고 아래에 보면 커밋 메시지도 나온다.
    
    
    Author: Greenapple0101
    Comment: Add vas gitops manifests

즉, 이 커밋에서 추가한 `vas` 관련 Kubernetes manifest들이 Argo CD를 통해 정상 배포된 것이다.

* * *

# 5\. Auto sync is not enabled는 문제일까?

화면에 이렇게 나온다.
    
    
    Auto sync is not enabled.

이건 에러가 아니다.

말 그대로 **자동 동기화가 꺼져 있다** 는 뜻이다.

현재 상태는 이렇다.
    
    
    GitHub 변경 감지 가능
    하지만 자동으로 배포하지는 않음
    사용자가 SYNC 버튼을 눌러야 반영됨

즉, 지금은 수동 배포 방식이다.

실무에서는 보통 환경에 따라 다르게 둔다.
    
    
    dev 환경: auto sync 켜는 경우 많음
    prod 환경: 수동 sync 또는 승인 기반 배포를 많이 씀

지금 실습에서는 수동 sync여도 전혀 문제 없다.

* * *

# 6\. Tree 화면은 뭘 보여주는 걸까?

![](https://velog.velcdn.com/images/yorange50/post/68a26243-36d6-4fcd-8b2d-f085e6f7aae9/image.png)

두 번째 화면을 보면 리소스 관계가 트리로 나온다.
    
    
    osc
     ├── vas-svc
     ├── vas-deploy
     │    └── ReplicaSet
     │          └── Pod
     └── vas-ing

이 구조는 이렇게 이해하면 된다.
    
    
    Application
    ↓
    Service / Deployment / Ingress
    ↓
    Deployment가 ReplicaSet 생성
    ↓
    ReplicaSet이 Pod 생성

즉, Argo CD가 단순히 YAML 파일 목록만 보여주는 게 아니라, 실제 Kubernetes 리소스들이 어떤 관계로 연결되어 있는지 시각화해서 보여준다.

* * *

# 7\. 지금 생성된 리소스들

![](https://velog.velcdn.com/images/yorange50/post/a88f5eaf-3784-4d8e-b7eb-45decabedc80/image.png)

List 화면을 보면 이런 리소스들이 있다.
    
    
    vas-svc
    vas-deploy
    vas-ing
    ReplicaSet
    Pod 2개

핵심은 이 3개다.
    
    
    Service: vas-svc
    Deployment: vas-deploy
    Ingress: vas-ing

각각의 역할은 이렇다.

리소스 | 역할  
---|---  
Deployment | 애플리케이션 Pod를 띄우고 관리  
ReplicaSet | Pod 개수를 맞춰주는 중간 관리자  
Pod | 실제 컨테이너가 실행되는 단위  
Service | Pod에 접근할 수 있는 내부 고정 주소  
Ingress | 외부에서 도메인/URL로 접근하게 해주는 입구  
  
지금 Argo CD 결과 화면에서는 이 리소스들이 전부 `Healthy`, `Synced` 상태다.

* * *

# 8\. Pods 화면은 왜 Node가 보일까?

![](https://velog.velcdn.com/images/yorange50/post/e1beeae4-1836-41cc-a8cd-c2c303781342/image.png)

Pods 화면에서는 Node 기준으로 묶여 있다.
    
    
    k3d-my-cluster-agent-1
    k3d-my-cluster-server-0

이건 현재 클러스터에 노드가 2개 있고, Pod들이 그 노드 위에 올라가 있다는 뜻이다.
    
    
    Node = 쿠버네티스가 일하는 서버
    Pod = 그 서버 위에서 실행되는 애플리케이션 단위

화면에서 Pod 상태가 초록색으로 보이니까, Pod도 정상적으로 실행 중인 상태다.

* * *

# 9\. Network 화면은 뭘 보여주는 걸까?

![](https://velog.velcdn.com/images/yorange50/post/41f0b81c-12f2-4e3e-beee-e861d9f0dfab/image.png)

Network 화면에서는 이런 흐름이 보인다.
    
    
    외부 요청
    ↓
    172.19.0.5
    ↓
    vas-ing
    ↓
    vas-svc
    ↓
    Pod

이건 외부에서 들어온 요청이 Ingress를 거쳐 Service로 전달되고, Service가 뒤쪽 Pod로 연결해주는 구조다.

조금 쉽게 쓰면:
    
    
    Ingress = 건물 입구
    Service = 안내 데스크
    Pod = 실제 일하는 직원

사용자가 도메인으로 접근하면 먼저 Ingress가 받고, 그 요청을 Service로 넘기고, Service가 실제 Pod로 보내준다.

* * *

# 10\. Sync 버튼을 눌렀을 때 나온 화면

![](https://velog.velcdn.com/images/yorange50/post/92980638-5c44-44e6-8952-43ac3f8d8821/image.png) ![](https://velog.velcdn.com/images/yorange50/post/722b4c2c-7b7c-49bf-9c59-740b0bf96dfc/image.png) ![](https://velog.velcdn.com/images/yorange50/post/3fb51476-fbc2-4d06-a749-a819ca151a27/image.png)

Sync 창에는 이런 리소스들이 체크되어 있다.
    
    
    /service/vas/vas-svc
    /apps/deployment/vas/vas-deploy
    /networking.k8s.io/ingress/vas/vas-ing

이건 Argo CD가 동기화할 대상이다.

즉, 이번 배포에서 Argo CD가 GitHub manifest를 보고 아래 3개를 클러스터에 적용했다는 뜻이다.
    
    
    Service 생성
    Deployment 생성
    Ingress 생성

그리고 결과 화면에 이렇게 나온다.
    
    
    service/vas-svc created
    deployment.apps/vas-deploy created
    ingress.networking.k8s.io/vas-ing created

이건 진짜로 리소스 생성이 성공했다는 의미다.

* * *

# 11\. History and Rollback 화면은 왜 중요할까?

![](https://velog.velcdn.com/images/yorange50/post/a7dacebb-44c9-4f51-b97a-b2c4de0543a7/image.png)

마지막 화면에는 배포 기록이 나온다.
    
    
    Revision: e6e7936
    Author: Greenapple0101
    Message: Add vas gitops manifests
    Time to deploy: 1s
    Initiated by: admin

이건 Argo CD가 어떤 Git 커밋을 기준으로 배포했는지 기록해둔 것이다.

GitOps의 장점이 여기서 나온다.

문제가 생기면 예전 커밋으로 되돌릴 수 있다.
    
    
    잘못된 manifest push
    ↓
    Argo CD가 반영
    ↓
    문제 발생
    ↓
    이전 revision으로 rollback

그래서 Argo CD는 단순 배포 도구가 아니라, **Git 커밋 기반 배포 이력 관리 도구** 라고도 볼 수 있다.

* * *

# 12\. 지금 상태를 한 문장으로 정리하면

현재 상태는 아주 좋다.
    
    
    GitHub demo_gitops 저장소의 vas manifest를 Argo CD가 읽어서,
    Kubernetes 클러스터의 vas namespace에 Service, Deployment, Ingress를 생성했고,
    Pod도 정상 실행 중이며,
    Git 상태와 클러스터 상태가 일치해서 Healthy + Synced 상태

면접식으로 말하면 이렇게 말하면 된다.

> Argo CD에 GitHub repository를 연결하고, `vas` 경로의 Kubernetes manifest를 기준으로 Application을 생성했습니다. 이후 수동 Sync를 실행하자 Service, Deployment, Ingress가 클러스터의 `vas` namespace에 생성되었고, Argo CD 화면에서 App Health는 Healthy, Sync Status는 Synced로 표시되었습니다. 이는 Git에 선언된 desired state와 클러스터의 live state가 일치하며, 배포된 리소스들도 정상 상태라는 의미입니다.

* * *

# 13\. 실무적으로 중요한 포인트

여기서 배운 핵심은 단순히 “화면에 초록불 떴다”가 아니다.

진짜 중요한 건 이 흐름이다.
    
    
    1. Kubernetes YAML을 GitHub에 올림
    2. Argo CD가 GitHub repo를 바라봄
    3. Git에 있는 선언 상태를 읽음
    4. 클러스터에 적용함
    5. 실제 상태와 Git 상태를 계속 비교함
    6. 다르면 OutOfSync, 같으면 Synced
    7. 리소스가 정상 동작하면 Healthy

이게 GitOps의 기본 구조다.

즉, 이제부터 배포의 중심은 터미널에서 `kubectl apply`를 직접 치는 게 아니라, **Git에 manifest를 올리고 Argo CD가 클러스터 상태를 맞추게 하는 방식** 이 된다.
