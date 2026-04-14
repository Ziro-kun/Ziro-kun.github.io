/**
 * input.txt에서 [images: file1.png, file2.png] 형식으로 명시된 이미지 추출
 * @param {string} input
 * @returns {Array<string>} 이미지 파일명 배열
 */
export function extractImagesFromInput(input) {
  // [images: file1.png, file2.png] 형식 지원
  const match = input.match(/\[images:\s*(.+?)\]/s);
  if (match) {
    return match[1]
      .split(",")
      .map((f) => f.trim())
      .filter((f) => /\.(jpg|jpeg|png|webp|gif)$/i.test(f));
  }
  return [];
}

/**
 * input.txt에서 이미지 메타섹션 제거
 * @param {string} input
 * @returns {string} 정리된 input
 */
export function removeImageMetaFromInput(input) {
  return input.replace(/\[images:\s*[^\]]+\]\s*/s, "");
}

/**
 * input.txt에서 [hero-image: filename.png] 형식으로 명시된 썸네일 이미지 추출
 * @param {string} input
 * @returns {string|null} 썸네일 파일명 또는 null
 */
export function extractHeroImageFromInput(input) {
  const match = input.match(/\[hero-image:\s*([^\]]+)\]/);
  return match ? match[1].trim() : null;
}

/**
 * input.txt에서 hero-image 메타섹션 제거
 * @param {string} input
 * @returns {string} 정리된 input
 */
export function removeHeroImageMetaFromInput(input) {
  return input.replace(/\[hero-image:\s*[^\]]+\]\s*/s, "");
}
