---
title: "GitHub Actions로 블로그 자동화 세팅하기 (삽질 기록)"
description: "GitHub Actions를 이용해 블로그 배포를 자동화하는 과정에서 겪었던 시행착오와 해결 방법"
pubDate: "2026-04-13"
tags: ["GitHub Actions", "자동화", "CI/CD", "블로그"]
---

드디어 GitHub Actions 자동화 블로그 세팅을 완료했다. 생각보다 **삽질이 많았지만** 결국 해냈다는 게 뿌듯하네.

## 왜 자동화가 필요했나

블로그 포스트를 작성할 때마다 수동으로 빌드하고 배포하는 과정이 반복되니까 답답했다. 매번 같은 명령어를 치고, 같은 실수를 반복하고... 이런 게 쌓이면 생산성이 떨어진다. 그래서 **GitHub Actions로 자동화**해서 푸시만 하면 알아서 배포되도록 만들기로 결심했다.

## 초반 설정에서 마주친 문제들

### 1. 워크플로우 문법이 생각보다 복잡했다

처음엔 YAML 문법이 헷갈렸다. 들여쓰기 하나 잘못하면 전체가 망가지는데, 에러 메시지도 명확하지 않아서 한참 헤맸다.

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
      - name: Build
        run: npm run build
```

위처럼 기본 구조부터 다시 공부했다.

### 2. 환경 변수 설정 실패

배포할 때 필요한 토큰이나 키를 어디에 저장해야 하는지 몰라서 좀 헤맸다. **GitHub의 Secrets 설정**을 활용해야 한다는 걸 알고 나서야 진전이 있었다.

Repository Settings → Secrets and variables → Actions에서 환경 변수를 등록하면 워크플로우에서 접근할 수 있다.

```yaml
- name: Deploy
  env:
    DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
  run: ./deploy.sh
```

### 3. 권한 문제

처음엔 GitHub Actions가 저장소에 푸시할 권한이 없어서 배포가 실패했다. GITHUB_TOKEN의 권한 설정을 조정해야 했다.

```yaml
permissions:
  contents: write
  pages: write
```

이 부분을 추가하니까 문제가 해결됐다.

## 결국 성공한 최종 워크플로우

여러 시행착오를 거쳐서 완성된 워크플로우는 이렇다:

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main

permissions:
  contents: write
  pages: write

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
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

이제 `main` 브랜치에 푸시하면 **자동으로 빌드되고 배포**된다.

## 배운 점과 다음 단계

- **YAML 문법은 정말 중요하다**: 들여쓰기, 콜론, 대시 하나도 놓치면 안 된다.
- **GitHub 공식 문서가 최고다**: 처음부터 문서를 정독했으면 삽질이 덜했을 것 같다.
- **Secrets 관리는 필수**: 토큰이나 키는 절대 코드에 노출되면 안 된다.

다음은 이 워크플로우에 **테스트 자동화**를 추가하고, 배포 전에 코드 품질을 체크하는 단계를 넣어볼 생각이다. 한 걸음씩 더 나아가면 될 것 같다.