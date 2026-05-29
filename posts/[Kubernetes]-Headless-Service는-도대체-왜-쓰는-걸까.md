---
title: "[Kubernetes] Headless Service는 도대체 왜 쓰는 걸까?"
source: "https://velog.io/@yorange50/Kubernetes-Headless-Service%EB%8A%94-%EB%8F%84%EB%8C%80%EC%B2%B4-%EC%99%9C-%EC%93%B0%EB%8A%94-%EA%B1%B8%EA%B9%8C"
published: "Thu, 28 May 2026 23:53:23 GMT"
backup_date: "2026-05-29T14:51:00.480022"
---

쿠버네티스에서 Service를 배우다 보면 보통 이런 식으로 이해한다.

> Pod는 계속 죽고 다시 생기니까 IP가 바뀐다. 그래서 Service가 고정된 주소 역할을 해준다.

맞는 말이다. 일반적인 Service는 여러 Pod 앞에 하나의 고정된 입구를 만들어준다.

그런데 쿠버네티스에는 조금 특이한 Service가 있다.

바로 **Headless Service** 다.

이름부터 이상하다.

> Headless? 머리가 없다는 뜻인가? Service인데 서비스 역할을 안 한다는 건가?

반쯤 맞다.

* * *

## 1\. 일반 Service는 어떤 역할을 할까?

일반적인 ClusterIP Service를 먼저 보자.
    
    
    apiVersion: v1
    kind: Service
    metadata:
      name: my-service
    spec:
      selector:
        app: my-app
      ports:
        - port: 80
          targetPort: 8080

이 Service는 `app: my-app` 라벨을 가진 Pod들을 찾아서 연결해준다.

예를 들어 Pod가 3개 있다고 하자.
    
    
    Pod A: 10.42.0.10
    Pod B: 10.42.0.11
    Pod C: 10.42.0.12

일반 Service는 이 Pod들 앞에 가상의 IP 하나를 만들어준다.
    
    
    my-service -> 10.43.100.50

사용자는 Pod IP를 직접 몰라도 된다.
    
    
    my-service:80

이렇게 접근하면 Kubernetes가 알아서 Pod 중 하나로 트래픽을 보내준다.

즉 일반 Service는 이런 역할을 한다.
    
    
    클라이언트
       |
       v
    Service IP
       |
       v
    Pod A / Pod B / Pod C 중 하나

여기서 중요한 점은 클라이언트 입장에서는 **뒤에 Pod가 몇 개인지, 각각 IP가 뭔지 모른다** 는 것이다.

그냥 Service 하나만 바라본다.

* * *

## 2\. 그런데 왜 Headless Service가 필요할까?

일반 Service는 편하다.

그런데 어떤 경우에는 문제가 된다.

예를 들어 데이터베이스 클러스터를 생각해보자.
    
    
    mysql-0
    mysql-1
    mysql-2

이런 Pod들이 있을 때, 클라이언트가 단순히 “아무 Pod나 하나”로 연결되면 안 될 수 있다.

예를 들어 이런 상황이 있다.
    
    
    mysql-0 = primary
    mysql-1 = replica
    mysql-2 = replica

이 경우에는 각 Pod를 구분해야 한다.
    
    
    mysql-0으로 접속해야 하는 경우
    mysql-1로 접속해야 하는 경우
    mysql-2로 접속해야 하는 경우

그런데 일반 Service는 Pod들을 하나로 묶어서 감춘다.
    
    
    mysql-service -> Pod 중 하나

이러면 클라이언트가 특정 Pod를 직접 선택하기 어렵다.

즉 일반 Service는 “대표 번호” 같은 느낌이다.
    
    
    회사 대표번호로 전화하면 누가 받을지 모름

반면 어떤 시스템은 이렇게 해야 한다.
    
    
    mysql-0에게 직접 전화
    mysql-1에게 직접 전화
    mysql-2에게 직접 전화

이때 쓰는 게 **Headless Service** 다.

* * *

## 3\. Headless Service란?

Headless Service는 쉽게 말하면

> Service IP를 만들지 않는 Service

다.

일반 Service는 ClusterIP를 가진다.
    
    
    my-service -> 10.43.100.50

하지만 Headless Service는 ClusterIP가 없다.
    
    
    clusterIP: None

예시는 이렇게 생겼다.
    
    
    apiVersion: v1
    kind: Service
    metadata:
      name: mysql
    spec:
      clusterIP: None
      selector:
        app: mysql
      ports:
        - port: 3306
          targetPort: 3306

핵심은 이 부분이다.
    
    
    clusterIP: None

이렇게 하면 Kubernetes가 Service용 가상 IP를 만들지 않는다.

* * *

## 4\. 그러면 Service가 아무것도 안 하는 거 아냐?

처음 보면 그렇게 느껴진다.

> ClusterIP도 없으면 Service가 왜 필요하지?

하지만 Headless Service는 여전히 중요한 일을 한다.

바로 **DNS 조회 결과로 Pod들의 IP를 직접 돌려준다.**

일반 Service는 DNS를 조회하면 Service IP가 나온다.
    
    
    my-service.default.svc.cluster.local
    -> 10.43.100.50

그런데 Headless Service는 DNS를 조회하면 Pod IP들이 나온다.
    
    
    mysql.default.svc.cluster.local
    -> 10.42.0.10
    -> 10.42.0.11
    -> 10.42.0.12

즉 일반 Service는 이렇게 말한다.
    
    
    나한테 와. 내가 알아서 Pod 중 하나로 보내줄게.

Headless Service는 이렇게 말한다.
    
    
    내가 Pod들의 주소를 알려줄게. 네가 직접 골라서 가.

이 차이가 핵심이다.

* * *

## 5\. 일반 Service와 Headless Service 차이

구분 | 일반 Service | Headless Service  
---|---|---  
ClusterIP | 있음 | 없음  
설정 | 기본값 | `clusterIP: None`  
DNS 결과 | Service IP 반환 | Pod IP 목록 반환  
로드밸런싱 | Kubernetes가 해줌 | 클라이언트가 직접 처리  
Pod 직접 접근 | 어려움 | 가능  
주 사용처 | 일반 웹/API 서버 | StatefulSet, DB, Kafka, Redis Cluster 등  
  
* * *

## 6\. Headless Service는 언제 쓸까?

대표적으로 **StatefulSet** 과 같이 많이 쓴다.

StatefulSet은 Pod 이름이 고정된다.
    
    
    mysql-0
    mysql-1
    mysql-2

Deployment는 Pod 이름이 랜덤하다.
    
    
    my-app-7d8f9c9d5b-x92ks
    my-app-7d8f9c9d5b-abc12

하지만 StatefulSet은 순서와 이름이 있다.
    
    
    mysql-0
    mysql-1
    mysql-2

이때 Headless Service를 붙이면 각 Pod에 안정적인 DNS 주소가 생긴다.
    
    
    mysql-0.mysql.default.svc.cluster.local
    mysql-1.mysql.default.svc.cluster.local
    mysql-2.mysql.default.svc.cluster.local

이게 진짜 중요하다.

Pod IP는 바뀔 수 있다. 하지만 StatefulSet의 Pod 이름과 DNS 주소는 안정적으로 유지된다.

그래서 클러스터형 애플리케이션에서 많이 쓴다.

예를 들면 이런 것들이다.
    
    
    MySQL
    PostgreSQL
    MongoDB
    Redis Cluster
    Kafka
    Zookeeper
    Elasticsearch
    OpenSearch

이런 애들은 단순히 아무 Pod나 연결되면 되는 게 아니라, 각 노드가 서로를 알아야 한다.
    
    
    나는 kafka-0이고
    너는 kafka-1이고
    쟤는 kafka-2야

이런 식으로 서로의 정체성을 알아야 한다.

그럴 때 Headless Service가 필요하다.

* * *

## 7\. 예시로 이해하기

StatefulSet이 있다고 하자.
    
    
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: mysql
    spec:
      serviceName: mysql
      replicas: 3
      selector:
        matchLabels:
          app: mysql
      template:
        metadata:
          labels:
            app: mysql
        spec:
          containers:
            - name: mysql
              image: mysql:8
              ports:
                - containerPort: 3306

여기서 중요한 부분은 이것이다.
    
    
    serviceName: mysql

StatefulSet은 이 `serviceName`에 적힌 Service를 이용해서 Pod DNS를 만든다.

그래서 보통 Headless Service를 같이 만든다.
    
    
    apiVersion: v1
    kind: Service
    metadata:
      name: mysql
    spec:
      clusterIP: None
      selector:
        app: mysql
      ports:
        - port: 3306
          targetPort: 3306

그러면 각 Pod는 이런 주소를 가진다.
    
    
    mysql-0.mysql.default.svc.cluster.local
    mysql-1.mysql.default.svc.cluster.local
    mysql-2.mysql.default.svc.cluster.local

이제 애플리케이션은 특정 Pod를 직접 바라볼 수 있다.
    
    
    mysql-0.mysql.default.svc.cluster.local:3306

* * *

## 8\. 일반 Service로는 안 되는 걸까?

완전히 안 되는 건 아니다.

일반 Service도 Pod들에게 트래픽을 보내줄 수 있다.

하지만 일반 Service는 Pod들을 하나의 묶음으로 감춘다.
    
    
    mysql-service

이 주소로 접속하면 어떤 Pod로 갈지 모른다.

그런데 Stateful 애플리케이션에서는 이런 게 필요할 수 있다.
    
    
    primary 노드는 어디인지
    replica 노드는 어디인지
    각 노드가 어떤 순서인지
    각 노드가 어떤 데이터를 가지고 있는지

이런 정보를 다뤄야 한다.

그래서 단순 로드밸런싱보다 **개별 Pod 식별** 이 더 중요하다.

Headless Service는 바로 이 문제를 해결한다.

* * *

## 9\. Headless Service를 한 문장으로 정리하면

Headless Service는

> Service IP를 만들지 않고, DNS를 통해 Pod들의 실제 주소를 직접 알려주는 Service

다.

조금 더 쉽게 말하면

> 일반 Service는 대표번호 Headless Service는 직원별 직통번호 목록

이다.

일반 Service:
    
    
    회사 대표번호로 전화
    -> 누가 받을지는 모름

Headless Service:
    
    
    직원별 번호를 알고 직접 전화
    -> mysql-0, mysql-1, mysql-2를 구분 가능

* * *

## 10\. 정리

Headless Service는 처음 보면 이상하다.

Service인데 ClusterIP가 없다.

그래서 “이게 뭐 하는 거지?” 싶다.

하지만 핵심은 단순하다.

일반 Service는 Pod들을 감추고 하나의 IP로 묶는다.
    
    
    Service IP 하나 제공

Headless Service는 Pod들을 감추지 않고 직접 보여준다.
    
    
    Pod IP 목록 제공

그래서 Headless Service는 보통 이런 상황에서 쓴다.
    
    
    Pod를 각각 구분해야 할 때
    StatefulSet을 사용할 때
    DB, Kafka, Redis, Zookeeper처럼 노드 정체성이 중요한 시스템을 만들 때
    클라이언트가 직접 로드밸런싱하거나 특정 Pod를 선택해야 할 때

결국 Headless Service는 “로드밸런싱용 Service”라기보다는

> Pod들의 안정적인 네트워크 주소를 만들어주는 장치

에 가깝다.

그래서 StatefulSet을 배우면 거의 반드시 같이 나온다.
    
    
    StatefulSet = 이름이 고정된 Pod
    Headless Service = 그 Pod에 안정적인 DNS 주소를 붙여주는 Service

이렇게 이해하면 된다.
