---
title: "우분투에서 Hermes Agent + Gemma 모델 연동하기"
description: "모델 파일만으로는 부족하다 — Ollama와 Hermes Agent로 로컬 LLM 구동하기"
pubDate: "2026-04-14"
tags: ["LLM", "Gemma", "Ollama", "Hermes Agent", "우분투", "AI"]
category: "explore"
heroImage: ../../image/ hermes-agent.png
---

# 0. 들어가며

> Gemma 모델 파일만 있으면 되지 않을까?

처음엔 정말 그렇게 생각했습니다. 모델 파일을 받으면 바로 실행할 수 있을 거라고요. 우분투에서 Hermes Agent와 Gemma를 연동하려고 했을 때의 이야기입니다.

하지만 현실은 훨씬 더 복잡했습니다. 정전으로 세션이 몇 번 끊기고, 메모리 부족으로 모델이 죽고, 포트 충돌로 삽질하면서 깨달은 게 하나 있었거든요.

**"모델 파일만으로는 부족하다. 추론 엔진이 있어야 한다."**

Gemini와의 대화를 통해 정리한 이 여정을 여러분과 나누려고 합니다.

---

# 1. 추론 엔진이란 뭘까

## 모델 파일과 실행의 간극

`Gemma-2-27b.gguf` 같은 모델 파일을 손에 들고 있다고 해봅시다. 이건 뭘까요?

> 그냥 가중치 데이터일 뿐입니다.

모델 파일은 AI의 "뇌"지만, 실제로 생각하게 만드는 건 따로 있어야 해요. 바로:

- 모델을 GPU/CPU 메모리에 로드
- 입력값을 처리
- 계산을 실행  
- 결과를 반환

이 모든 걸 담당하는 게 **추론 엔진(Inference Engine)**입니다.

![깃애니멀 퀴즈 시스템](../../image/스크린샷 2026-03-09 23-11-22.png)
~~_추론 엔진이 없으면 이 정도 성능도 낼 수 없어요_~~

## 선택지들

우분투에서 쓸 수 있는 추론 엔진은 여러 개가 있습니다:

| 엔진 | 특징 | 추천 대상 |
|------|------|---------|
| **Ollama** | 모든 걸 자동으로 처리, 가장 간단 | 입문자, 빠른 구성 |
| **vLLM** | 높은 처리량, 성능 최적화 | 대규모 배포, 성능 중시 |
| **LM Studio** | GUI 제공, 매우 직관적 | GUI 선호자 |
| **Text Generation WebUI** | 기능 많음, 커스터마이징 가능 | 고급 사용자 |

저는 **Ollama**를 적극 추천합니다.

> Ollama는 "모델 다운로드 → 메모리 로드 → API 서버 생성"을 한 번에 처리해줍니다.

---

# 2. Ollama + Hermes Agent 설치하기

## Step 1: NVIDIA 드라이버 확인

GPU로 돌릴 거라면 NVIDIA 드라이버가 설치되어 있는지 먼저 확인하세요:

```bash
nvidia-smi
```

드라이버가 없다면:

```bash
sudo apt update && sudo apt install nvidia-driver-550
```

(2026년 기준, 550이 표준입니다)

## Step 2: Ollama 설치

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

이 명령어 하나로 모든 게 끝납니다. Ollama는 설치되면서 자동으로 systemd 서비스로 등록됩니다.

## Step 3: Gemma 모델 선택하기

Hermes Agent와 함께 쓸 Gemma를 고르는 게 중요합니다. 하드웨어 사양을 고려해서요:

```bash
# 가벼운 테스트용
ollama pull gemma2:2b

# 일반적인 추론 (권장)
ollama pull gemma4:26b

# 고성능 장비용
ollama pull gemma2:27b
```

제 경우엔 ZenBook(16GB RAM)이라서 Gemma 4 26B를 받으려다가 메모리 부족으로 삽질했습니다. ~~_나 같은 사람이 될 필요는 없어요_~~

## Step 4: Hermes Agent 설치

`pip install hermes-agent`는 안 됩니다. (저도 같은 에러를 만났어요)

공식 설치 스크립트를 사용하세요:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

설치 후 터미널을 재시작하거나:

```bash
source ~/.bashrc
```

## Step 5: Hermes Agent 설정

```bash
hermes setup
```

여기서 아래를 선택하면 됩니다:

- **Model Provider**: Custom endpoint (번호 24)
- **Base URL**: `http://localhost:11434/v1`
- **Model Name**: `gemma4:26b` (또는 당신이 받은 모델명)
- **API Key**: `ollama` (뭐든 상관없어요)
- **Context Length**: Enter (비워두세요)

---

# 3. 첫 실행 시 주의할 점들

## 포트 충돌 확인

만약 11434 포트가 이미 사용 중이라면?

```bash
netstat -tulpn | grep 11434
```

Docker 같은 다른 서비스가 쓰고 있을 수 있거든요.

## 메모리 부족 문제

가장 흔한 에러입니다:

```
❌ Error: HTTP 500: model requires more system memory 
           (18.3 GiB) than is available (14.1 GiB)
```

이러면 더 작은 모델을 선택하세요:

```bash
ollama pull gemma2:7b
```

또는 더 가벼운 퀀타이즈 버전:

```bash
ollama pull bartowski/gemma-4-26B-A4B-it-GGUF
```

## 정전 대비 (중요!)

우분투 서버에서 가장 무서운 게 정전입니다. 종료되면 Ollama가 자동으로 시작되지 않거든요.

```bash
systemctl status ollama
```

으로 확인하고, 재부팅 후에도 살아있는지 체크하세요. 필요하면 수동으로:

```bash
ollama serve
```

또는 더 안전하게 tmux 세션을 사용:

```bash
tmux new -s ollama
ollama serve
# Ctrl+B, D로 나가기
# 나중에 tmux attach -t ollama로 복구
```

---

# 4. 성능과 모델 선택

## 하드웨어별 추천 모델

| 노트북/장비 | VRAM | 추천 모델 |
|-----------|------|---------|
| 라이젠 노트북 (내장) | 8GB | Gemma 2 2B |
| ZenBook (내장, 16GB) | 10GB 정도 | Gemma 2 7B |
| RTX 3060 | 12GB | Gemma 2 13B |
| RTX 4090 | 24GB | Gemma 4 26B ✓ |
| A100/H100 | 40GB+ | Gemma 4 31B |

저는 이 표를 무시하고 26B를 받으려다가 낭패를 봤습니다. ~~_권장사항은 권장사항이다_~~

## 모델별 특징

**Gemma 4 (최신, 2026년 3월)**
- 함수 호출(Function Calling) 최적화
- Thinking Mode 지원 (답변 전에 생각)
- 256K 컨텍스트 윈도우
- Hermes Agent와의 호환성 최고

**Gemma 2 (일반적)**
- 전반적으로 안정적
- 다양한 사이즈(2B, 7B, 9B, 27B)
- 리소스 효율성 우수

---

# 5. 실제 사용해보기

## Hermes Agent 실행

```bash
hermes
```

실행하고 "Who are you?"라고 물어봅시다:

```
> Who are you?

I am Hermes Agent, an advanced AI assistant powered by 
Gemma 4 26B model...
```

이렇게 Gemma로부터 답변이 오면 성공입니다!

## API로 접근 (Python)

Hermes Agent는 뒤에서 OpenAI 호환 API를 제공합니다:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="gemma4:26b",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

---

# 6. 마치며

이 과정을 거치면서 배운 게 있습니다:

> 모델은 도구지, 그 자체로는 아무것도 아니다.

Gemma 파일 하나로는 할 수 없는 게 정말 많습니다. Ollama라는 추론 엔진이 있어야 비로소 "작동하는" AI가 됩니다. 그리고 Hermes Agent가 그걸 "에이전트"로 변신시킵니다.

우분투에서 정전도 여러 번 겪고, 메모리 부족으로 삽질하고, 포트 충돌로 답답해했지만, 결국:

1. Ollama로 모델을 띄우고
2. Hermes Agent로 연결하면
3. 정말 강력한 로컬 AI 에이전트가 탄생합니다.

지금 바로 터미널에서:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes
```

이 네 줄만 실행해 보세요. 여러분의 컴퓨터가 갑자기 "생각하는 기계"로 변신할 거예요.

> 새로운 기술을 두려워하지 마세요. 기술은 결국 도구일 뿐입니다. 필요한 건 용기와 조금의 인내심뿐이에요.

Happy prompting! 🚀
