---
title: "[Kubernetes] 로컬에서 k3d 클러스터 만들고 LoadBalancer 포트 열기"
source: "https://velog.io/@yorange50/Kubernetes-로컬에서-k3d-클러스터-만들고-LoadBalancer-포트-열기"
published: "2026-05-06T22:00:48.887Z"
tags: ""
backup_date: "2026-05-29T14:52:52.774813"
---

![](https://velog.velcdn.com/images/yorange50/post/d4c39157-4ed9-4955-846f-baccb49175ea/image.png)

이번에는 로컬 환경에서 `k3d`를 사용해 Kubernetes 클러스터를 만들고, `80`, `443` 포트를 LoadBalancer에 연결하는 작업을 진행했다. 처음에는 `-p 80:80@loadbalancer`, `-p 443:443@loadbalancer` 옵션이 무슨 의미인지 헷갈렸는데, 정리해보면 로컬 PC의 포트를 k3d 클러스터 안의 LoadBalancer 컨테이너로 연결하는 설정이었다.

## 1. k3d란?

`k3d`는 로컬 Docker 환경 위에 가벼운 Kubernetes 클러스터를 만들어주는 도구다.

정확히는 `k3s`라는 경량 Kubernetes 배포판을 Docker 컨테이너 안에서 실행할 수 있게 도와준다.

즉, 로컬 PC에 직접 무거운 Kubernetes를 설치하는 것이 아니라 Docker 컨테이너로 Kubernetes 클러스터를 띄우는 방식이다.

구조를 단순하게 보면 다음과 같다.

```text
로컬 PC
↓
Docker Desktop
↓
k3d
↓
k3s Kubernetes Cluster
```

이번 작업에서는 로컬에서 `board-cluster`라는 이름의 k3d 클러스터를 생성했다.

## 2. LoadBalancer 포트 매핑이란?

상사가 준 옵션은 다음과 같았다.

```bash
-p "80:80@loadbalancer"
-p "443:443@loadbalancer"
```

처음에는 일반 Docker의 포트 매핑처럼 보였는데, 뒤에 `@loadbalancer`가 붙어 있었다.

일반 Docker 포트 매핑은 보통 이렇게 쓴다.

```bash
docker run -p 80:80 nginx
```

이 뜻은 다음과 같다.

```text
로컬 PC의 80번 포트 → 컨테이너 내부의 80번 포트
```

그런데 k3d에서는 다음과 같이 쓸 수 있다.

```bash
-p "80:80@loadbalancer"
```

이 의미는 다음과 같다.

```text
로컬 PC의 80번 포트 → k3d LoadBalancer의 80번 포트
```

즉, 내 브라우저에서 `http://localhost`로 접근하면 로컬 PC의 80번 포트로 요청이 들어오고, 이 요청이 k3d 클러스터의 LoadBalancer 컨테이너로 전달된다.

HTTPS용 포트도 마찬가지다.

```bash
-p "443:443@loadbalancer"
```

이 뜻은 다음과 같다.

```text
로컬 PC의 443번 포트 → k3d LoadBalancer의 443번 포트
```

정리하면 다음과 같다.

| 옵션                     | 의미                                       |
| ---------------------- | ---------------------------------------- |
| `80:80@loadbalancer`   | 로컬 80번 포트를 k3d LoadBalancer 80번 포트에 연결   |
| `443:443@loadbalancer` | 로컬 443번 포트를 k3d LoadBalancer 443번 포트에 연결 |

## 3. 왜 80번과 443번 포트를 여는가?

웹 서비스에서 대표적인 포트는 `80`과 `443`이다.

| 포트  | 용도    |
| --- | ----- |
| 80  | HTTP  |
| 443 | HTTPS |

브라우저에서 다음처럼 접속하면 기본적으로 80번 포트를 사용한다.

```text
http://localhost
```

그리고 다음처럼 접속하면 443번 포트를 사용한다.

```text
https://localhost
```

그래서 로컬 Kubernetes 환경에서도 실제 웹 서비스처럼 접근하기 위해 80번과 443번 포트를 LoadBalancer에 연결한 것이다.

## 4. 클러스터 생성 명령어

PowerShell에서 다음 명령어를 실행했다.

```powershell
k3d cluster create board-cluster `
  -p "80:80@loadbalancer" `
  -p "443:443@loadbalancer"
```

여기서 백틱(`)은 PowerShell에서 줄바꿈을 위한 문자다.

Linux나 macOS의 쉘에서는 보통 `\`를 쓰지만, PowerShell에서는 백틱을 쓴다.

즉, 위 명령어는 한 줄로 쓰면 다음과 같다.

```powershell
k3d cluster create board-cluster -p "80:80@loadbalancer" -p "443:443@loadbalancer"
```

명령어를 분해하면 다음과 같다.

| 부분                          | 의미                           |
| --------------------------- | ---------------------------- |
| `k3d cluster create`        | k3d 클러스터 생성                  |
| `board-cluster`             | 클러스터 이름                      |
| `-p "80:80@loadbalancer"`   | 로컬 80번 포트를 LoadBalancer에 연결  |
| `-p "443:443@loadbalancer"` | 로컬 443번 포트를 LoadBalancer에 연결 |

## 5. 실행 로그 확인

클러스터를 생성했더니 다음과 같은 로그가 출력되었다.

```text
INFO[0000] portmapping '80:80' targets the loadbalancer
INFO[0000] portmapping '443:443' targets the loadbalancer
INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-board-cluster'
INFO[0000] Created image volume k3d-board-cluster-images
INFO[0000] Starting new tools node...
INFO[0001] Creating node 'k3d-board-cluster-server-0'
INFO[0003] Pulling image 'docker.io/rancher/k3s:v1.31.5-k3s1'
INFO[0008] Creating LoadBalancer 'k3d-board-cluster-serverlb'
INFO[0027] Cluster 'board-cluster' created successfully!
```

여기서 중요한 부분은 다음이다.

```text
Cluster 'board-cluster' created successfully!
```

이 로그가 나오면 클러스터 생성이 성공한 것이다.

또한 다음 로그도 중요하다.

```text
Creating LoadBalancer 'k3d-board-cluster-serverlb'
```

이것은 k3d가 로컬용 LoadBalancer 컨테이너를 만들었다는 뜻이다.

## 6. 현재 만들어진 구조

이번 명령어를 실행하면 내부적으로 다음과 같은 구조가 만들어진다.

```text
Windows 로컬 PC
↓
Docker Desktop
↓
k3d board-cluster
├── k3d-board-cluster-server-0
└── k3d-board-cluster-serverlb
```

여기서 `server-0`은 Kubernetes 서버 노드 역할을 한다.

`serverlb`는 LoadBalancer 역할을 한다.

즉, `-p "80:80@loadbalancer"` 옵션은 로컬 PC의 80번 포트를 `serverlb` 쪽으로 연결하는 설정이라고 보면 된다.

## 7. kubectl 연결 확인

클러스터 생성 후 `kubectl`이 정상적으로 클러스터에 연결되는지 확인했다.

```powershell
kubectl cluster-info
```

실행 결과는 다음과 같았다.

```text
Kubernetes control plane is running at https://host.docker.internal:50908
CoreDNS is running at https://host.docker.internal:50908/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
Metrics-server is running at https://host.docker.internal:50908/api/v1/namespaces/kube-system/services/https:metrics-server:https/proxy
```

여기서 중요한 부분은 다음이다.

```text
Kubernetes control plane is running
```

이 문구가 보이면 `kubectl`이 Kubernetes API 서버에 정상적으로 접근하고 있다는 뜻이다.

## 8. host.docker.internal은 무엇인가?

출력 결과에 다음 주소가 보였다.

```text
https://host.docker.internal:50908
```

처음 보면 낯설 수 있다.

`host.docker.internal`은 Docker 컨테이너 환경에서 호스트 PC를 가리키기 위해 사용하는 주소다.

Windows 로컬 환경에서 Docker 안에 있는 k3d 클러스터와 내 로컬 환경이 통신할 때 이런 주소가 사용된다.

즉, 이상한 에러가 아니라 로컬 Docker 기반 Kubernetes 환경에서 자연스럽게 나오는 주소다.

## 9. 이번 작업에서 완료한 것

이번에 완료한 작업은 다음과 같다.

```text
Docker Desktop 실행
k3d 설치
k3d 클러스터 생성
80번 포트 LoadBalancer 매핑
443번 포트 LoadBalancer 매핑
kubectl cluster-info로 클러스터 연결 확인
```

보고용으로 정리하면 다음과 같이 말할 수 있다.

```text
로컬 Docker 환경에서 k3d board-cluster 생성 완료했습니다.

생성 옵션:
-p "80:80@loadbalancer"
-p "443:443@loadbalancer"

kubectl cluster-info 확인 결과,
Kubernetes control plane, CoreDNS, metrics-server 정상 동작 확인했습니다.
```

## 10. 아직 하지 않은 것

이번 작업은 클러스터 생성과 포트 매핑까지만 진행했다.

아직 다음 작업은 하지 않았다.

```text
애플리케이션 Pod 배포
Service 생성
Ingress 생성
localhost 접속 테스트
```

즉, 현재 상태는 “웹 애플리케이션을 올린 상태”가 아니라, “웹 애플리케이션을 올릴 수 있는 로컬 Kubernetes 환경을 만든 상태”다.

## 11. 전체 흐름 정리

최종 흐름은 다음과 같다.

```text
1. Docker Desktop 실행
2. k3d 설치
3. k3d cluster create 명령어 실행
4. 80/443 포트를 LoadBalancer에 매핑
5. k3d 클러스터 생성 완료
6. kubectl cluster-info로 연결 확인
```

명령어 기준으로 보면 다음과 같다.

```powershell
k3d cluster create board-cluster `
  -p "80:80@loadbalancer" `
  -p "443:443@loadbalancer"
```

확인 명령어는 다음과 같다.

```powershell
kubectl cluster-info
```

이번 작업에서는 k3d 클러스터 생성과 80/443 포트 매핑을 진행한 뒤,
nginx를 배포하여 localhost에서 웹 서버 응답이 정상적으로 보이는 것까지 확인했다.

다만 이번 글에서는 nginx를 예시 서비스로 사용했으며,
실제 프로젝트 애플리케이션 배포와 상세한 Ingress 구성은 다음 단계에서 다룰 예정이다.