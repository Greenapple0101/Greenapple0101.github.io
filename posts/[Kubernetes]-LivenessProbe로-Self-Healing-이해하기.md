---
title: "[Kubernetes] LivenessProbe로 Self-Healing 이해하기"
source: "https://velog.io/@yorange50/Kubernetes-LivenessProbe%EB%A1%9C-Self-Healing-%EC%9D%B4%ED%95%B4%ED%95%98%EA%B8%B0"
published: "Thu, 28 May 2026 23:55:20 GMT"
backup_date: "2026-05-29T14:51:00.477039"
---

쿠버네티스를 공부하다 보면 자주 나오는 말이 있다.

> 쿠버네티스는 Self-Healing을 지원한다.

처음 들으면 뭔가 엄청 대단한 기능처럼 느껴진다.

“쿠버네티스가 알아서 장애를 고쳐준다고?” “그럼 서버가 죽어도 자동으로 살아나는 건가?”

반은 맞고, 반은 조심해서 이해해야 한다.

쿠버네티스가 마법처럼 모든 장애를 해결해주는 건 아니다. 대신 **컨테이너가 비정상 상태라고 판단되면 다시 실행해주는 구조** 를 가지고 있다.

이때 가장 기본적으로 쓰이는 기능이 바로 **LivenessProbe** 다.

* * *

## 1\. Self-Healing이란?

Self-Healing은 말 그대로 **스스로 회복하는 기능** 이다.

예를 들어 애플리케이션에 문제가 생겼다고 해보자.
    
    
    Spring Boot 서버가 멈춤
    Node.js 프로세스가 죽음
    Python API 서버가 응답하지 않음
    Nginx가 비정상 상태가 됨

이런 상황에서 예전 방식이라면 사람이 직접 서버에 들어가야 했다.
    
    
    서버 접속
    프로세스 확인
    로그 확인
    재시작 명령 실행

하지만 쿠버네티스는 컨테이너 상태를 계속 확인하다가 문제가 있다고 판단하면 컨테이너를 다시 실행할 수 있다.

흐름은 단순하다.
    
    
    애플리케이션 이상 발생
            ↓
    쿠버네티스가 감지
            ↓
    컨테이너 재시작
            ↓
    서비스 복구

이게 쿠버네티스에서 말하는 Self-Healing이다.

* * *

## 2\. 쿠버네티스는 어떻게 이상을 감지할까?

컨테이너가 완전히 죽으면 쿠버네티스는 쉽게 알 수 있다.

컨테이너 안의 메인 프로세스가 종료되면 컨테이너도 종료된다.
    
    
    메인 프로세스 종료
            ↓
    컨테이너 종료
            ↓
    kubelet이 감지
            ↓
    컨테이너 재시작

여기까지는 쉽다.

그런데 문제는 애매한 상황이다.
    
    
    프로세스는 살아 있음
    하지만 요청 처리는 안 됨
    
    포트는 열려 있음
    하지만 내부적으로 deadlock 상태
    
    서버는 떠 있음
    하지만 /healthz가 500을 반환함

이런 경우 컨테이너는 죽지 않았다. 그래서 쿠버네티스 입장에서는 겉으로 봤을 때 정상처럼 보일 수 있다.

그래서 필요한 게 **Probe** 다.

* * *

## 3\. Probe란?

Probe는 쿠버네티스가 컨테이너 상태를 확인하기 위해 주기적으로 보내는 검사다.

쉽게 말하면 kubelet이 컨테이너에게 계속 물어보는 것이다.
    
    
    너 살아있어?
    너 요청 받을 수 있어?
    너 시작 완료됐어?

쿠버네티스에는 대표적으로 세 가지 Probe가 있다.

Probe | 의미  
---|---  
LivenessProbe | 컨테이너가 살아 있는지 확인  
ReadinessProbe | 트래픽을 받을 준비가 됐는지 확인  
StartupProbe | 애플리케이션 시작이 끝났는지 확인  
  
이 중에서 Self-Healing과 가장 직접적으로 연결되는 것이 **LivenessProbe** 다.

* * *

## 4\. LivenessProbe란?

LivenessProbe는 컨테이너가 살아 있는지 확인하는 검사다.

검사에 계속 실패하면 kubelet은 이렇게 판단한다.
    
    
    이 컨테이너는 살아 있는 척하고 있지만 실제로는 비정상이다.
    재시작해야 한다.

그러면 kubelet이 컨테이너를 종료하고 다시 실행한다.
    
    
    LivenessProbe 실패
            ↓
    kubelet이 비정상 판단
            ↓
    컨테이너 종료
            ↓
    restartPolicy에 따라 재시작

즉 LivenessProbe는 Self-Healing을 위한 **감지 장치** 라고 보면 된다.

* * *

## 5\. HTTP 방식 LivenessProbe 예시

가장 흔한 방식은 HTTP 요청으로 상태를 확인하는 방식이다.

예를 들어 애플리케이션이 `/healthz` 경로를 제공한다고 하자.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: liveness-demo
    spec:
      containers:
        - name: app
          image: nginx
          ports:
            - containerPort: 80
          livenessProbe:
            httpGet:
              path: /healthz
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3

이 설정은 이런 뜻이다.
    
    
    컨테이너 시작 후 10초 기다림
    5초마다 /healthz로 HTTP 요청
    3번 연속 실패하면 비정상으로 판단
    컨테이너 재시작

다만 기본 nginx 이미지는 `/healthz` 경로가 없을 수 있다. 그러면 404가 반환되고 Probe가 실패한다.

HTTP Probe는 응답 코드가 **200 이상 400 미만** 이면 성공으로 본다. 404는 실패다.

그래서 nginx로 간단히 테스트할 때는 `/` 경로를 쓰는 게 더 편하다.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: nginx-liveness
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3

이 경우 kubelet은 주기적으로 nginx의 `/` 경로를 확인한다.
    
    
    GET /
    응답 정상
    → 컨테이너 유지
    
    GET /
    응답 실패
    → 실패 횟수 증가
    
    3번 연속 실패
    → 컨테이너 재시작

* * *

## 6\. LivenessProbe 동작 흐름

전체 흐름은 이렇게 볼 수 있다.
    
    
    Pod 실행
       ↓
    컨테이너 시작
       ↓
    initialDelaySeconds만큼 대기
       ↓
    kubelet이 LivenessProbe 실행
       ↓
    성공?
       ├─ 성공 → 컨테이너 유지
       └─ 실패 → 실패 횟수 증가
                  ↓
            failureThreshold 초과?
                  ↓
            컨테이너 재시작

여기서 중요한 주체는 **kubelet** 이다.

API Server가 직접 컨테이너를 검사하는 것이 아니다. 각 노드의 kubelet이 자기 노드에 있는 컨테이너를 검사한다.

* * *

## 7\. exec 방식 LivenessProbe

HTTP 서버가 아니어도 LivenessProbe를 사용할 수 있다.

컨테이너 내부에서 명령어를 실행해서 상태를 확인할 수도 있다.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: exec-liveness
    spec:
      containers:
        - name: app
          image: busybox
          command:
            - sh
            - -c
            - "touch /tmp/healthy; sleep 30; rm -f /tmp/healthy; sleep 3600"
          livenessProbe:
            exec:
              command:
                - cat
                - /tmp/healthy
            initialDelaySeconds: 5
            periodSeconds: 5

이 예시는 처음에는 `/tmp/healthy` 파일이 존재한다.
    
    
    cat /tmp/healthy 성공
    → 정상

그런데 30초 뒤 파일이 삭제된다.
    
    
    cat /tmp/healthy 실패
    → LivenessProbe 실패
    → 컨테이너 재시작

즉 HTTP 요청이 아니어도 컨테이너 안에서 명령어를 실행해서 상태를 확인할 수 있다.

* * *

## 8\. TCP 방식 LivenessProbe

포트가 열려 있는지만 확인할 수도 있다.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: tcp-liveness
    spec:
      containers:
        - name: redis
          image: redis
          ports:
            - containerPort: 6379
          livenessProbe:
            tcpSocket:
              port: 6379
            initialDelaySeconds: 10
            periodSeconds: 5

이 설정은 Redis의 6379 포트가 열려 있는지 확인한다.
    
    
    6379 포트 연결 성공
    → 정상
    
    6379 포트 연결 실패
    → 비정상

다만 TCP 방식은 깊은 상태 점검에는 한계가 있다.

포트는 열려 있지만 내부 로직이 망가진 경우에도 정상으로 판단할 수 있기 때문이다.

* * *

## 9\. LivenessProbe 주요 옵션

자주 보는 옵션은 아래와 같다.

옵션 | 의미  
---|---  
initialDelaySeconds | 컨테이너 시작 후 첫 검사까지 기다리는 시간  
periodSeconds | 몇 초마다 검사할지  
timeoutSeconds | 검사 응답을 몇 초까지 기다릴지  
failureThreshold | 몇 번 실패하면 비정상으로 볼지  
successThreshold | 몇 번 성공해야 정상으로 볼지  
  
예시는 다음과 같다.
    
    
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3

뜻은 이렇다.
    
    
    시작 후 30초 기다림
    10초마다 검사
    응답은 3초까지 기다림
    3번 연속 실패하면 재시작

* * *

## 10\. LivenessProbe와 ReadinessProbe 차이

여기서 많이 헷갈린다.

둘 다 상태 체크처럼 보인다. 하지만 실패했을 때 결과가 다르다.
    
    
    LivenessProbe 실패
    → 컨테이너 재시작
    
    ReadinessProbe 실패
    → Service 트래픽 대상에서 제외

비교하면 이렇다.

구분 | LivenessProbe | ReadinessProbe  
---|---|---  
질문 | 살아 있나? | 요청 받을 준비가 됐나?  
실패 시 | 컨테이너 재시작 | Service Endpoint에서 제외  
목적 | Self-Healing | 트래픽 보호  
예시 | deadlock, 무한 대기 | DB 연결 전, 캐시 로딩 중  
  
핵심은 이거다.

> LivenessProbe는 죽이는 검사고, ReadinessProbe는 트래픽을 빼는 검사다.

그래서 준비가 잠깐 안 된 상태를 LivenessProbe 실패로 처리하면 위험하다.

예를 들어 앱이 뜨는 데 1분 걸리는데 LivenessProbe가 10초 뒤부터 검사한다고 하자.
    
    
    앱 시작 중
    ↓
    LivenessProbe 실패
    ↓
    컨테이너 재시작
    ↓
    다시 앱 시작 중
    ↓
    또 실패
    ↓
    CrashLoopBackOff

이런 상황을 피하려면 `initialDelaySeconds`를 충분히 주거나 `startupProbe`를 같이 쓰는 것이 좋다.

* * *

## 11\. StartupProbe는 언제 쓸까?

애플리케이션 시작이 느린 경우에는 StartupProbe를 사용하면 좋다.

StartupProbe가 성공하기 전까지는 LivenessProbe와 ReadinessProbe 검사를 미룰 수 있다.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: app-with-startup-probe
    spec:
      containers:
        - name: app
          image: my-app:1.0
          ports:
            - containerPort: 8080
    
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            failureThreshold: 30
            periodSeconds: 2
    
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 10
            failureThreshold: 3
    
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            periodSeconds: 5
            failureThreshold: 3

이 구조는 이렇게 이해하면 된다.
    
    
    StartupProbe
    → 처음 시작이 끝났는지 확인
    
    LivenessProbe
    → 시작 후 살아 있는지 확인
    
    ReadinessProbe
    → 트래픽 받을 준비가 됐는지 확인

* * *

## 12\. 실습 예시: 일부러 죽는 컨테이너 만들기

Self-Healing을 눈으로 보려면 일부러 실패하는 Pod를 만들면 된다.
    
    
    apiVersion: v1
    kind: Pod
    metadata:
      name: liveness-self-healing
    spec:
      containers:
        - name: app
          image: busybox
          command:
            - sh
            - -c
            - "touch /tmp/healthy; sleep 20; rm -f /tmp/healthy; sleep 3600"
          livenessProbe:
            exec:
              command:
                - cat
                - /tmp/healthy
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 2

적용한다.
    
    
    kubectl apply -f liveness-self-healing.yaml

상태를 계속 본다.
    
    
    kubectl get pod liveness-self-healing -w

처음에는 정상이다.
    
    
    liveness-self-healing   1/1   Running   0

20초 뒤 `/tmp/healthy` 파일이 삭제된다. 그러면 LivenessProbe가 실패하고 컨테이너가 재시작된다.

잠시 후 재시작 횟수가 증가한다.
    
    
    liveness-self-healing   1/1   Running   1

상세 이벤트를 보면 더 확실하다.
    
    
    kubectl describe pod liveness-self-healing

이런 이벤트를 볼 수 있다.
    
    
    Liveness probe failed
    Container app failed liveness probe, will be restarted
    Killing container
    Started container

이게 바로 LivenessProbe 기반 Self-Healing이다.

* * *

## 13\. 주의할 점

LivenessProbe는 좋은 기능이지만 잘못 설정하면 오히려 장애를 만들 수 있다.

### 1\. 너무 빠르게 검사하지 않기

앱이 뜨는 데 오래 걸리는데 검사 시간이 너무 빠르면 계속 재시작될 수 있다.
    
    
    initialDelaySeconds: 3
    periodSeconds: 5
    failureThreshold: 1

이런 설정은 위험할 수 있다.

앱이 아직 뜨는 중인데 실패로 판단해서 컨테이너를 계속 죽일 수 있기 때문이다.

* * *

### 2\. 외부 의존성을 LivenessProbe에 강하게 넣지 않기

예를 들어 `/healthz`에서 DB까지 검사한다고 하자.

DB가 잠깐 느려졌다.
    
    
    DB 일시 장애
    ↓
    /healthz 실패
    ↓
    앱 컨테이너 재시작
    ↓
    오히려 장애 확대

앱 자체는 살아 있는데 DB 때문에 LivenessProbe가 실패하면, 멀쩡한 앱 컨테이너까지 계속 재시작될 수 있다.

그래서 보통은 이렇게 나누는 것이 좋다.
    
    
    LivenessProbe
    → 내 프로세스가 회복 불가능하게 망가졌는가?
    
    ReadinessProbe
    → 지금 트래픽을 받아도 되는가?

DB, 외부 API, 메시지 큐 상태는 LivenessProbe보다 ReadinessProbe에서 다루는 경우가 많다.

* * *

### 3\. LivenessProbe는 만능이 아니다

LivenessProbe는 컨테이너 재시작으로 회복 가능한 문제에 적합하다.

하지만 이런 문제는 재시작만으로 해결되지 않을 수 있다.
    
    
    잘못된 이미지
    잘못된 환경변수
    DB 자체 장애
    Secret 누락
    ConfigMap 오류
    네트워크 정책 문제
    디스크 부족

이런 경우에는 컨테이너를 계속 재시작해도 다시 실패한다.

그러면 `CrashLoopBackOff` 상태에 빠질 수 있다.

* * *

## 14\. 한 번에 정리

LivenessProbe는 쿠버네티스가 컨테이너의 생존 상태를 확인하는 검사다.

검사에 계속 실패하면 kubelet이 컨테이너를 재시작한다.
    
    
    LivenessProbe 실패
    ↓
    컨테이너 비정상 판단
    ↓
    컨테이너 재시작
    ↓
    Self-Healing

Self-Healing은 이렇게 동작한다.
    
    
    감지: LivenessProbe
    판단: kubelet
    조치: 컨테이너 재시작
    복구: 새 컨테이너 실행

마지막으로 세 가지 Probe를 정리하면 이렇다.
    
    
    LivenessProbe
    = 살아 있는지 확인
    
    ReadinessProbe
    = 트래픽 받을 준비가 됐는지 확인
    
    StartupProbe
    = 처음 시작이 완료됐는지 확인

쿠버네티스가 알아서 회복한다는 말은, 아무 기준 없이 마법처럼 고쳐준다는 뜻이 아니다.

우리가 Probe로 **어떤 상태를 비정상으로 볼지** 알려주면, kubelet이 그 기준에 따라 컨테이너를 재시작해주는 것이다.

그래서 LivenessProbe는 쿠버네티스 Self-Healing을 이해할 때 가장 먼저 알아야 하는 기본 장치라고 보면 된다.
