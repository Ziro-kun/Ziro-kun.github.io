import fs from "fs";
import path from "path";

const IMAGES_DIR = path.resolve("src/image");

export function getImagesForPost(userPrompt) {
  // userPrompt에서 제목 추출 (첫 줄)
  const titleMatch = userPrompt.match(/^(.+)/);
  const titleText = titleMatch ? titleMatch[1].slice(0, 50) : "";

  // 제목에서 파일명 규칙에 맞는 prefix 생성
  const titlePrefix = titleText
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-가-힣]/g, "")
    .slice(0, 30);

  if (!fs.existsSync(IMAGES_DIR)) {
    return [];
  }

  // 해당 제목으로 시작하는 모든 이미지 파일 찾기
  const files = fs.readdirSync(IMAGES_DIR);
  const imageFiles = files.filter(
    (f) =>
      /\.(jpg|jpeg|png|webp|gif)$/i.test(f) &&
      (titlePrefix === "" || f.startsWith(titlePrefix))
  );

  return imageFiles.map((f) => ({
    filename: f,
    path: `/src/image/${f}`,
    relativePath: `../../image/${f}`, // src/content/blog/에서 상대경로
  }));
}
