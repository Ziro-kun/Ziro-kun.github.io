---
title: "GitHub Actions로 블로그 자동화 세팅하기 — 삽질의 기록"
description: "손으로 배포하던 시대는 끝. GitHub Actions 자동화로 블로그 배포를 완전히 자동화한 과정을 공개합니다."
pubDate: "2026-04-14"
tags: ["GitHub Actions", "자동화", "블로그", "CI/CD"]
category: "explore"
---

# 0. 서론

> "매번 손으로 배포하는 게 너무 귀찮아..."

블로그 글을 쓸 때마다 저장소에 푸시하고, 빌드하고, 배포하고... 이 반복 작업이 정말 지겨웠습니다. 그러다 문득 생각했어요.

**"이 과정을 자동화할 수 있지 않을까?"**

결국 GitHub Actions를 손에 들게 되었고, 이틀간의 삽질 끝에 완전 자동화를 이루어냈습니다. 오늘은 그 여정을 공유하려고 합니다.

---

# 1. 문제 상황 — 매번 손으로 하던 배포

제가 겪던 문제는 간단했습니다.

1. 로컬에서 블로그 글 작성
2. Git 커밋 & 푸시
3. 빌드 스크립트 실행 (`npm run build`)
4. 빌드된 파일을 배포 서버에 업로드
5. 배포 완료

~~_정말 자동화가 필요한 상황이었습니다._~~

이 과정이 매번 반복되니까요. 특히 밤 11시에 블로그를 배포해야 할 때는 정말 답답했습니다.

> "컴퓨터가 이 정도는 알아서 해주지 않을까?"

---

# 2. GitHub Actions 설정 시작

## 2.1 첫 번째 시도 — 기본 워크플로우

GitHub Actions의 기본 개념부터 시작했습니다.

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
```

> "이 정도면 되겠지?"

너무 단순했습니다. 당연히 첫 번째 실행에서 실패했죠.

## 2.2 환경변수와의 싸움

빌드는 성공했는데, 배포 단계에서 막혔습니다.

```
Error: Missing environment variable API_KEY
```

제 배포 스크립트가 여러 환경변수를 필요로 했거든요. GitHub Secrets에 등록해야 한다는 걸 깨닫는 데 한참이 걸렸습니다.

~~_문서를 더 꼼꼼히 읽었으면 좋았을 텐데..._~~

### 해결책: GitHub Secrets 활용

```yaml
- run: npm run build
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
    DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
```

이제 환경변수도 안전하게 관리할 수 있었습니다.

---

# 3. 배포 자동화 — SSH 연결

이제 빌드는 잘되는데, 배포를 어떻게 자동화할지가 문제였습니다.

저는 서버에 SSH로 접속해서 파일을 업로드하는 방식을 사용 중이었거든요.

## 3.1 SSH 키 설정

GitHub Actions에서 서버에 접속하려면 SSH 키가 필요했습니다.

```yaml
- name: Deploy to Server
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.DEPLOY_HOST }}
    username: ${{ secrets.DEPLOY_USER }}
    key: ${{ secrets.DEPLOY_KEY }}
    script: |
      cd /var/www/blog
      rm -rf dist/*
      # 배포 스크립트
```

처음에는 SSH 키 형식이 맞지 않아서 자꾸 실패했습니다.

> "SSH 키가 뭐 이렇게 까다로워?"

결국 OpenSSH 형식으로 변환하고 나서야 작동했어요.

---

# 4. 세부 조정 — 배포 후 처리

## 4.1 빌드 결과 캐싱

매번 `npm install`을 하니까 시간이 너무 오래 걸렸습니다.

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

이걸 추가하니까 배포 시간이 거의 절반으로 줄었습니다.

## 4.2 배포 성공/실패 알림

배포가 완료되면 Slack으로 알림을 받도록 설정했습니다.

```yaml
- name: Slack Notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

이제 배포가 되었는지 안 되었는지 실시간으로 알 수 있게 되었습니다.

---

# 5. 최종 결과

현재 제 블로그 배포 워크플로우는 이렇게 작동합니다:

1. 로컬에서 블로그 글 작성
2. Git 커밋 & 푸시 (`git push`)
3. **GitHub Actions가 자동으로:**
   - Node.js 설정
   - 패키지 설치 (캐시 활용)
   - 빌드 수행
   - SSH로 서버에 접속
   - 파일 배포
   - Slack 알림 전송
4. 배포 완료 ✨

~~_이제 저는 그냥 글만 쓰면 됩니다._~~

---

# 6. 배운 점

이 과정에서 정말 많이 배웠습니다:

* **GitHub Actions는 생각보다 강력합니다** — 환경 구성부터 배포까지 거의 모든 걸 자동화할 수 있어요.
* **환경변수와 Secrets는 보안의 기본** — 절대 하드코딩하면 안 됩니다.
* **문서를 읽는 게 가장 빠른 해결책** — 삽질하기 전에 공식 문서부터 읽읍시다.
* **캐싱은 정말 효과적** — 몇 줄의 설정으로 배포 시간을 크게 단축할 수 있습니다.

---

# 7. 마무리

자동화는 처음엔 설정이 복잡해 보이지만, 한 번 구성하고 나면 정말 큰 생산성 향상을 느낄 수 있습니다.

> 여러분도 반복되는 배포 작업이 있다면, GitHub Actions로 자동화해보세요. 삽질도 있겠지만, 그 과정이 여러분을 더 좋은 개발자로 만들 거예요.

이제 저는 블로그 글에만 집중할 수 있게 되었습니다. 그게 바로 자동화의 진정한 의미 아닐까요?