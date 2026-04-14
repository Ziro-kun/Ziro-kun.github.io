import fs from "fs";
import path from "path";
import { askClaude } from "./claude.js";
import {
  extractImagesFromInput,
  removeImageMetaFromInput,
  extractHeroImageFromInput,
  removeHeroImageMetaFromInput,
} from "./imageExtractor.js";
import { cleanNonexistentImages } from "./validateImages.js";

const POSTS_DIR = path.resolve("src/content/blog");

function sanitizeFilename(title) {
  return title
    .replace(/["""'']/g, "")
    .replace(/\s+/g, "-")
    .replace(/[^\w\-가-힣]/g, "")
    .toLowerCase();
}

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

export async function generateAndSavePost(userPrompt, styleGuide = "") {
  // 입력에서 이미지 메타 추출
  const heroImage = extractHeroImageFromInput(userPrompt);
  const images = extractImagesFromInput(userPrompt);
  let cleanInput = removeHeroImageMetaFromInput(userPrompt);
  cleanInput = removeImageMetaFromInput(cleanInput);

  const imageInfo =
    images.length > 0
      ? `\n\n[포함된 이미지 파일 목록]\n${images.map((img) => `- ${img}`).join("\n")}\n마크다운에서는 ![이미지 설명](../../image/{파일명}) 형식으로 삽입하세요.`
      : "";

  const heroImageInfo = heroImage
    ? `\n\nheroImage 파일: ${heroImage}\nfrontmatter의 heroImage 필드에 다음을 추가하세요: ../../../assets/blog/${heroImage}`
    : "";

  const systemPrompt = styleGuide
    ? `다음 글쓰기 스타일을 따라주세요:\n\n${styleGuide}\n\n`
    : "";

  const today = getToday();
  const fullPrompt = `${systemPrompt}아래 내용을 바탕으로 블로그 포스트를 작성해주세요.
반드시 아래 형식의 YAML frontmatter로 시작해야 합니다. 코드펜스(\`\`\`)로 감싸지 말고 --- 로 바로 시작하세요.
pubDate는 반드시 따옴표로 감싼 문자열이어야 합니다.${heroImage ? `\nheroImage가 지정되었으므로 frontmatter에 다음을 추가하세요: heroImage: ../../../assets/blog/${heroImage}` : ""}

---
title: "제목"
description: "한 줄 요약"
pubDate: "${today}"
tags: ["태그1", "태그2"]${heroImage ? `\nheroImage: ../../../assets/blog/${heroImage}` : ""}
---

${cleanInput}${imageInfo}${heroImageInfo}`;

  let content = await askClaude(fullPrompt);

  // 존재하지 않는 이미지 참조 자동 정리
  content = cleanNonexistentImages(content);

  // title 추출
  const titleMatch = content.match(/title:\s*["']?(.+?)["']?\s*\n/);
  const title = titleMatch ? titleMatch[1] : "untitled";
  const filename = `${getToday()}-${sanitizeFilename(title)}.md`;
  const filepath = path.join(POSTS_DIR, filename);

  fs.writeFileSync(filepath, content, "utf-8");
  console.log(`포스트 생성 완료: ${filepath}`);
  return filepath;
}
