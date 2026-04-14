#!/usr/bin/env python3
"""
기존 마이그레이션된 Velog 포스트에 thumbnail 필드 추가
사용법: python3 scripts/add-thumbnails.py
"""

import requests
import os
import re

API_URL = "https://v2.velog.io/graphql"
USERNAME = "applez"
BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")


def fetch_all_posts(username):
    query = """
    query Posts($username: String!, $cursor: ID) {
      posts(username: $username, cursor: $cursor) {
        id
        title
        url_slug
        thumbnail
      }
    }
    """
    all_posts = []
    cursor = None
    while True:
        variables = {"username": username}
        if cursor:
            variables["cursor"] = cursor
        res = requests.post(API_URL, json={"query": query, "variables": variables})
        res.raise_for_status()
        batch = res.json()["data"]["posts"]
        if not batch:
            break
        all_posts.extend(batch)
        cursor = batch[-1]["id"]
        if len(batch) < 20:
            break
    return all_posts


def normalize(text):
    """비교용 정규화: 소문자, 특수문자/공백 제거"""
    return re.sub(r'[^a-z0-9가-힣]', '', text.lower())


def get_frontmatter_title(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return match.group(1).strip().strip('"\'') if match else None


def add_thumbnail_to_file(filepath, thumbnail_url):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "thumbnail:" in content:
        return False

    new_content = re.sub(
        r'(category:.*\n)',
        f'\\1thumbnail: "{thumbnail_url}"\n',
        content, count=1
    )
    if new_content == content:
        new_content = re.sub(
            r'(tags:.*\n)',
            f'\\1thumbnail: "{thumbnail_url}"\n',
            content, count=1
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    print("Velog에서 포스트 목록 가져오는 중...")
    posts = fetch_all_posts(USERNAME)

    # title 정규화 → thumbnail 매핑
    thumb_map = {
        normalize(p["title"]): p["thumbnail"]
        for p in posts if p.get("thumbnail")
    }
    print(f"  thumbnail 있는 글: {len(thumb_map)}개\n")

    files = [f for f in os.listdir(BLOG_DIR) if f.endswith(".md")]
    success, skip, no_match = 0, 0, 0

    for filename in sorted(files):
        filepath = os.path.join(BLOG_DIR, filename)
        title = get_frontmatter_title(filepath)
        if not title:
            no_match += 1
            continue

        norm_title = normalize(title)
        thumbnail_url = thumb_map.get(norm_title)

        if not thumbnail_url:
            print(f"  [미매칭] {filename}")
            no_match += 1
            continue

        changed = add_thumbnail_to_file(filepath, thumbnail_url)
        if changed:
            print(f"  [추가] {filename}")
            success += 1
        else:
            print(f"  [스킵] 이미 있음: {filename}")
            skip += 1

    print(f"\n완료! 추가: {success}개 / 스킵: {skip}개 / 미매칭: {no_match}개")


if __name__ == "__main__":
    main()
