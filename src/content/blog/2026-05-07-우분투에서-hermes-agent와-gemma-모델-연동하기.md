---
title: "우분투에서 Hermes Agent와 Gemma 모델 연동하기"
description: "Ollama를 통해 로컬 LLM을 실행하고 Hermes Agent와 연결하는 완전 가이드"
pubDate: "2026-05-07"
tags: ["LLM", "Gemma", "Ollama", "Hermes Agent", "우분투"]
category: "explore"
heroImage: "https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 19-27-33.png"
---

# 0. 서론

며칠 전 Gemini와 대화하다가 문득 드는 생각이 있었습니다.

> "우리도 로컬 환경에서 LLM을 직접 실행할 수 있지 않을까?"

그렇게 시작된 삽질의 여정. 처음엔 Gemma 모델 파일만 받으면 되겠지 싶었는데, 현실은 그리 녹록지 않았습니다. 모델 파일만으로는 아무것도 못 하더군요. 추론 엔진(Inference Engine)이 필요했던 겁니다.

이 글은 우분투 환경에서 **Ollama**를 이용해 Gemma 모델을 실행하고, **Hermes Agent**와 연동하는 과정을 정리한 것입니다. 제 삽질이 누군가에겐 지름길이 되길 바랍니다.

---

# 1. 문제 상황: 모델 파일만으로는 부족하다

처음엔 이렇게 생각했습니다.

> Gemma 모델 파일을 받으면 → 그걸로 추론하면 된다?

~~천진했습니다.~~

실제로는:
- **모델 파일** (`.safetensors`, `.gguf` 등) — 가중치(weights)만 들어있음
- **추론 엔진** — 그 가중치를 메모리에 로드하고, 텍스트 처리하고, GPU/CPU 최적화까지 담당

즉, 모델 파일은 설계도일 뿐, 실제로 집을 짓는 건 추론 엔진이라는 뜻이죠.

---

# 2. 추론 엔진 선택지와 Ollama를 고른 이유

우분투에서 쓸 수 있는 추론 엔진은 여러 개입니다:

| 엔진 | 장점 | 단점 |
|------|------|------|
| **Ollama** | 설치 간단, 모델 관리 자동, API 기본 제공 | 커스터마이징 제한적 |
| **vLLM** | 고성능, 배치 처리 최적화 | 설치/설정 복잡 |
| **llama.cpp** | 경량, CPU에서도 빠름 | CLI 중심, API 별도 구축 필요 |
| **LM Studio** | GUI 친화적 | 무겁고 느림 |

저는 **Ollama**를 선택했습니다. 이유는 간단합니다:

> 모델 다운로드 → 메모리 로드 → API 서버 생성을 **한 번에** 처리해줍니다.

그리고 Hermes Agent와의 연동도 가장 깔끔했거든요.

---

# 3. 단계별 설치 및 설정

## 3.1 Ollama 설치

우분투에서 Ollama를 설치하는 건 정말 간단합니다:

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

설치 후 버전 확인:

```bash
ollama --version
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-09 23-11-22.png" alt="Ollama 버전 확인" style="width:100%;max-width:800px;" />
~~_이 순간, 모든 게 시작되었습니다_~~

## 3.2 Gemma 모델 실행

Ollama를 설치하면 `ollama run` 명령어로 모델을 바로 실행할 수 있습니다:

```bash
ollama run gemma:7b
```

처음 실행하면 모델을 다운로드합니다. 사이즈에 따라 시간이 걸리죠.

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-10 00-53-21.png" alt="Gemma 모델 다운로드" style="width:100%;max-width:800px;" />
~~_기다림의 미학_~~

다운로드가 완료되면 대화형 프롬프트가 나타납니다:

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-03-10 01-16-51.png" alt="Gemma 프롬프트" style="width:100%;max-width:800px;" />
~~_드디어... 대화할 수 있다_~~

**Ctrl + D** (또는 `exit`)로 빠져나옵니다.

### 모델 선택 가이드

하드웨어 사양에 따라:

- **8GB 이상 VRAM** → `gemma:7b` 추천
- **12GB 이상 VRAM** → `gemma:13b` 고려
- **24GB 이상 VRAM** → `gemma2:27b` 가능
- **CPU만 사용** → `gemma:2b` 추천 (느리지만 동작함)

저는 7b로 진행했습니다.

## 3.3 Hermes Agent 설치

이제 Hermes Agent를 설치합니다:

```bash
pip install hermes-agent
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 07-36-53.png" alt="Hermes Agent 설치" style="width:100%;max-width:800px;" />
~~_pip의 무한 로딩 지옥_~~

## 3.4 Hermes 설정

이제 Hermes가 Ollama의 Gemma 모델을 사용하도록 설정합니다:

```bash
hermes setup
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 19-27-33.png" alt="Hermes setup 시작" style="width:100%;max-width:800px;" />

대화형으로 진행되는데, 핵심 항목들을 입력합니다:

**질문 1: Provider 선택**
```
Select LLM Provider (openai/ollama/claude): ollama
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 19-40-57.png" alt="Provider 선택" style="width:100%;max-width:800px;" />

**질문 2: Ollama API 엔드포인트**
```
Enter Ollama API URL (default: http://localhost:11434): 
```

기본값으로 두면 됩니다. (Enter 누르기)

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-44.png" alt="Ollama API URL" style="width:100%;max-width:800px;" />

**질문 3: 모델명 입력**
```
Enter Model name (e.g., gpt-4, claude-3-sonnet, gemma:7b): gemma:7b
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-50.png" alt="모델명 입력" style="width:100%;max-width:800px;" />

**질문 4: 추가 설정들**

나머지 질문들은 대부분 기본값으로 진행했습니다:

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-21-58.png" alt="추가 설정" style="width:100%;max-width:800px;" />

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-23-32.png" alt="설정 계속" style="width:100%;max-width:800px;" />

설정 완료 후:

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-31-18.png" alt="설정 완료" style="width:100%;max-width:800px;" />
~~_성공... 아니 진짜?_~~

---

# 4. 실행 및 테스트

## 4.1 Ollama 백그라운드 실행

Hermes를 사용하려면 Ollama가 백그라운드에서 계속 실행되어야 합니다:

```bash
ollama serve
```

또는 별도 터미널에서:

```bash
nohup ollama serve > ollama.log 2>&1 &
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-31-52.png" alt="Ollama serve" style="width:100%;max-width:800px;" />

## 4.2 Hermes Agent 실행

이제 Python에서 Hermes Agent를 사용할 수 있습니다:

```python
from hermes_agent import Agent

agent = Agent()
response = agent.run("Hello, what's your name?")
print(response)
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-41-37.png" alt="Hermes Agent 테스트" style="width:100%;max-width:800px;" />

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-53-17.png" alt="응답 확인" style="width:100%;max-width:800px;" />
~~_정말... 말을 한다_~~

---

# 5. 주의사항 및 트러블슈팅

## 5.1 GPU 메모리 부족 에러

```
CUDA out of memory
```

**해결책:**
- 더 작은 모델 사용: `gemma:2b` 또는 `gemma:7b`
- 또는 CPU 모드로 실행: `OLLAMA_NUM_GPU=0 ollama run gemma:7b`

## 5.2 포트 충돌 (11434 already in use)

```bash
lsof -i :11434  # 포트 사용 프로세스 확인
kill -9 <PID>   # 프로세스 종료
```

## 5.3 권한 문제 (Permission denied)

```bash
sudo usermod -aG ollama $USER
newgrp ollama
```

## 5.4 Hermes 설정 파일 위치

설정은 `~/.hermes/config.json`에 저장됩니다:

```bash
cat ~/.hermes/config.json
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 20-57-51.png" alt="설정 파일" style="width:100%;max-width:800px;" />

## 5.5 모델 메모리 로드 시간

처음 실행 시 모델을 메모리에 로드하는데 20~30초 걸릴 수 있습니다. 이는 정상입니다.

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 21-04-27.png" alt="로드 시간" style="width:100%;max-width:800px;" />

---

# 6. 고급 설정

## 6.1 API 엔드포인트 직접 호출

Ollama가 실행 중이면 HTTP API로도 접근 가능합니다:

```bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "gemma:7b",
    "prompt": "Why is the sky blue?",
    "stream": false
  }'
```

<img src="https://raw.githubusercontent.com/Ziro-kun/Ziro-kun.github.io/main/src/image/스크린샷 2026-04-14 21-22-19.png" alt="API 호출" style="width:100%;max-width:800px;" />

## 6.2 여러 모델 동시 운영

Ollama는 여러 모델을 설치하고 필요에 따라 전환할 수 있습니다:

```bash
ollama pull gemma:2b
ollama pull gemma:7b
ollama pull gemma2:27b

# 사용할 모델 선