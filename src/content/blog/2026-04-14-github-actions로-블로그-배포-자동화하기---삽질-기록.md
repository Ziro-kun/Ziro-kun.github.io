---
title: "GitHub Actions로 블로그 배포 자동화하기 - 삽질 기록"
description: "GitHub Actions를 이용해 블로그 배포를 자동화한 과정과 마주친 문제들을 정리했습니다."
pubDate: "2026-04-14"
tags: ["GitHub Actions", "CI/CD", "자동화", "블로그"]
category: "explore"
---

드디어 해냈다. GitHub Actions로 블로그 배포 자동화를 완료했다. 생각보다 복잡했고 삽질도 많았지만, 이제 코드를 푸시하면 자동으로 배포되는 쾌감을 맛봤다.

## 왜 자동화를 시작했나

매번 블로그 글을 작성하고 나서 수동으로 빌드하고 배포하는 과정이 반복되다 보니 정말 답답했다. "이걸 자동화할 수 없을까?" 라는 생각에서 출발했고, GitHub Actions라는 강력한 도구가 있다는 걸 알게 됐다.

## 첫 시도 - 기본 워크플로우 설정

처음엔 간단할 줄 알았다. GitHub의 공식 문서를 따라가면서 기본 워크플로우를 만들어봤다.

```yaml
name: Deploy Blog

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: npm run build
      - name: Deploy
        run: npm run deploy
```

이렇게 간단할 줄 알았는데... 아니었다.

## 문제 1 - 의존성 설치 누락

첫 번째 빌드가 실패했다. `npm run build` 단계에서 모듈을 찾을 수 없다는 에러가 떴다. 당연히 **`npm install`을 먼저 실행해야** 했다. 기본 중의 기본을 빠뜨렸다.

```yaml
steps:
  - uses: actions/checkout@v3
  - name: Install dependencies
    run: npm install
  - name: Build
    run: npm run build
```

## 문제 2 - 배포 권한 설정

다음은 배포 단계에서 막혔다. GitHub 저장소에 접근할 권한이 없다는 메시지였다. 이건 **Personal Access Token(PAT)** 또는 **SSH 키**를 설정해야 하는 부분이었다.

결국 GitHub Settings에서 새로운 token을 생성하고, 이를 저장소 시크릿(Secret)으로 등록했다.

```yaml
- name: Deploy
  env:
    DEPLOY_KEY: ${{ secrets.DEPLOY_TOKEN }}
  run: npm run deploy
```

## 문제 3 - Node 버전 호환성

세 번째 문제는 좀 더 까다로웠다. 로컬에서는 잘 돌아가는데 GitHub Actions에서는 자꾸 타입 에러가 났다. 알고 보니 **Node 버전이 달랐다**. 로컬에선 18을 쓰고 있었는데, Actions는 기본으로 다른 버전을 사용하고 있었다.

```yaml
- uses: actions/setup-node@v3
  with:
    node-version: '18'
```

이 한 줄이 모든 걸 해결했다.

## 최종 워크플로우

여러 시행착오를 거쳐 완성된 워크플로우는 다음과 같다:

```yaml
name: Deploy Blog

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        run: npm run build
      
      - name: Deploy
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: npm run deploy
```

## 배운 점

- **자동화는 한 번의 설정으로 반복적인 작업을 완전히 없앤다**. 이제 푸시 한 번으로 모든 게 끝난다.
- **문서를 제대로 읽는 게 중요하다**. 공식 문서에 다 나와 있었는데 대충 읽다가 삽질을 했다.
- **로컬과 CI 환경의 차이를 항상 고려해야 한다**. 로컬에서 잘 된다고 해서 자동화 환경에서도 잘 되는 건 아니다.

이제 블로그 글을 쓰고 커밋만 하면 자동으로 배포되니 정말 편하다. 다음엔 테스트 자동화도 추가해볼 생각이다.