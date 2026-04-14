import fs from "fs";
import path from "path";

const IMAGES_DIR = path.resolve("src/image");

/**
 * 마크다운에서 이미지 참조를 모두 추출
 * @param {string} markdown
 * @returns {Array<{full: string, path: string, alt: string}>}
 */
export function extractImageReferences(markdown) {
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const images = [];
  let match;

  while ((match = imageRegex.exec(markdown)) !== null) {
    images.push({
      full: match[0],
      alt: match[1],
      path: match[2],
    });
  }

  return images;
}

/**
 * 주어진 이미지 경로가 실제로 존재하는지 확인
 * @param {string} imagePath
 * @returns {boolean}
 */
export function imageFileExists(imagePath) {
  // 상대경로를 절대경로로 변환
  let filePath;

  if (imagePath.startsWith("../../image/")) {
    // ../../image/xxx.png 형식
    filePath = path.join(IMAGES_DIR, imagePath.replace("../../image/", ""));
  } else if (imagePath.startsWith("/src/image/")) {
    // /src/image/xxx.png 형식
    filePath = path.join(IMAGES_DIR, imagePath.replace("/src/image/", ""));
  } else {
    return false;
  }

  return fs.existsSync(filePath);
}

/**
 * 마크다운에서 존재하지 않는 이미지 참조를 제거
 * @param {string} markdown
 * @returns {string} 정리된 마크다운
 */
export function cleanNonexistentImages(markdown) {
  const images = extractImageReferences(markdown);
  let cleaned = markdown;
  const removedImages = [];

  images.forEach(({ full, path: imagePath }) => {
    if (!imageFileExists(imagePath)) {
      cleaned = cleaned.replace(full, "");
      removedImages.push(imagePath);
    }
  });

  // 이전 개행 정리
  cleaned = cleaned.replace(/\n\n\n+/g, "\n\n");

  if (removedImages.length > 0) {
    console.warn(
      `⚠️  다음 이미지는 존재하지 않아 제거되었습니다: ${removedImages.join(", ")}`
    );
  }

  return cleaned;
}
