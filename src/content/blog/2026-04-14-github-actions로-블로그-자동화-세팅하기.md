---
title: "GitHub Actions로 블로그 자동화 세팅하기"
description: "깃허브 액션을 처음 다뤄봤는데, 예상치 못한 삽질들을 거쳐 결국 블로그 자동 배포 파이프라인을 완성했습니다."
pubDate: "2026-04-14"
tags: ["github-actions", "automation", "ci-cd", "블로그"]
category: "explore"
---

# 0. 시작하기 전에

집에 돌아와 블로그 세팅을 시작했지만, GitHub Actions와 워크플로우는 생각보다 만만하지 않았습니다. 자동화는 멋진데, 그걸 구현하는 과정은... 음, 다르더라고요.

> "자동화면 자동화지, 뭐가 이렇게 복잡해?"

결국 여러 번의 시행착오를 거쳐 블로그 자동 배포 파이프라인을 완성했습니다. 그 과정을 솔직하게 풀어낼게요.

---

# 1. 왜 GitHub Actions인가

처음엔 간단했습니다. 블로그 포스트를 쓰고 → 깃에 푸시하고 → 배포하는 과정이 반복되고 있었거든요.

> "매번 수동으로 배포하는 건 너무 비효율적이잖아?"

그래서 결정했습니다. **GitHub Actions를 통해 푸시 → 자동 빌드 → 자동 배포** 파이프라인을 만들자고요.

장점은 명확했습니다:
- GitHub 저장소 내에서 모든 게 처리된다
- 별도 서버나 CI/CD 도구가 필요 없다
- 무료다 ~~(아주 중요)~~
- 문서가 많다 ~~(근데 초보자 입장에선 많은 게 복잡하다)~~

---

# 2. 첫 시도: 워크플로우 파일 작성

GitHub Actions는 `.github/workflows/` 디렉토리 안의 YAML 파일로 동작합니다.

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - run: npm run deploy
```

간단하죠? 코드를 푸시하면 → 자동으로 빌드되고 → 배포된다는 거였습니다.

> 현실은 그렇게 단순하지 않았습니다.

---

# 3. 첫 번째 삽질: 환경변수 문제

빌드는 잘됐는데, 배포 단계에서 문제가 생겼습니다. 제 배포 스크립트가 환경변수를 필요로 했거든요.

```
Error: DEPLOY_KEY is not defined
```

> "어? 내 로컬에선 잘 되는데?"

로컬 환경에선 `.env` 파일에 키가 저장되어 있었습니다. 하지만 GitHub Actions 러너는 그걸 모르죠.

**해결책:** GitHub 저장소의 Settings → Secrets and variables → Actions에서 환경변수를 등록했습니다.

```yaml
- run: npm run deploy
  env:
    DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
    API_URL: ${{ secrets.API_URL }}
```

이제 워크플로우에서 시크릿에 접근할 수 있게 됐습니다.

---

# 4. 두 번째 삽질: 빌드 실패의 미스터리

몇 시간 뒤, 빌드가 갑자기 실패하기 시작했습니다.

```
Error: Cannot find module 'some-package'
```

로컬에선 정상인데, 러너에선 왜 모듈을 못 찾을까요?

> "lock 파일을 커밋하지 않았나?"

확인해보니 `package-lock.json`을 `.gitignore`에 넣어뒀더라고요. 로컬에서는 캐시된 node_modules가 있어서 상관없었지만, 깨끗한 러너 환경에서는 의존성을 제대로 설치할 수 없었던 거였습니다.

**해결책:** lock 파일을 저장소에 커밋했습니다.

```bash
git add package-lock.json
git commit -m "Add lock file for reproducible builds"
```

이제 모든 환경에서 동일한 버전의 패키지가 설치됩니다.

---

# 5. 세 번째 삽질: 배포 권한 문제

빌드는 성공했는데 배포가 실패했습니다.

```
Error: Permission denied
```

제 배포 스크립트가 특정 디렉토리에 쓰기 권한이 필요했는데, GitHub Actions 러너가 그 권한을 갖지 못했던 거예요.

> "이게 뭐 하는 짓이야..."

멘탈이 무너지기 시작했습니다. ~~(밤 11시쯤 됐을 때)~~

**해결책:** 워크플로우에서 배포 스크립트를 실행하기 전에 권한을 설정했습니다.

```yaml
- name: Set permissions
  run: chmod +x ./scripts/deploy.sh

- name: Deploy
  run: ./scripts/deploy.sh
```

추가로, SSH 키를 GitHub Secrets에 저장하고 워크플로우에서 사용하도록 설정했습니다.

```yaml
- name: Setup SSH
  run: |
    mkdir -p ~/.ssh
    echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts
```

---

# 6. 마침내, 성공

모든 문제를 해결한 최종 워크플로우입니다:

```yaml
name: Deploy Blog

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          NODE_ENV: production
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts
      
      - name: Deploy
        run: npm run deploy
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
```

이제 코드를 `main` 브랜치에 푸시하면:
1. 자동으로 의존성이 설치되고
2. 빌드가 실행되고
3. 배포 서버에 파일이 업로드된다

> 이게 자동화의 맛이구나.

---

# 7. 배운 점

이 과정을 거치며 깨달은 게 몇 가지 있습니다:

* **환경의 차이를 존중하라** — 로컬과 CI/CD 환경은 다르다. 모든 설정을 명시적으로 관리해야 한다.
* **lock 파일은 필수다** — 재현 가능한 빌드를 위해선 의존성 버전을 고정해야 한다.
* **권한 관리는 섬세하게** — 배포 서버 접근 권한, SSH 키 등을 안전하게 관리해야 한다.
* **로그를 꼼꼼히 읽자** — GitHub Actions의 로그는 매우 상세하다. 문제의 원인이 거기 있다.

---

# 8. 마무리

GitHub Actions 자동화 설정은 처음엔 복잡해 보이지만, 차근차근 하나씩 문제를 해결하다 보면 결국 된다는 거예요. 

삽질은 했지만, 이제 블로그에 글을 올릴 때마다 자동으로 배포되는 쾌감을 느낄 수 있습니다.

> 새로운 기술을 배울 때 실패는 필수 불가결합니다. 두려워하지 마십쇼. 그 과정에서 배우는 게 가장 큽니다.

다음 번엔 테스트 자동화도 추가해봐야겠어요. ~~(또 삽질할 준비가 됐습니다)~~