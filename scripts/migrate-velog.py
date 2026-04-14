#!/usr/bin/env python3
"""
Velog → Astro 블로그 마이그레이션 스크립트
사용법: python3 scripts/migrate-velog.py
"""

import requests
import json
import os
import re

API_URL = "https://v2.velog.io/graphql"
USERNAME = "applez"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")


def fetch_posts(username, cursor=None):
    query = """
    query Posts($username: String!, $cursor: ID) {
      posts(username: $username, cursor: $cursor) {
        id
        title
        short_description
        url_slug
        released_at
        tags
      }
    }
    """
    variables = {"username": username}
    if cursor:
        variables["cursor"] = cursor

    res = requests.post(API_URL, json={"query": query, "variables": variables})
    res.raise_for_status()
    return res.json()["data"]["posts"]


def fetch_post_body(username, url_slug):
    query = """
    query Post($username: String!, $url_slug: String!) {
      post(username: $username, url_slug: $url_slug) {
        body
      }
    }
    """
    variables = {"username": username, "url_slug": url_slug}
    res = requests.post(API_URL, json={"query": query, "variables": variables})
    res.raise_for_status()
    return res.json()["data"]["post"]["body"]


def sanitize_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = re.sub(r'\s+', "-", title.strip())
    return title[:80]


def format_date(released_at):
    # "2023-05-12T..." → "2023-05-12"
    return released_at[:10]


def yaml_string(value):
    """큰따옴표가 포함된 경우 단일따옴표로, 그렇지 않으면 큰따옴표로 감싸기"""
    if '"' in value:
        return f"'{value}'"
    return f'"{value}"'

def build_frontmatter(title, description, pub_date, tags):
    tag_list = ", ".join([f'"{t}"' for t in tags])
    desc = description.replace("'", "") if description else ""
    return f"""---
title: {yaml_string(title)}
description: {yaml_string(desc)}
pubDate: "{pub_date}"
tags: [{tag_list}]
---
"""


def migrate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Velog 사용자 '{USERNAME}' 글 목록 가져오는 중...")
    all_posts = []
    cursor = None

    while True:
        batch = fetch_posts(USERNAME, cursor)
        if not batch:
            break
        all_posts.extend(batch)
        cursor = batch[-1]["id"]
        print(f"  {len(all_posts)}개 수집 중...")
        if len(batch) < 20:
            break

    print(f"\n총 {len(all_posts)}개 포스트 발견. 변환 시작...\n")

    success, skip = 0, 0
    for post in all_posts:
        title = post["title"]
        slug = post["url_slug"]
        pub_date = format_date(post["released_at"])
        tags = post.get("tags", [])
        description = post.get("short_description", "")

        filename = f"{pub_date}-{sanitize_filename(title)}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"  [스킵] 이미 존재: {filename}")
            skip += 1
            continue

        try:
            body = fetch_post_body(USERNAME, slug)
            frontmatter = build_frontmatter(title, description, pub_date, tags)
            content = frontmatter + "\n" + body

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"  [완료] {filename}")
            success += 1
        except Exception as e:
            print(f"  [오류] {title}: {e}")

    print(f"\n완료! 성공: {success}개 / 스킵: {skip}개")
    print(f"저장 위치: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    migrate()
