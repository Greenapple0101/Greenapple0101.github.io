---
title: "[Kubernetes] 프로비저닝이란 무엇일까?"
source: "https://velog.io/@yorange50/Kubernetes-%ED%94%84%EB%A1%9C%EB%B9%84%EC%A0%80%EB%8B%9D%EC%9D%B4%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%BC%EA%B9%8C"
published: "Wed, 27 May 2026 18:50:52 GMT"
backup_date: "2026-05-29T14:51:00.491691"
---

Kubernetes에서 PV와 PVC를 공부하다 보면 이런 말이 나온다.
    
    
    정적 프로비저닝
    동적 프로비저닝
    StorageClass를 통한 동적 프로비저닝

처음 들으면 단어부터 어렵다.

“프로비저닝이 뭔데?” “그냥 생성이랑 다른 건가?” “PV/PVC랑 무슨 관계지?”

이번 글에서는 **프로비저닝** 이라는 개념을 쉽게 정리해본다.

* * *

## 1\. 프로비저닝이란?

프로비저닝은 영어로 `Provisioning`이다.

쉽게 말하면 **필요한 자원을 사용할 수 있는 상태로 준비해주는 과정** 이다.
    
    
    프로비저닝
    = 필요한 자원을 준비해서 쓸 수 있게 해주는 것

여기서 자원은 상황에 따라 달라질 수 있다.
    
    
    서버
    디스크
    네트워크
    계정
    권한
    스토리지
    데이터베이스

즉 프로비저닝은 단순히 “만든다”보다 조금 넓은 의미다.

그 자원을 실제로 사용할 수 있도록 준비하는 과정 전체를 말한다.

* * *

## 2\. 일상 비유로 이해하기

회사에 신입사원이 들어왔다고 해보자.

신입사원이 일을 하려면 여러 가지가 필요하다.
    
    
    노트북
    사내 계정
    이메일 계정
    출입카드
    업무 툴 권한
    VPN 권한

회사가 이것들을 준비해준다.
    
    
    신입사원 입사
        ↓
    노트북 지급
        ↓
    계정 생성
        ↓
    권한 부여
        ↓
    업무 가능 상태

이 과정이 프로비저닝이다.

즉 프로비저닝은 **누군가가 사용할 수 있도록 필요한 자원을 세팅해주는 일** 이다.

* * *

## 3\. 인프라에서 프로비저닝

인프라에서는 프로비저닝이라는 말을 더 자주 쓴다.

예를 들어 서버 하나를 준비한다고 해보자.

단순히 서버만 켜면 끝이 아니다.
    
    
    서버 생성
    OS 설치
    디스크 연결
    네트워크 설정
    방화벽 설정
    SSH 접속 설정
    필요한 패키지 설치
    서비스 실행 준비

이 모든 과정이 서버 프로비저닝에 포함될 수 있다.

클라우드에서는 이런 식이다.
    
    
    EC2 인스턴스 생성
    EBS 디스크 연결
    보안 그룹 설정
    키페어 설정
    VPC/Subnet 연결
    퍼블릭 IP 할당

즉 인프라에서 프로비저닝은:
    
    
    서비스가 동작할 수 있도록 필요한 인프라 자원을 준비하는 과정

이라고 보면 된다.

* * *

## 4\. Kubernetes에서 프로비저닝

Kubernetes에서도 프로비저닝이라는 말이 나온다.

특히 PV/PVC를 공부할 때 자주 나온다.

여기서 말하는 프로비저닝은 보통 **스토리지 프로비저닝** 이다.

즉:
    
    
    Pod가 사용할 저장 공간을 준비해주는 과정

이라고 보면 된다.

Pod는 기본적으로 언제든지 사라질 수 있다.
    
    
    Pod 삭제
        ↓
    Pod 내부 데이터도 사라질 수 있음

그래서 데이터가 유지되어야 하는 경우에는 외부 저장 공간이 필요하다.

이때 Kubernetes는 PV와 PVC를 사용한다.
    
    
    Pod → PVC → PV → 실제 저장소

여기서 PV를 준비하거나 자동으로 만들어주는 과정이 프로비저닝이다.

* * *

## 5\. PV와 PVC 다시 보기

PV는 `PersistentVolume`이다.
    
    
    PV = 실제 저장 공간

예를 들면 이런 것들이 PV가 될 수 있다.
    
    
    hostPath
    NFS
    AWS EBS
    GCP Persistent Disk
    Azure Disk
    Ceph
    Longhorn

PVC는 `PersistentVolumeClaim`이다.
    
    
    PVC = 저장 공간 요청서

Pod가 직접 PV를 고르는 게 아니라 PVC를 통해 요청한다.
    
    
    10Gi 저장 공간 주세요.
    ReadWriteOnce 방식이면 됩니다.

그러면 Kubernetes가 조건에 맞는 PV를 연결해준다.
    
    
    PVC 요청
       ↓
    PV 연결
       ↓
    Pod가 저장 공간 사용

이 과정에서 PV를 준비하는 방식이 바로 프로비저닝이다.

* * *

## 6\. 정적 프로비저닝

정적 프로비저닝은 관리자가 PV를 미리 만들어두는 방식이다.
    
    
    정적 프로비저닝
    = 사람이 PV를 미리 만들어두는 방식

흐름은 이렇다.
    
    
    1. 관리자가 PV를 미리 생성한다.
    2. 사용자가 PVC를 생성한다.
    3. Kubernetes가 조건에 맞는 PV를 찾는다.
    4. PV와 PVC가 연결된다.
    5. Pod가 PVC를 사용한다.

예를 들어 관리자가 먼저 PV를 만든다.
    
    
    apiVersion: v1
    kind: PersistentVolume
    metadata:
      name: my-pv
    spec:
      capacity:
        storage: 1Gi
      accessModes:
        - ReadWriteOnce
      hostPath:
        path: /mnt/data

이 PV는 이런 뜻이다.
    
    
    1Gi 저장 공간을 준비한다.
    ReadWriteOnce 방식으로 접근할 수 있다.
    실제 저장 위치는 노드의 /mnt/data다.

그다음 사용자가 PVC를 만든다.
    
    
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

PVC는 이렇게 요청한다.
    
    
    1Gi 저장 공간이 필요합니다.
    ReadWriteOnce 방식이면 됩니다.

Kubernetes는 PV와 PVC의 조건을 비교한다.
    
    
    PV: 1Gi 있음
    PVC: 1Gi 필요
    
    PV: ReadWriteOnce 가능
    PVC: ReadWriteOnce 요청
    
    → 조건이 맞음

그러면 PV와 PVC가 연결된다.
    
    
    my-pv ↔ my-pvc

이 상태를 `Bound`라고 한다.
    
    
    kubectl get pvc

출력 예시는 다음과 같다.
    
    
    NAME     STATUS   VOLUME   CAPACITY
    my-pvc   Bound    my-pv    1Gi

* * *

## 7\. 정적 프로비저닝의 특징

정적 프로비저닝은 구조가 단순하다.

관리자가 직접 PV를 만들어두기 때문에 실습할 때 이해하기 쉽다.

하지만 단점도 있다.
    
    
    PVC가 생길 때마다 관리자가 PV를 직접 만들어야 함
    요청이 많아지면 관리가 번거로움
    용량이나 accessModes가 안 맞으면 Pending 상태가 됨

즉 정적 프로비저닝은 작은 실습이나 고정된 환경에서는 괜찮지만, 실제 운영 환경에서는 불편할 수 있다.

* * *

## 8\. 동적 프로비저닝

동적 프로비저닝은 PVC 요청이 들어왔을 때 PV를 자동으로 만들어주는 방식이다.
    
    
    동적 프로비저닝
    = PVC 요청에 따라 PV를 자동으로 생성하는 방식

흐름은 이렇다.
    
    
    1. 사용자가 PVC를 생성한다.
    2. PVC에 StorageClass를 지정한다.
    3. Kubernetes가 StorageClass를 확인한다.
    4. 해당 StorageClass의 provisioner가 실제 저장소를 만든다.
    5. PV가 자동 생성된다.
    6. PVC와 PV가 연결된다.
    7. Pod가 PVC를 사용한다.

정적 프로비저닝과 가장 큰 차이는 이 부분이다.
    
    
    정적 프로비저닝
    → PV를 사람이 미리 만든다.
    
    동적 프로비저닝
    → PVC 요청을 보고 PV가 자동으로 만들어진다.

* * *

## 9\. StorageClass란?

동적 프로비저닝에서 중요한 개념이 `StorageClass`다.

StorageClass는 쉽게 말하면 **스토리지를 어떤 방식으로 만들지 정해둔 설정** 이다.
    
    
    StorageClass
    = PV 자동 생성 방식에 대한 템플릿

예를 들어 이런 식으로 생각할 수 있다.
    
    
    standard
    → 일반 디스크로 만들어줘
    
    fast
    → 빠른 SSD로 만들어줘
    
    nfs
    → NFS 기반으로 만들어줘
    
    longhorn
    → Longhorn 스토리지로 만들어줘

PVC는 StorageClass를 지정해서 요청한다.
    
    
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: dynamic-pvc
    spec:
      storageClassName: standard
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 10Gi

이 PVC는 이렇게 말하는 것이다.
    
    
    standard 방식으로 10Gi 저장 공간을 만들어주세요.
    ReadWriteOnce 방식으로 사용할게요.

그러면 Kubernetes는 `standard` StorageClass에 연결된 provisioner를 사용해서 실제 저장소를 만든다.

* * *

## 10\. provisioner란?

provisioner는 실제로 저장소를 만들어주는 역할을 한다.

예를 들어 클라우드 환경에서는 이런 일이 일어날 수 있다.
    
    
    PVC 생성
       ↓
    StorageClass 확인
       ↓
    AWS EBS 디스크 자동 생성
       ↓
    PV 자동 생성
       ↓
    PVC와 PV 연결

여기서 AWS EBS 디스크를 실제로 만들어주는 쪽이 provisioner다.

즉 provisioner는:
    
    
    PVC 요청을 보고 실제 스토리지를 생성해주는 담당자

라고 보면 된다.

* * *

## 11\. 정적 프로비저닝과 동적 프로비저닝 비교

구분 | 정적 프로비저닝 | 동적 프로비저닝  
---|---|---  
PV 생성 | 관리자가 미리 생성 | PVC 요청 시 자동 생성  
StorageClass | 필수는 아님 | 보통 필요  
운영 편의성 | 낮음 | 높음  
실습 이해도 | 쉬움 | 처음엔 약간 복잡  
사용 예시 | hostPath, NFS 실습 | 클라우드 디스크, Longhorn, CSI  
  
정리하면 이렇다.
    
    
    정적 프로비저닝
    → 사람이 미리 창고를 만들어둔다.
    
    동적 프로비저닝
    → 누가 창고를 요청하면 자동으로 새 창고를 만들어준다.

* * *

## 12\. PVC가 Pending인 이유

PV/PVC 실습을 하다 보면 PVC가 `Pending` 상태에 머무는 경우가 있다.
    
    
    kubectl get pvc
    
    
    NAME     STATUS    VOLUME   CAPACITY
    my-pvc   Pending

이 뜻은 아직 PVC가 사용할 PV를 찾지 못했다는 뜻이다.

가능한 원인은 다음과 같다.
    
    
    조건에 맞는 PV가 없음
    요청한 용량보다 작은 PV만 있음
    accessModes가 맞지 않음
    storageClassName이 맞지 않음
    동적 프로비저닝을 위한 StorageClass가 없음
    provisioner가 정상 동작하지 않음

예를 들어 PVC는 10Gi를 요청했는데, PV는 1Gi짜리밖에 없다면 연결되지 않는다.
    
    
    PVC: 10Gi 필요
    PV: 1Gi 있음
    
    → 조건 불일치
    → Pending

또 PVC는 `ReadWriteMany`를 요청했는데 PV는 `ReadWriteOnce`만 지원해도 연결되지 않는다.
    
    
    PVC: ReadWriteMany 필요
    PV: ReadWriteOnce 가능
    
    → 조건 불일치
    → Pending

* * *

## 13\. 프로비저닝 흐름 그림

정적 프로비저닝은 다음과 같다.
    
    
    관리자
      ↓
    PV 미리 생성
      ↓
    사용자 PVC 생성
      ↓
    Kubernetes가 PV/PVC 연결
      ↓
    Pod가 PVC 사용

동적 프로비저닝은 다음과 같다.
    
    
    사용자 PVC 생성
      ↓
    StorageClass 확인
      ↓
    provisioner가 실제 저장소 생성
      ↓
    PV 자동 생성
      ↓
    PVC와 PV 연결
      ↓
    Pod가 PVC 사용

Pod 입장에서는 둘 다 비슷하다.

Pod는 그냥 PVC를 참조한다.
    
    
    Pod → PVC → PV → 실제 저장소

PV가 미리 만들어졌든, 자동으로 만들어졌든 Pod는 PVC만 바라보면 된다.

* * *

## 14\. 프로비저닝을 왜 알아야 할까?

Kubernetes에서 애플리케이션을 운영하다 보면 상태가 있는 서비스가 필요하다.

예를 들면:
    
    
    MySQL
    PostgreSQL
    Redis
    MongoDB
    Jenkins
    Prometheus
    Grafana
    로그 저장소
    파일 업로드 서버

이런 서비스들은 데이터를 저장해야 한다.

Pod가 재시작될 때마다 데이터가 날아가면 안 된다.

그래서 PV/PVC가 필요하고, PV/PVC를 제대로 쓰려면 프로비저닝을 이해해야 한다.

특히 운영 환경에서는 매번 PV를 사람이 직접 만들기보다, StorageClass를 통한 동적 프로비저닝을 많이 사용한다.

* * *

## 15\. 정리

프로비저닝은 필요한 자원을 사용할 수 있는 상태로 준비해주는 과정이다.

Kubernetes의 PV/PVC에서는 주로 저장 공간을 준비하는 과정을 의미한다.

정리하면 다음과 같다.
    
    
    프로비저닝
    → 필요한 자원을 사용할 수 있게 준비하는 과정
    
    스토리지 프로비저닝
    → Pod가 사용할 저장 공간을 준비하는 과정
    
    정적 프로비저닝
    → 관리자가 PV를 미리 만들어두는 방식
    
    동적 프로비저닝
    → PVC 요청에 따라 PV를 자동으로 만들어주는 방식
    
    StorageClass
    → 동적 프로비저닝에서 어떤 방식으로 스토리지를 만들지 정하는 설정
    
    provisioner
    → 실제 저장소를 생성해주는 담당자

한 줄로 정리하면 이렇다.
    
    
    프로비저닝은 “필요한 자원을 만들어서 바로 쓸 수 있는 상태로 준비해주는 것”이다.

PV/PVC 관점에서는 이렇게 기억하면 된다.
    
    
    정적 프로비저닝
    = PV를 미리 만들어두고 PVC가 가져다 씀
    
    동적 프로비저닝
    = PVC가 요청하면 PV가 자동으로 만들어짐
