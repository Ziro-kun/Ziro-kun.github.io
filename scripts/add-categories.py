#!/usr/bin/env python3
"""기존 블로그 포스트에 category 필드 일괄 추가"""

import os
import re

BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

# 파일명 키워드 → 카테고리 매핑
CATEGORY_MAP = [
    (["ChatGPT", "수다", "OpenClaw", "AI-Agent", "자식농사", "자동화", "github-actions", "깃허브-블로그"], "AI 탐구"),
    (["Kaggle", "Computer-Vision", "UCI", "Titanic"], "데이터 & ML"),
    (["고누아이", "인텔", "AWS", "자격증", "AI-study"], "자기개발"),
    (["왜케", "생존신고", "근황", "바쁘"], "일상"),
]

def get_category(filename):
    for keywords, category in CATEGORY_MAP:
        for kw in keywords:
            if kw.lower() in filename.lower():
                return category
    return None

def add_category(filepath, category):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "category:" in content:
        print(f"  [스킵] 이미 category 있음: {os.path.basename(filepath)}")
        return False

    # tags: 줄 뒤에 category 삽입
    new_content = re.sub(
        r'(tags:.*\n)',
        f'\\1category: "{category}"\n',
        content,
        count=1
    )

    if new_content == content:
        # tags 없으면 pubDate 뒤에 삽입
        new_content = re.sub(
            r'(pubDate:.*\n)',
            f'\\1category: "{category}"\n',
            content,
            count=1
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

def main():
    files = [f for f in os.listdir(BLOG_DIR) if f.endswith(".md")]
    print(f"총 {len(files)}개 파일 처리 중...\n")

    for filename in sorted(files):
        filepath = os.path.join(BLOG_DIR, filename)
        category = get_category(filename)
        if not category:
            print(f"  [미분류] {filename}")
            continue
        changed = add_category(filepath, category)
        if changed:
            print(f"  [{category}] {filename}")

    print("\n완료!")

if __name__ == "__main__":
    main()
