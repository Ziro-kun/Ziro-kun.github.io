import fs from "fs";
import path from "path";
import { askClaude } from "./claude.js";

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
  const systemPrompt = styleGuide
    ? `다음 글쓰기 스타일을 따라주세요:\n\n${styleGuide}\n\n`
    : "";

  const fullPrompt = `${systemPrompt}아래 내용을 바탕으로 블로그 포스트를 작성해주세요.
반드시 YAML frontmatter로 시작해야 합니다 (title, description, pubDate, tags 포함).

${userPrompt}`;

  const content = await askClaude(fullPrompt);

  // title 추출
  const titleMatch = content.match(/title:\s*["']?(.+?)["']?\s*\n/);
  const title = titleMatch ? titleMatch[1] : "untitled";
  const filename = `${getToday()}-${sanitizeFilename(title)}.md`;
  const filepath = path.join(POSTS_DIR, filename);

  fs.writeFileSync(filepath, content, "utf-8");
  console.log(`포스트 생성 완료: ${filepath}`);
  return filepath;
}
