---
title: "자격증 도전기 - AWS Certified Cloud Practitioner 1️⃣"
description: "AI 미생의 IT 자격증 도전기입니다."
pubDate: "2025-12-23"
tags: ["aws", "certification", "cloud", "자격증", "클라우드"]
category: "growth"
---

작년 1월에 ADsP를 60점(커트라인)이라는 아주 경제적인(?) 점수로 취득하고 7월에 정처기를 과락으로 말아먹은 뒤 간만에 자격증에 도전하였습니다. 비교적 취득하기 쉽고 현업에서 많이 써먹는다는 강사님의 말씀에 몹쓸병이 도졌습니다. 

동기들 대상으로 파티원을 모아서 1달 속성으로 공부하고 2월에 시험을 치를 예정입니다. 간만에 스터디그룹 운영을 하려니 내향인은 또 걱정이 많습니다. 제가 많이 알아야 파티를 이끌고 갈 수 있으니 일단 저부터 공부를 해봅니다.

---

# 1. 학습자료

일단 스터디그룹 운영을 위해 저의 친애하는 동반자 ChatGPT에게 같이 고민해달라고 했더니, 종이책이든 e북이든 교재는 따로 필요 없고, 강의를 하나 추천해줍니다.

```
5. 참고 교재·강의 (과하지 않게)
▣ 강의 (1개만 선택 권장)
Stephane Maarek – AWS Cloud Practitioner (Udemy)
Practitioner 최적화 강의
실무 설명 + 시험 포인트 명확

▣ 교재
별도 종이책 ❌ (비추천)
대신:
AWS 공식 Exam Guide
서비스별 비교 표 직접 제작 (스터디 산출물로 좋음)
```

그래서 추천해주는 강의를 찾아봤습니다.

![](https://velog.velcdn.com/images/applez/post/ef8b33e9-dae3-4ba2-837f-8ff8c77de30a/image.png)

지금은 구매해서 저렇게 나오는데, 14시간짜리 강의가 단돈 ₩15,000입니다. 이정도면 살만하다 해서 구매하고 장장 500장짜리 강의 슬라이드도 받았습니다. 문제는 죄다 영어입니다. 강의는 한글자막을 지원하는데 슬라이드는... 그래서 똑똑한 생성형AI들의 힘을 빌리기로 했습니다.

아래는 Google NotebookLM에게 부탁하여 강의 슬라이드를 소스로 핵심 용어를 카테고리별로 정리한 용어집입니다.

---

### **1. 클라우드 기본 개념 및 모델**
*   **클라우드 컴퓨팅 (Cloud Computing)**: IT 리소스를 인터넷을 통해 온디맨드로 제공하며, **사용량 기반 요금(Pay-as-you-go)**으로 비용을 지불하는 모델입니다.
*   **IaaS (Infrastructure as a Service)**: 네트워킹, 컴퓨터, 데이터 스토리지 등의 **기초적인 빌딩 블록**을 제공하며 가장 높은 유연성을 가집니다.
*   **PaaS (Platform as a Service)**: 하드웨어나 운영 체제 관리의 부담을 줄이고 애플리케이션의 **배포와 관리**에만 집중할 수 있게 합니다.
*   **SaaS (Software as a Service)**: 서비스 제공업체에 의해 완전히 관리되는 **완성된 제품**을 의미합니다.
*   **탄력성 (Elasticity)**: 수요 변화에 따라 리소스를 **자동으로 확장하거나 축소**하여 성능과 비용을 최적화하는 시스템의 능력입니다.

### **2. AWS 글로벌 인프라**
*   **리전 (Region)**: 전 세계에 물리적으로 분리되어 있는 **데이터 센터의 클러스터**입니다.
*   **가용 영역 (Availability Zone, AZ)**: 하나의 리전 내에서 물리적으로 격리되어 있는 **하나 이상의 데이터 센터 모음**입니다.
*   **엣지 로케이션 (Edge Location)**: 사용자에게 더 낮은 지연 시간으로 콘텐츠를 전달하기 위해 데이터를 **캐싱**하는 거점 지점입니다.

### **3. 보안 및 자격 증명 관리**
*   **공동 책임 모델 (Shared Responsibility Model)**: AWS는 **'클라우드 자체의 보안'**을 책임지고, 고객은 **'클라우드 내부의 보안'**(데이터, 구성 등)을 책임지는 구조입니다.
*   **IAM (Identity & Access Management)**: AWS 리소스에 대한 접근을 **안전하게 제어**하는 중앙 서비스입니다.
*   **MFA (Multi-Factor Authentication)**: 보안 강화를 위해 암호 외에 **추가적인 인증 장치**를 요구하는 기술입니다.
*   **KMS (Key Management Service)**: 데이터 암호화에 사용되는 **암호화 키**를 생성하고 관리하는 서비스입니다.

### **4. 핵심 컴퓨팅 및 네트워크 서비스**
*   **Amazon EC2 (Elastic Compute Cloud)**: 클라우드에서 빌려 쓰는 **가상 서버** 인스턴스입니다.
*   **AWS Lambda**: 서버를 관리할 필요 없이 코드를 실행하고 실행 시간에 대해서만 비용을 지불하는 **서버리스 컴퓨팅** 서비스입니다.
*   **Amazon VPC (Virtual Private Cloud)**: AWS 계정 전용의 **가상 네트워크 환경**을 논리적으로 격리하여 구축하는 서비스입니다.
*   **Amazon Route 53**: 가용성과 확장성이 뛰어난 클라우드 **DNS(도메인 네임 시스템)** 서비스입니다.

### **5. 스토리지 및 데이터베이스 서비스**
*   **Amazon S3 (Simple Storage Service)**: 데이터를 객체 형태로 저장하는 **무제한 확장 가능한 객체 스토리지**입니다.
*   **Amazon EBS (Elastic Block Store)**: EC2 인스턴스에서 사용할 수 있는 **고성능 블록 스토리지** 볼륨(네트워크 드라이브)입니다.
*   **Amazon RDS (Relational Database Service)**: SQL을 사용하는 **관계형 데이터베이스**를 클라우드에서 쉽게 운영할 수 있게 돕는 관리형 서비스입니다.
*   **Amazon DynamoDB**: 어떤 규모에서도 일관된 성능을 제공하는 완전 관리형 **NoSQL 데이터베이스**입니다.

### **6. 관리, 비용 및 지원 플랜**
*   **AWS Organizations**: 여러 AWS 계정을 중앙에서 **통합 관리 및 결제**할 수 있는 서비스입니다.
*   **AWS Cost Explorer**: 비용 및 사용량 데이터를 시각화하여 확인하고 **미래 비용을 예측**하는 도구입니다.
*   **Well-Architected Framework**: 운영 우수성, 보안, 안정성, 성능 효율성, 비용 최적화, 지속 가능성이라는 **6가지 핵심 요소**를 기반으로 한 설계 원칙입니다.

---

# 2. 스터디 계획
일단 그룹을 4~5인으로 구성해서 주 2회 이론부터 발제-발표하는 방식으로 진행하고 마지막 2타임은 문제풀이에 집중하기로 했습니다. ChatGPT가 커리큘럼도 이렇게 짜주더군요. 참 좋은 친구입니다.
```
3. 주차별 커리큘럼 (Practitioner 표준)
▣ 1주차: 클라우드 기초 + 글로벌 인프라

Cloud 개념 (IaaS / PaaS / SaaS)
AWS 글로벌 인프라
Region / AZ / Edge Location
Shared Responsibility Model ⭐️(시험 핵심)

▣ 2주차: 컴퓨팅 & 스토리지

EC2 (On-Demand / Reserved / Spot)
Lambda (서버리스 개념)
Storage
S3 (Standard / IA / Glacier)
EBS vs EFS vs S3 구분 ⭐️

▣ 3주차: 네트워크 & 데이터베이스

VPC 기초 (Public / Private Subnet)
ELB, Auto Scaling 개념
RDS / DynamoDB / Aurora 차이 ⭐️

▣ 4주차: 보안·요금·운영

IAM (User / Group / Role / Policy) ⭐️⭐️
보안 책임 구분
과금 구조
Pay-as-you-go
Cost Explorer / Budgets
Well-Architected Framework 개요
```
문제를 풀려면 개념을 어느 정도는 익혀야 하기에, '나도 공부하면서 남도 알기쉽게 설명해주기'를 목표로 파티원들과 함께 이론부터 조질 생각입니다. 

참고로 Google NotebookLM을 활용하여 소스 기반 마인드맵을 그려봤는데, LLM에 상관없이 파트 분류는 거의 비슷하게 나옵니다.
![](https://velog.velcdn.com/images/applez/post/53647d92-5845-4d36-9d3d-70487a2a2ab4/image.png)


---
# 3. 문제 소스
대부분 먼저 공부하신 분들의 후기를 보니, 문제풀이를 많이 했다고 하셔서 ChatGPT에게 문제 소스도 같이 추천해달라고 했습니다. 
```
4. 문제 소스 추천 (검증된 것 위주)
▣ 1순위 (공식)

AWS Skill Builder – Cloud Practitioner Essentials
AWS 공식
실제 시험 문항 톤과 가장 유사
무료/유료 혼합

▣ 2순위 (실전 대비)

Udemy Cloud Practitioner Practice Tests
문제 수 많음
오답 해설이 중요한 기준

▣ 3순위 (개념 점검용)

ExamTopics (주의해서 사용)
실제 시험 유사 문항 많음
❗️정답 논쟁 있음 → 토론용으로만 활용 권장
```
이 외에도 아마 공개된 부분들이 많을 것 같아서, 천천히 찾아볼 예정입니다. 1월 중순에 1회 기사 시험도 있어서 정처기 도전도 다시 해야하는데 과연 두 마리 토끼를 다 잡을 수 있을지 걱정이 앞섭니다. 