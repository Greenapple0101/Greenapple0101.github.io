---
title: "[Kubernetes] Helm values.yaml은 왜 쓰는 걸까?"
source: "https://velog.io/@yorange50/Kubernetes-Helm-values.yaml%EC%9D%80-%EC%99%9C-%EC%93%B0%EB%8A%94-%EA%B1%B8%EA%B9%8C"
published: "Wed, 27 May 2026 19:30:20 GMT"
backup_date: "2026-05-29T14:51:00.485580"
---

Kubernetes를 공부하다 보면 처음에는 YAML 파일을 직접 작성한다.
    
    
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    kubectl apply -f ingress.yaml

그런데 Prometheus, Grafana, OpenSearch 같은 도구를 설치하려고 하면 YAML 파일이 너무 많아진다.

Deployment, Service, ConfigMap, Secret, PVC, Ingress, ServiceAccount, Role, RoleBinding 등 필요한 리소스가 많기 때문이다.

이럴 때 사용하는 도구가 **Helm** 이고, Helm에서 설정값을 바꿀 때 사용하는 파일이 **values.yaml** 이다.

* * *

## 1\. Helm은 뭐였지?

Helm은 Kubernetes용 패키지 매니저다.

쉽게 말하면 Kubernetes 애플리케이션 설치 도구다.

Ubuntu에서 프로그램 설치할 때:
    
    
    apt install nginx

처럼 하듯이, Kubernetes에서는 Helm으로 복잡한 애플리케이션을 설치할 수 있다.

예를 들어 lecture-4에서는 Helm으로 Prometheus Stack을 설치했다.
    
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
      -f prometheus-custom-values.yaml \
      -n monitoring

이 명령어 하나로 Prometheus, Grafana, node-exporter 같은 여러 컴포넌트가 함께 설치된다. 

* * *

## 2\. Helm Chart란?

Helm에서 애플리케이션 설치 묶음을 **Chart** 라고 한다.
    
    
    Chart
    = Kubernetes YAML 템플릿 묶음

예를 들어 Prometheus Chart 안에는 이런 리소스 템플릿들이 들어 있을 수 있다.
    
    
    Deployment
    StatefulSet
    Service
    ConfigMap
    Secret
    ServiceAccount
    Ingress
    PVC

즉 Chart는 완성된 YAML 파일 하나가 아니라, 여러 Kubernetes 리소스를 만들 수 있는 템플릿 묶음이다.

* * *

## 3\. 그런데 왜 values.yaml이 필요할까?

Chart는 템플릿이다.

템플릿이라는 건 빈칸이 있다는 뜻이다.

예를 들어 이런 설정들은 환경마다 다를 수 있다.
    
    
    replica 개수
    image tag
    service type
    ingress host
    storage size
    storageClass
    resource request/limit
    admin password
    port 번호

모든 사람이 같은 설정으로 Prometheus나 OpenSearch를 설치하지는 않는다.

누구는 Grafana를 Ingress로 열고 싶고, 누구는 NodePort로 열고 싶을 수 있다.

누구는 저장 공간을 10Gi만 쓰고 싶고, 누구는 100Gi가 필요할 수 있다.

이런 차이를 Chart 코드 자체를 수정하지 않고 바꾸기 위해 사용하는 파일이 `values.yaml`이다.
    
    
    Chart
    = 설치 템플릿
    
    values.yaml
    = 템플릿에 넣을 설정값

* * *

## 4\. values.yaml은 설정값 파일이다

`values.yaml`은 Helm Chart에 전달하는 설정값 파일이다.

예를 들어 이런 식으로 생겼다.
    
    
    replicaCount: 2
    
    image:
      repository: nginx
      tag: "1.17"
    
    service:
      type: ClusterIP
      port: 80
    
    ingress:
      enabled: true
      host: nginx.192.168.164.4.sslip.io

이 파일은 직접 Kubernetes 리소스를 만드는 YAML은 아니다.

즉 이건 `kubectl apply -f values.yaml` 하는 파일이 아니다.
    
    
    values.yaml
    = Kubernetes 리소스 YAML이 아니라
      Helm Chart에 넣어주는 설정값 파일

이 차이가 진짜 중요하다.

* * *

## 5\. values.yaml과 template의 관계

Helm Chart 안에는 template 파일이 있다.

예를 들어 Deployment 템플릿이 이런 식일 수 있다.
    
    
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      replicas: {{ .Values.replicaCount }}
      template:
        spec:
          containers:
            - name: app
              image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"

여기서 이런 부분이 보인다.
    
    
    {{ .Values.replicaCount }}
    {{ .Values.image.repository }}
    {{ .Values.image.tag }}

이 값들은 `values.yaml`에서 가져온다.

values.yaml에 이렇게 되어 있으면:
    
    
    replicaCount: 2
    
    image:
      repository: nginx
      tag: "1.17"

Helm은 템플릿을 이렇게 바꿔준다.
    
    
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-app
    spec:
      replicas: 2
      template:
        spec:
          containers:
            - name: app
              image: "nginx:1.17"

즉 Helm은:
    
    
    template + values.yaml
    = 실제 Kubernetes YAML

을 만들어낸다.

* * *

## 6\. -f 옵션은 뭐야?

Helm 설치 명령어에서 자주 보는 옵션이 있다.
    
    
    -f prometheus-custom-values.yaml

이 `-f`는 values 파일을 지정하는 옵션이다.

lecture-4에서는 Prometheus Stack 설치할 때 custom values 파일을 넘겼다.
    
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
      -f prometheus-custom-values.yaml \
      -n monitoring

OpenSearch 설치할 때도 values 파일을 넘겼다.
    
    
    helm install opensearch opensearch-project/opensearch \
      -f opensearch-custom-values.yaml \
      -n monitoring

즉 `-f`는 이런 뜻이다.
    
    
    이 Chart를 설치하되,
    기본 설정 말고 내가 만든 values 파일 설정을 반영해서 설치해줘.

lecture-4에서는 Prometheus, OpenSearch, OpenSearch Dashboards, Fluent-bit 설치에 Helm과 custom values 파일을 사용했다. 

* * *

## 7\. 기본 values와 custom values

Helm Chart는 기본 values를 가지고 있다.

즉 사용자가 아무 설정을 안 줘도 기본값으로 설치될 수 있다.
    
    
    helm install my-app chart-name

하지만 실습이나 운영에서는 기본값만으로 부족한 경우가 많다.

예를 들어 Ingress host를 바꾸고 싶을 수 있다.
    
    
    ingress:
      enabled: true
      hosts:
        - grafana.192.168.164.4.sslip.io

또는 storageClass를 바꾸고 싶을 수 있다.
    
    
    persistence:
      enabled: true
      storageClass: local-path
      size: 10Gi

이럴 때 custom values 파일을 만든다.
    
    
    기본 values
    = Chart가 제공하는 기본 설정
    
    custom values
    = 내가 원하는 환경에 맞게 덮어쓰는 설정

* * *

## 8\. values.yaml은 설정 덮어쓰기 파일이다

values.yaml은 전체 YAML을 새로 만드는 파일이라기보다는, 기본 설정을 필요한 만큼 덮어쓰는 파일에 가깝다.

예를 들어 Chart 기본값이 이렇다고 해보자.
    
    
    service:
      type: ClusterIP
      port: 80

내가 values 파일에 이렇게 쓰면:
    
    
    service:
      type: NodePort

Helm은 `service.type`만 NodePort로 바꾸고, 나머지 기본값은 유지할 수 있다.

즉 values 파일은 필요한 설정만 바꿔도 된다.
    
    
    values.yaml은 모든 설정을 다 적는 파일이 아니라
    바꾸고 싶은 설정만 적는 파일로 많이 쓴다.

* * *

## 9\. Helm values에서 자주 바꾸는 것들

Helm values 파일에서 자주 바꾸는 값들은 대략 이렇다.
    
    
    image
    replicaCount
    service
    ingress
    resources
    persistence
    storageClass
    nodeSelector
    tolerations
    affinity
    env
    config
    admin password

하나씩 보면 다음과 같다.

* * *

## 10\. image 설정

어떤 컨테이너 이미지를 쓸지 정한다.
    
    
    image:
      repository: nginx
      tag: "1.17"
      pullPolicy: IfNotPresent

뜻은 이렇다.
    
    
    nginx:1.17 이미지를 사용한다.
    이미지가 이미 있으면 다시 받지 않는다.

* * *

## 11\. replicaCount 설정

Pod를 몇 개 띄울지 정한다.
    
    
    replicaCount: 2

뜻은 이렇다.
    
    
    Pod를 2개 띄운다.

Kubernetes Deployment의 `replicas`와 연결되는 경우가 많다.

* * *

## 12\. service 설정

Service 타입과 포트를 정한다.
    
    
    service:
      type: ClusterIP
      port: 80

뜻은 이렇다.
    
    
    ClusterIP 타입 Service를 만들고
    80번 포트로 노출한다.

Service 타입은 보통 이런 것들이 있다.
    
    
    ClusterIP
    NodePort
    LoadBalancer

* * *

## 13\. ingress 설정

Ingress를 사용할지, 어떤 host로 열지 정한다.
    
    
    ingress:
      enabled: true
      className: nginx
      hosts:
        - host: grafana.192.168.164.4.sslip.io
          paths:
            - path: /
              pathType: Prefix

뜻은 이렇다.
    
    
    Ingress를 사용한다.
    nginx Ingress Controller를 사용한다.
    grafana.192.168.164.4.sslip.io로 접속할 수 있게 한다.

lecture-4에서도 Prometheus와 Grafana를 Ingress로 외부에 노출했다. Prometheus는 `prometheus.192.168.164.4.sslip.io`, Grafana는 `grafana.192.168.164.4.sslip.io` host를 사용했다. 

* * *

## 14\. resources 설정

Pod가 사용할 CPU와 Memory 요청량/제한량을 정한다.
    
    
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi

뜻은 이렇다.
    
    
    최소 이 정도 자원은 필요하다: requests
    최대 이 정도까지만 쓰게 한다: limits

Kubernetes에서 request/limit은 스케줄링과 자원 제한에 중요하다.

* * *

## 15\. persistence 설정

데이터를 유지할지 정한다.
    
    
    persistence:
      enabled: true
      storageClass: local-path
      size: 10Gi

뜻은 이렇다.
    
    
    데이터를 유지하기 위해 PVC를 사용한다.
    local-path StorageClass를 사용한다.
    10Gi 저장 공간을 요청한다.

Prometheus나 OpenSearch처럼 데이터를 저장하는 도구에서는 이 설정이 중요하다.

OpenSearch는 로그와 인덱스를 저장해야 하므로 PV가 필요하다. lecture-4에서도 OpenSearch 설치 시 PV가 필요하며, 환경에 따라 Local Path Provisioner가 필요할 수 있다고 설명되어 있다. 

* * *

## 16\. values.yaml이 실제로 하는 일

Helm 설치 흐름은 이렇게 보면 된다.
    
    
    1. helm install 명령 실행
    
    2. Helm이 Chart를 읽음
    
    3. Chart의 template 파일을 읽음
    
    4. 기본 values와 custom values를 합침
    
    5. template 안의 {{ .Values.xxx }} 부분에 값 주입
    
    6. 실제 Kubernetes YAML 생성
    
    7. Kubernetes API Server에 리소스 생성 요청

그림처럼 보면 이렇다.
    
    
    Chart templates
          +
    values.yaml
          ↓
    렌더링
          ↓
    실제 Kubernetes YAML
          ↓
    API Server에 적용

즉 Helm values는 Kubernetes에 바로 적용되는 파일이 아니라, **Kubernetes YAML을 만들기 위한 입력값** 이다.

* * *

## 17\. helm install과 helm upgrade

처음 설치할 때는 `helm install`을 쓴다.
    
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
      -f prometheus-custom-values.yaml \
      -n monitoring

이미 설치한 Helm release의 설정을 바꾸고 싶으면 `helm upgrade`를 쓴다.
    
    
    helm upgrade prometheus prometheus-community/kube-prometheus-stack \
      -f prometheus-custom-values.yaml \
      -n monitoring

즉:
    
    
    helm install
    = 처음 설치
    
    helm upgrade
    = 기존 설치를 values 변경 내용으로 업데이트

만약 같은 release 이름으로 다시 install 하려고 하면 이런 에러가 날 수 있다.
    
    
    cannot reuse a name that is still in use

이건 이미 같은 이름의 Helm release가 있기 때문이다.

이때는 `helm upgrade`를 쓰거나, 기존 release를 지우고 다시 설치해야 한다.
    
    
    helm uninstall prometheus -n monitoring

lecture-4에서도 Prometheus Stack 삭제 시 `helm uninstall prometheus -n monitoring` 명령을 사용했다. 

* * *

## 18\. helm get values

설치된 release에 적용된 values를 보고 싶으면 이렇게 한다.
    
    
    helm get values prometheus -n monitoring

전체 values까지 보고 싶으면:
    
    
    helm get values prometheus -n monitoring --all

차이는 이렇다.
    
    
    helm get values
    → 사용자가 직접 덮어쓴 values 중심으로 확인
    
    helm get values --all
    → 기본값까지 포함해서 전체 values 확인

* * *

## 19\. helm show values

Chart가 어떤 values를 지원하는지 보고 싶으면 다음 명령어를 쓴다.
    
    
    helm show values prometheus-community/kube-prometheus-stack

OpenSearch라면:
    
    
    helm show values opensearch-project/opensearch

이 명령어는 Chart의 기본 values를 보여준다.

그래서 custom values 파일을 만들기 전에 보통 이렇게 확인한다.
    
    
    1. helm show values로 기본 설정 확인
    2. 필요한 부분만 복사
    3. custom-values.yaml에 수정
    4. helm install -f custom-values.yaml로 설치

* * *

## 20\. values.yaml을 공부하는 방법

처음부터 values.yaml 전체를 다 이해하려고 하면 너무 어렵다.

Chart values는 굉장히 길 수 있다.

그래서 처음에는 자주 바꾸는 것만 보면 된다.
    
    
    ingress
    service
    resources
    persistence
    storageClass
    replicaCount
    image

특히 실습에서는 이 네 가지를 우선 보면 좋다.
    
    
    1. 어디로 접속할 것인가?
       → ingress, service
    
    2. 몇 개 띄울 것인가?
       → replicaCount
    
    3. 자원을 얼마나 줄 것인가?
       → resources
    
    4. 데이터를 저장할 것인가?
       → persistence, storageClass

* * *

## 21\. 정리

Helm values.yaml은 Helm Chart의 설정값을 바꾸는 파일이다.

정리하면 다음과 같다.
    
    
    Helm
    → Kubernetes 애플리케이션을 설치/관리하는 패키지 매니저
    
    Chart
    → Kubernetes 리소스 템플릿 묶음
    
    values.yaml
    → Chart 템플릿에 넣어줄 설정값 파일
    
    -f 옵션
    → 내가 만든 values 파일을 Helm 설치/업그레이드에 반영
    
    template
    → 실제 Kubernetes YAML이 만들어지기 전의 틀
    
    helm install
    → 처음 설치
    
    helm upgrade
    → 기존 release 설정 변경
    
    helm show values
    → Chart가 지원하는 기본 values 확인
    
    helm get values
    → 설치된 release에 적용된 values 확인

한 줄로 정리하면 이렇다.
    
    
    values.yaml은 Helm Chart를 내 환경에 맞게 설치하기 위한 설정값 파일이다.

조금 더 쉽게 말하면:
    
    
    Chart가 음식 레시피라면,
    values.yaml은 맵기, 양, 토핑, 포장 여부를 정하는 주문 옵션이다.

즉 Helm을 쓴다는 건 YAML을 안 보는 게 아니라, **수많은 Kubernetes YAML을 values.yaml이라는 설정 파일로 조절하는 방식** 을 쓰는 것이다.
