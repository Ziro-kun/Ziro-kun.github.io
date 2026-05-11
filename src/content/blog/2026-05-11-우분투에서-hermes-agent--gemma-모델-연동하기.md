---
title: "우분투에서 Hermes Agent + Gemma 모델 연동하기"
description: "Ollama를 통해 로컬에서 Gemma 모델을 실행하고 Hermes Agent와 연결하는 완벽한 가이드"
pubDate: "2026-05-11"
tags: ["AI", "LLM", "Ollama", "Gemma", "Ubuntu"]
category: "explore"
heroImage: "https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 19-27-33.png"
---

# 0. 서론

얼마 전 Gemini와 대화하면서 흥미로운 주제가 나왔습니다. 로컬 우분투 환경에서 Hermes Agent와 Gemma 모델을 어떻게 연동할 수 있을까 하는 거였어요.

> "Gemma 모델 파일만 있으면 되지 않을까?"

그렇게 단순하지 않더라고요. Gemini의 설명을 받으며 알게 된 건, **모델 파일만으로는 부족하고, 추론 엔진(Inference Engine)이 필수**라는 겁니다. 이 글에서는 그 과정을 차근차근 정리해봤습니다.

---

# 1. 왜 Ollama인가?

## 추론 엔진이 필요한 이유

Gemma 같은 LLM 모델 파일(`.gguf` 또는 `.safetensors`)은 **가중치 데이터일 뿐**입니다. 실제로 추론을 돌리려면:

- 모델을 메모리에 로드
- GPU/CPU에서 연산 수행
- API 서버로 노출

이 모든 걸 담당하는 게 추론 엔진입니다.

주요 선택지:

| 엔진 | 특징 | 추천 대상 |
|------|------|---------|
| **Ollama** | 모델 다운로드 + 실행 + API 제공 (원클릭) | 초심자, 빠른 시작 |
| **vLLM** | 고성능, 배치 처리 최적화 | 프로덕션, 고성능 필요 |
| **LM Studio** | GUI 기반 | GUI 선호자 |

저는 **Ollama**를 강력 추천합니다. 설치부터 실행까지 정말 간단하거든요.

---

# 2. 단계별 설정 가이드

## Step 1: Ollama 설치 및 Gemma 실행

### 설치하기

```bash
# 우분투에서 Ollama 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 서비스 시작
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Gemma 모델 다운로드 및 실행

```bash
# Gemma 모델 실행 (자동으로 다운로드)
ollama run gemma2

# 또는 특정 크기 지정
ollama run gemma2:7b
ollama run gemma2:9b
ollama run gemma2:27b
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-09 23-11-22.png" alt="Ollama 실행 화면" style="width:100%;max-width:800px;" />
~~_이 화면이 나오면 성공입니다_~~

첫 실행 시 모델 파일을 다운로드하는데, 인터넷 속도에 따라 5~30분 정도 걸립니다.

> "잠깐, 내 GPU 메모리가 충분한가?"

Gemma 모델별 요구 사양:

| 모델 | 최소 VRAM | 권장 VRAM |
|------|---------|---------|
| gemma2:2b | 2GB | 4GB |
| gemma2:7b | 4GB | 8GB |
| gemma2:9b | 6GB | 12GB |
| gemma2:27b | 16GB | 24GB |

메모리가 부족하면 CPU로 자동 전환되는데, 속도가 **엄청 느립니다** (?)

### 정상 작동 확인

```bash
# 다른 터미널에서 API 테스트
curl http://localhost:11434/api/generate -d '{
  "model": "gemma2",
  "prompt": "Hello, how are you?"
}'
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-10 00-53-21.png" alt="Ollama API 응답" style="width:100%;max-width:800px;" />
~~_JSON 응답이 스트리밍으로 들어옵니다_~~

---

## Step 2: Hermes Agent 설치

Hermes Agent는 LLM 기반의 자율 에이전트 프레임워크입니다.

```bash
# pip로 설치
pip install hermes-agent

# 또는 GitHub에서 클론
git clone https://github.com/hermes-agent/hermes-agent.git
cd hermes-agent
pip install -e .
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-10 01-16-51.png" alt="Hermes Agent 설치" style="width:100%;max-width:800px;" />

---

## Step 3: Hermes를 Gemma와 연동

### 설정 파일 생성

Hermes 프로젝트 디렉토리에서:

```bash
hermes setup
```

대화형 설정이 시작됩니다:

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 07-36-53.png" alt="hermes setup 실행" style="width:100%;max-width:800px;" />

### 설정 내용

프롬프트에 다음과 같이 입력합니다:

**1. LLM Provider 선택**

```
? Which LLM provider would you like to use?
> Custom / Local (Ollama)
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-44.png" alt="LLM Provider 선택" style="width:100%;max-width:800px;" />

**2. API 엔드포인트**

```
? What is your Ollama API endpoint?
> http://localhost:11434
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-50.png" alt="API 엔드포인트 입력" style="width:100%;max-width:800px;" />

**3. 모델 이름**

```
? What model name should Hermes use?
> gemma2
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-58.png" alt="모델 이름 입력" style="width:100%;max-width:800px;" />

생성된 설정 파일(`config.yaml` 또는 `.env`)을 확인합니다:

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-23-32.png" alt="config.yaml 확인" style="width:100%;max-width:800px;" />

---

## Step 4: 간단한 테스트 스크립트

```python
from hermes_agent import Agent

# 에이전트 초기화
agent = Agent(model="gemma2", provider="local")

# 질문 던지기
response = agent.run("우분투에서 파이썬 가상환경을 만드는 방법을 알려줘")
print(response)
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-31-18.png" alt="테스트 스크립트 실행" style="width:100%;max-width:800px;" />
~~_로컬 모델이 답변을 생성합니다_~~

---

# 3. 주의사항 & 트러블슈팅

## GPU 메모리 부족

**증상:** Ollama가 CPU 모드로 자동 전환, 응답이 1분 이상 걸림

**해결책:**
- 더 작은 모델 사용: `gemma2:2b` 또는 `gemma2:7b`
- 다른 GPU 프로세스 종료: `nvidia-smi`로 확인 후 종료
- VRAM 늘리기: 거의 불가능하면 클라우드 GPU 고려

```bash
# GPU 메모리 확인
nvidia-smi

# Ollama 메모리 사용량 확인
ollama list
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-31-52.png" alt="GPU 메모리 확인" style="width:100%;max-width:800px;" />

## 포트 충돌 (Port 11434 already in use)

**해결책:**

```bash
# 기존 Ollama 프로세스 종료
sudo systemctl stop ollama

# 또는 포트 변경
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

## Hermes 연결 실패

**증상:** `ConnectionError: Failed to connect to http://localhost:11434`

**확인사항:**

```bash
# 1. Ollama 서비스 상태 확인
sudo systemctl status ollama

# 2. 포트 열려있는지 확인
netstat -tuln | grep 11434

# 3. 수동으로 재시작
sudo systemctl restart ollama
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-41-37.png" alt="systemctl 상태 확인" style="width:100%;max-width:800px;" />

## 권한 문제 (Permission denied)

```bash
# Ollama 그룹에 사용자 추가
sudo usermod -aG ollama $USER

# 변경사항 적용 (로그아웃 후 재로그인, 또는)
newgrp ollama
```

---

# 4. 성능 최적화 팁

## 모델 선택 기준

하드웨어 사양별 추천:

| 사양 | 추천 모델 | 특징 |
|------|---------|------|
| 2GB VRAM | gemma2:2b | 가볍지만 품질 낮음 |
| 4-8GB VRAM | gemma2:7b | **가성비 최고** |
| 12GB+ VRAM | gemma2:9b | 고품질 응답 |
| 24GB+ VRAM | gemma2:27b | 최고 성능 |

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-53-17.png" alt="모델 성능 비교" style="width:100%;max-width:800px;" />

## 응답 속도 향상

```bash
# 1. Ollama 캐시 활성화 (설정 파일에 추가)
OLLAMA_CACHE=true

# 2. 배치 크기 조정
OLLAMA_BATCH_SIZE=256

# 3. 스레드 수 최적화
OLLAMA_NUM_THREAD=8
```

---

# 5. 다음 단계

이제 기본 설정이 완료되었습니다. 다음으로 할 수 있는 것들:

* **RAG(Retrieval-Augmented Generation)** 추가 — 외부 데이터와 연결
* **Tool/Plugin** 개발 — 에이전트가 외부 API 호출
* **Fine-tuning** — 특정 도메인에 맞게 모델 조정
* **멀티 에이전트** — 여러 에이전트 간 협업

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-57-51.png" alt="다음 단계" style="width:100%;max-width:800px;" />

---

# 6. 마무리

처음엔 단순하게 생각했어요. 모델 파일만 있으면 되겠지 하고요. 하지만 Gemini와의 대화를 통해 깨달았습니다.

> "LLM은 엔진이 있어야 돈다"

Ollama는 정말 잘 만들어진 도구입니다. 복잡한 설정 없이도 로컬 환경에서 최신 LLM을 돌릴 수 있게 해줍니다. 그리고 Hermes Agent와의 조합이면, 자신만의 AI 에이전트를 만들 수 있어요.

<img src="https://raw.githubusercontent.com/Ziro-kun