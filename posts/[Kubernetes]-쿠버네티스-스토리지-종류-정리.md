---
title: "[Kubernetes] 쿠버네티스 스토리지 종류 정리"
source: ""
published: "2026-05-29T18:01:00.000Z"
---

쿠버네티스에서 스토리지를 공부하면 처음에는 `Volume`, `PV`, `PVC`, `StorageClass` 같은 개념이 나오고, 그 안에서 또 `hostPath`, `emptyDir`, `NFS`, `iSCSI`, `AWS EBS`, `Azure Disk`, `GCE PD` 같은 이름들이 나온다.

처음 보면 너무 많아서 헷갈린다.

그래서 먼저 이렇게 나눠서 보면 좋다.

```text
Kubernetes Storage 종류

1. 임시 저장소
   - emptyDir

2. 노드 로컬 저장소
   - hostPath
   - local

3. 네트워크 공유 저장소
   - NFS
   - iSCSI
   - FC

4. 클라우드 블록 스토리지
   - AWS EBS
   - GCE Persistent Disk
   - Azure Disk
   - Cinder

5. 쿠버네티스 추상화 리소스
   - PersistentVolume
   - PersistentVolumeClaim
   - StorageClass
```

이번 글에서는 스토리지 종류 중심으로 정리한다.

---

## 1. emptyDir

`emptyDir`은 Pod가 생성될 때 같이 만들어지는 임시 저장소다.

Pod가 살아있는 동안에는 유지되지만, Pod가 삭제되면 같이 사라진다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo hello > /data/hello.txt && sleep 3600"]
      volumeMounts:
        - name: temp-storage
          mountPath: /data
  volumes:
    - name: temp-storage
      emptyDir: {}
```

구조는 이렇다.

```text
Pod
 ├── Container
 │    └── /data
 │
 └── emptyDir Volume
```

`emptyDir`은 이런 경우에 쓴다.

```text
임시 파일 저장
컨테이너 간 파일 공유
로그 임시 저장
캐시 데이터 저장
```

예를 들어 하나의 Pod 안에 app 컨테이너와 sidecar 컨테이너가 있을 때, app이 로그를 쓰고 sidecar가 그 로그를 읽는 구조에 사용할 수 있다.

```text
app container
  → /logs/app.log에 로그 작성

sidecar container
  → /logs/app.log 읽어서 외부로 전송

두 컨테이너가 같은 emptyDir 공유
```

단점은 명확하다.

```text
Pod가 삭제되면 데이터도 삭제됨
영구 데이터 저장용으로 부적합
DB 데이터 저장하면 안 됨
```

한 줄로 정리하면 이렇다.

> emptyDir은 Pod 생명주기와 함께하는 임시 저장소다.

---

## 2. hostPath

`hostPath`는 Pod가 실행되는 Node의 실제 파일이나 디렉터리를 Pod 안에 마운트하는 방식이다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-pod
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - name: html
          mountPath: /usr/share/nginx/html
  volumes:
    - name: html
      hostPath:
        path: /hostdir_or_file
```

이 구조는 이렇게 보면 된다.

```text
Node
 └── /hostdir_or_file
        ↑
     hostPath
        ↑
Pod
 └── Container
      └── /usr/share/nginx/html
```

컨테이너 입장에서는 `/usr/share/nginx/html`에 접근하지만, 실제 데이터는 Node의 `/hostdir_or_file`에 있다.

장점은 단순하다.

```text
설정이 쉬움
Node의 실제 파일을 바로 확인 가능
실습하기 좋음
시스템 파일 접근이 필요한 특수 Pod에서 사용 가능
```

하지만 운영에서는 조심해야 한다.

```text
Pod가 특정 Node에 의존함
Pod가 다른 Node로 이동하면 데이터가 없음
Node 파일시스템을 직접 건드려 보안 위험이 있음
여러 Node 간 데이터 공유가 어려움
```

예를 들어 Pod가 Node1에서 실행될 때는 데이터가 있다.

```text
Node1
 └── /data/index.html 있음
```

그런데 장애로 Pod가 Node2로 옮겨가면?

```text
Node2
 └── /data/index.html 없음
```

그래서 hostPath는 보통 실습, 테스트, 데몬셋, 노드 로그 수집 같은 특수한 경우에 사용한다.

> hostPath는 Node의 로컬 경로를 Pod에 직접 붙이는 방식이다.

---

## 3. local Volume

`local` Volume은 특정 Node의 로컬 디스크를 사용하는 방식이다.

hostPath와 비슷하게 Node 로컬 저장소를 쓰지만, PersistentVolume과 함께 사용해서 쿠버네티스가 어느 정도 스케줄링을 인식할 수 있게 만든다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
                - worker-node-1
```

핵심은 `nodeAffinity`다.

```text
이 PV는 worker-node-1에 있는 로컬 디스크다
그러니까 이 PV를 쓰는 Pod도 worker-node-1에 떠야 한다
```

장점은 성능이다.

```text
네트워크 스토리지보다 빠를 수 있음
로컬 SSD 사용 가능
지연시간이 낮음
```

단점은 가용성이다.

```text
해당 Node가 죽으면 접근 불가
다른 Node로 쉽게 이동 불가
데이터 복제는 별도로 고려해야 함
```

> local Volume은 성능은 좋지만 Node 장애에 약한 로컬 영구 저장소다.

---

## 4. NFS

`NFS`는 Network File System이다.

여러 서버가 네트워크를 통해 하나의 파일시스템을 공유할 수 있게 해준다.

쿠버네티스에서는 여러 Pod가 같은 저장소를 공유해야 할 때 자주 나온다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nfs-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: nfs-volume
          mountPath: /usr/share/nginx/html
  volumes:
    - name: nfs-volume
      nfs:
        server: 192.168.0.10
        path: /exports/data
```

구조는 이렇다.

```text
NFS Server
 └── /exports/data
        ↑
      Network
        ↑
Pod A  Pod B  Pod C
```

NFS의 장점은 공유다.

```text
여러 Pod가 같은 파일 접근 가능
여러 Node에서 접근 가능
ReadWriteMany 지원 가능
온프레미스 환경에서 많이 사용
```

여기서 `ReadWriteMany`는 여러 Pod가 동시에 읽고 쓸 수 있는 접근 모드다.

```text
ReadWriteMany
→ 여러 Node의 여러 Pod가 동시에 마운트 가능
```

단점도 있다.

```text
NFS 서버가 장애 지점이 될 수 있음
네트워크 성능에 영향 받음
동시 쓰기 성능 문제 가능
권한 설정이 까다로울 수 있음
```

> NFS는 여러 Pod가 같은 파일 저장소를 공유할 때 유용한 네트워크 파일 스토리지다.

---

## 5. iSCSI

`iSCSI`는 네트워크를 통해 블록 스토리지를 연결하는 방식이다.

NFS가 파일 단위 공유에 가깝다면, iSCSI는 원격 디스크를 로컬 디스크처럼 붙이는 느낌에 가깝다.

```text
NFS
→ 네트워크 파일시스템

iSCSI
→ 네트워크로 연결하는 블록 디스크
```

구조는 대략 이렇다.

```text
iSCSI Target
   ↓
Network
   ↓
Node
   ↓
Pod에 Volume으로 제공
```

장점은 이렇다.

```text
블록 스토리지 제공
DB 같은 워크로드에 사용 가능
온프레미스 스토리지 환경에서 활용 가능
```

단점은 이렇다.

```text
설정이 복잡함
스토리지 네트워크 구성이 필요함
운영 난이도가 NFS보다 높을 수 있음
동시 다중 쓰기에 주의 필요
```

> iSCSI는 네트워크를 통해 원격 블록 디스크를 붙이는 방식이다.

---

## 6. FC

`FC`는 Fibre Channel이다.

주로 기업용 스토리지 환경에서 사용하는 고성능 스토리지 연결 방식이다.

```text
서버
  ↓
Fibre Channel 네트워크
  ↓
SAN Storage
```

장점은 안정성과 성능이다.

```text
고성능
낮은 지연시간
기업용 SAN 환경에서 사용
```

단점은 비용과 복잡도다.

```text
전용 장비 필요
구성이 복잡함
클라우드·일반 실습 환경에서는 보기 어려움
```

> FC는 기업용 SAN 환경에서 쓰는 고성능 블록 스토리지 연결 방식이다.

---

## 7. AWS EBS

`AWS EBS`는 AWS의 블록 스토리지다.

EC2에 디스크를 붙이듯이, Kubernetes에서는 Pod가 사용할 PersistentVolume으로 붙일 수 있다.

```text
AWS EBS Volume
        ↓
Node에 attach
        ↓
Pod에 mount
```

과거에는 YAML에 `awsElasticBlockStore`를 직접 쓰기도 했지만, 요즘은 보통 CSI Driver와 StorageClass를 통해 동적으로 생성한다.

EBS의 특징은 이렇다.

```text
블록 스토리지
AWS 환경에서 사용
보통 하나의 Node에 attach
ReadWriteOnce 방식으로 많이 사용
DB 저장소로 사용 가능
```

주의할 점은 EBS가 기본적으로 특정 Availability Zone에 속한다는 것이다.

```text
EBS가 ap-northeast-2a에 있음
Pod가 ap-northeast-2c Node에 뜸
→ attach 불가
```

그래서 EKS에서는 StorageClass, topology, scheduler 동작을 같이 이해해야 한다.

> AWS EBS는 AWS에서 Pod에 붙이는 대표적인 클라우드 블록 스토리지다.

---

## 8. GCE Persistent Disk

`GCE PD`는 Google Cloud의 Persistent Disk다.

AWS EBS와 비슷한 위치에 있는 GCP의 블록 스토리지다.

```text
GCE Persistent Disk
        ↓
GKE Node에 attach
        ↓
Pod에 mount
```

특징은 이렇다.

```text
GCP 환경에서 사용
블록 스토리지
PersistentVolume으로 사용 가능
ReadWriteOnce 중심
StorageClass로 동적 프로비저닝 가능
```

> GCE Persistent Disk는 GCP에서 사용하는 대표적인 쿠버네티스 블록 스토리지다.

---

## 9. Azure Disk

`Azure Disk`는 Microsoft Azure의 블록 스토리지다.

AKS에서 PersistentVolume으로 많이 사용된다.

```text
Azure Disk
      ↓
AKS Node에 attach
      ↓
Pod에 mount
```

특징은 이렇다.

```text
Azure 환경에서 사용
블록 스토리지
ReadWriteOnce 중심
DB나 상태 저장 애플리케이션에 사용 가능
StorageClass로 동적 생성 가능
```

> Azure Disk는 Azure에서 Pod에 붙이는 클라우드 블록 스토리지다.

---

## 10. Cinder

`Cinder`는 OpenStack의 블록 스토리지 서비스다.

OpenStack 기반 클라우드에서 Kubernetes를 운영할 때 사용할 수 있다.

```text
OpenStack Cinder Volume
          ↓
Node에 attach
          ↓
Pod에 mount
```

특징은 이렇다.

```text
OpenStack 환경에서 사용
블록 스토리지
PersistentVolume으로 사용 가능
프라이빗 클라우드 환경에서 등장
```

> Cinder는 OpenStack 환경의 블록 스토리지를 쿠버네티스에 연결할 때 사용한다.

---

## 11. ConfigMap Volume

스토리지라고 하면 디스크만 떠올리기 쉬운데, 쿠버네티스에서는 ConfigMap도 Volume처럼 마운트할 수 있다.

ConfigMap은 설정값을 저장하는 리소스다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  index.html: |
    hello configmap volume
```

Pod에 Volume으로 붙일 수 있다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-volume-pod
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - name: config-volume
          mountPath: /usr/share/nginx/html
  volumes:
    - name: config-volume
      configMap:
        name: nginx-config
```

이렇게 하면 ConfigMap의 데이터가 파일처럼 보인다.

```text
ConfigMap
  index.html
      ↓
Pod 안의 /usr/share/nginx/html/index.html
```

> ConfigMap Volume은 설정 파일을 컨테이너 안에 파일 형태로 넣을 때 사용한다.

---

## 12. Secret Volume

Secret도 Volume으로 마운트할 수 있다.

비밀번호, 토큰, 인증서 같은 값을 파일로 컨테이너에 전달할 때 쓴다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  password: mypassword
```

Pod에서 Secret을 Volume으로 마운트한다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "cat /etc/secret/password && sleep 3600"]
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secret
  volumes:
    - name: secret-volume
      secret:
        secretName: app-secret
```

구조는 이렇다.

```text
Secret
  password
      ↓
Pod 안의 /etc/secret/password
```

주의할 점은 Secret이 base64로 보인다고 안전한 게 아니라는 것이다.

Secret 조회 권한이 있으면 디코딩해서 볼 수 있다.

> Secret Volume은 민감정보를 컨테이너 안에 파일로 전달할 때 사용한다.

---

## 13. PersistentVolume, PVC, StorageClass

스토리지 종류를 볼 때 마지막으로 꼭 알아야 하는 게 쿠버네티스의 추상화 리소스다.

### PersistentVolume

`PersistentVolume`, 줄여서 `PV`는 클러스터에 준비된 실제 저장소다.

```text
PV
→ 관리자가 준비한 저장공간
→ 또는 StorageClass가 동적으로 만든 저장공간
```

예를 들어 NFS, EBS, Azure Disk 같은 실제 저장소가 PV로 표현된다.

### PersistentVolumeClaim

`PersistentVolumeClaim`, 줄여서 `PVC`는 Pod가 스토리지를 요청하는 문서다.

```text
PVC
→ Pod가 "나 10Gi 저장소 필요해"라고 요청하는 것
```

Pod는 보통 실제 PV를 직접 고르지 않는다. PVC를 참조한다.

```text
Pod
  ↓
PVC 요청
  ↓
PV 연결
  ↓
실제 스토리지 사용
```

### StorageClass

`StorageClass`는 스토리지를 자동으로 만들기 위한 템플릿이다.

```text
StorageClass
→ 어떤 종류의 스토리지를 어떤 방식으로 만들지 정의
```

예를 들어 EKS에서는 EBS를 자동으로 만들고, AKS에서는 Azure Disk를 자동으로 만들고, GKE에서는 GCE PD를 자동으로 만들 수 있다.

전체 흐름은 이렇다.

```text
Pod
  ↓
PVC
  ↓
StorageClass
  ↓
실제 클라우드 디스크 자동 생성
  ↓
PV 생성
  ↓
Pod에 mount
```

---

## 14. Access Mode도 같이 봐야 한다

스토리지를 고를 때는 접근 방식도 중요하다.

대표적인 Access Mode는 세 가지다.

```text
ReadWriteOnce, RWO
→ 하나의 Node에서 읽기/쓰기 가능

ReadOnlyMany, ROX
→ 여러 Node에서 읽기 전용 가능

ReadWriteMany, RWX
→ 여러 Node에서 읽기/쓰기 가능
```

간단히 보면 이렇다.

| Access Mode | 의미              | 예시                      |
| ----------- | --------------- | ----------------------- |
| RWO         | 한 Node에서 읽기/쓰기  | EBS, Azure Disk, GCE PD |
| ROX         | 여러 Node에서 읽기 전용 | 일부 네트워크 스토리지            |
| RWX         | 여러 Node에서 읽기/쓰기 | NFS                     |

특히 여러 Pod가 같은 저장소를 동시에 써야 하면 `RWX` 지원 여부를 봐야 한다.

```text
여러 Pod가 같은 파일을 읽고 써야 함
→ NFS 같은 RWX 지원 스토리지 고려
```

반대로 DB처럼 하나의 Pod가 전용 디스크를 쓰는 구조라면 `RWO`가 일반적이다.

```text
MySQL Pod
→ PVC
→ EBS
→ RWO
```

---

## 15. 스토리지 종류 한 번에 비교

| 종류               | 성격                | 유지 기간        | 공유 가능성              | 주 사용처                   |
| ---------------- | ----------------- | ------------ | ------------------- | ----------------------- |
| emptyDir         | 임시 저장소            | Pod 삭제 시 삭제  | 같은 Pod 내부 컨테이너끼리 공유 | 임시파일, 캐시, 로그 전달         |
| hostPath         | Node 로컬 경로        | Node에 남음     | 특정 Node 중심          | 실습, 노드 로그, 시스템 Pod      |
| local            | Node 로컬 디스크       | Node에 남음     | 특정 Node 중심          | 고성능 로컬 저장소              |
| NFS              | 네트워크 파일 스토리지      | 외부 서버에 유지    | 여러 Pod 공유 가능        | 공유 파일, RWX              |
| iSCSI            | 네트워크 블록 스토리지      | 외부 스토리지에 유지  | 보통 단일 attach 중심     | DB, 블록 스토리지             |
| FC               | SAN 블록 스토리지       | 외부 스토리지에 유지  | 기업 환경 구성에 따라 다름     | 고성능 기업용 스토리지            |
| AWS EBS          | 클라우드 블록 스토리지      | EBS에 유지      | 보통 RWO              | EKS, DB 저장소             |
| GCE PD           | 클라우드 블록 스토리지      | PD에 유지       | 보통 RWO              | GKE, DB 저장소             |
| Azure Disk       | 클라우드 블록 스토리지      | Disk에 유지     | 보통 RWO              | AKS, DB 저장소             |
| Cinder           | OpenStack 블록 스토리지 | Cinder에 유지   | 보통 RWO              | OpenStack 기반 Kubernetes |
| ConfigMap Volume | 설정 파일             | ConfigMap 기준 | 여러 Pod에서 참조 가능      | 설정 파일 주입                |
| Secret Volume    | 민감정보 파일           | Secret 기준    | 여러 Pod에서 참조 가능      | 인증서, 토큰, 비밀번호           |

---

## 16. 어떤 상황에 뭘 쓰면 될까?

상황별로 보면 더 쉽다.

```text
Pod 안에서 잠깐 쓸 임시 공간이 필요하다
→ emptyDir

컨테이너 여러 개가 같은 Pod 안에서 파일을 공유해야 한다
→ emptyDir

Node의 특정 파일이나 로그를 Pod에서 읽어야 한다
→ hostPath

실습에서 Node 디렉터리를 Pod에 붙여보고 싶다
→ hostPath

여러 Pod가 같은 파일 저장소를 공유해야 한다
→ NFS

DB처럼 영구 디스크가 필요하다
→ EBS, GCE PD, Azure Disk, Cinder, iSCSI

클라우드에서 PVC 만들면 자동으로 디스크가 생기게 하고 싶다
→ StorageClass

설정 파일을 컨테이너에 넣고 싶다
→ ConfigMap Volume

비밀번호나 인증서를 파일로 넣고 싶다
→ Secret Volume
```

---

## 17. 정리

쿠버네티스 스토리지는 단순히 “파일 저장”이 아니라, Pod가 데이터를 어디에 저장하고 어떻게 유지할지를 정하는 개념이다.

종류별 핵심은 이렇게 기억하면 된다.

```text
emptyDir
→ Pod 생명주기와 함께하는 임시 저장소

hostPath
→ Node의 실제 경로를 Pod에 붙이는 저장소

local
→ 특정 Node의 로컬 디스크를 PV로 사용하는 저장소

NFS
→ 여러 Pod가 공유할 수 있는 네트워크 파일 스토리지

iSCSI / FC
→ 네트워크 기반 블록 스토리지

EBS / GCE PD / Azure Disk / Cinder
→ 클라우드 또는 프라이빗 클라우드의 블록 스토리지

ConfigMap Volume
→ 설정값을 파일처럼 마운트

Secret Volume
→ 민감정보를 파일처럼 마운트

PV / PVC / StorageClass
→ 실제 스토리지를 쿠버네티스 방식으로 요청하고 연결하는 추상화
```

마지막으로 이렇게 정리하면 된다.

> 쿠버네티스 스토리지 종류는 “임시로 쓸 것인가, 노드 로컬을 쓸 것인가, 여러 Pod가 공유할 것인가, 클라우드 디스크를 쓸 것인가”를 기준으로 나누면 훨씬 덜 헷갈린다.
