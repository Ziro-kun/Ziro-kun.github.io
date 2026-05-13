#!/usr/bin/env python3
"""
포트폴리오 파일 Obsidian → Astro 변환 스크립트
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime


def convert_frontmatter(content):
    """한글 frontmatter 키를 영문으로 변환"""
    if not content.startswith('---'):
        return content

    lines = content.split('\n')
    frontmatter_end = -1
    for i in range(1, len(lines)):
        if lines[i] == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return content

    frontmatter_lines = lines[1:frontmatter_end]
    body = '\n'.join(lines[frontmatter_end + 1:])

    # 한글 키 → 영문 키 매핑
    key_map = {
        '설명': 'description',
        '역할': 'role',
        '유형': 'type',
        '팀원 수': 'teamSize',
        '파일과 미디어': '_skip_',
        'topics': 'github',
    }

    new_frontmatter = ['---']
    skip_next_lines = 0
    github_url = None

    for i, line in enumerate(frontmatter_lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue

        skip = False
        for korean_key, english_key in key_map.items():
            if line.startswith(f'{korean_key}:'):
                if english_key == '_skip_':
                    # 파일과 미디어는 제거, 여러 줄이므로 다음 줄들도 제거
                    skip = True
                    for j in range(i + 1, len(frontmatter_lines)):
                        if frontmatter_lines[j].startswith('  '):
                            skip_next_lines += 1
                        else:
                            break
                elif english_key == 'github':
                    # topics → github: 첫 번째 URL만 추출
                    for j in range(i + 1, len(frontmatter_lines)):
                        if '- ' in frontmatter_lines[j] and 'http' in frontmatter_lines[j]:
                            github_url = frontmatter_lines[j].replace('- ', '').strip().strip('"')
                            skip_next_lines += 1
                            break
                else:
                    # 일반 변환
                    new_line = line.replace(f'{korean_key}:', f'{english_key}:')
                    new_frontmatter.append(new_line)
                break

        if not skip and line and not line.startswith(('설명:', '역할:', '유형:', '팀원 수:', '파일과 미디어:', '  -')):
            new_frontmatter.append(line)

    # github URL 추가
    if github_url:
        new_frontmatter.append(f'github: {github_url}')

    new_frontmatter.append('---')
    return '\n'.join(new_frontmatter) + '\n' + body


def convert_wikilinks(content):
    """Obsidian wikilink를 마크다운 링크로 변환"""
    # [[파일|별칭]] → [별칭](/portfolio/intel/파일)
    def replace_wikilink_with_alias(match):
        parts = match.group(1).split('|')
        filename = parts[0].strip()
        alias = parts[1].strip() if len(parts) > 1 else filename

        # 경로 변환
        if filename in ['Intel_Portfolio', 'Mini Project Portfolio', 'Project Portfolio']:
            category = filename.replace(' Portfolio', '').lower()
            path = f'/portfolio/{category}'
        else:
            path = f'/portfolio/intel/{slugify(filename)}'

        return f'[{alias}]({path})'

    # [[파일명]] (별칭 없음)
    def replace_plain_wikilink(match):
        filename = match.group(1).strip()
        if filename in ['Intel_Portfolio', 'Mini Project Portfolio', 'Project Portfolio']:
            category = filename.replace(' Portfolio', '').lower()
            path = f'/portfolio/{category}'
        else:
            path = f'/portfolio/intel/{slugify(filename)}'
        return f'[{filename}]({path})'

    # 별칭 있는 wikilink 먼저 처리
    content = re.sub(r'\[\[([^\]]+\|[^\]]+)\]\]', replace_wikilink_with_alias, content)
    # 별칭 없는 wikilink 처리
    content = re.sub(r'\[\[([^\]]+)\]\]', replace_plain_wikilink, content)

    return content


def convert_image_wikilinks(content):
    """![[파일명]] → ![](경로)"""
    def replace_image(match):
        filename = match.group(1)
        # Pasted image는 assets/portfolio/로
        if filename.startswith('Pasted image'):
            path = f'../../assets/portfolio/{filename}'
        else:
            path = f'../../assets/portfolio/{filename}'
        return f'![{filename}]({path})'

    content = re.sub(r'!\[\[([^\]]+)\]\]', replace_image, content)
    return content


def convert_obsidian_callouts(content):
    """Obsidian Callout > [!type] 내용 → blockquote로 변환"""
    # Callout을 blockquote로 변환
    # > [!abstract] 내용 → > **내용**
    # > [!success] 내용 → > **내용**
    # 등등...

    def replace_callout(match):
        callout_type = match.group(1)  # abstract, success, info, tip 등
        content = match.group(2)
        return f'> {content}'

    content = re.sub(r'> \[!(\w+)\]\s*(.*?)(?=\n(?:>|#|$))', replace_callout, content, flags=re.MULTILINE | re.DOTALL)
    return content


def slugify(text):
    """텍스트를 URL slug로 변환"""
    # 한글 제거, 공백 → 하이픈, 소문자로
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # 영숫자, 공백, 하이픈만 유지
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def generate_frontmatter(filename, file_path):
    """인덱스 파일용 frontmatter 생성"""
    today = datetime.now().strftime('%Y-%m-%d')

    type_map = {
        'Intel_Portfolio.md': 'intel',
        'Mini Project Portfolio.md': 'mini',
        'Project Portfolio.md': 'career',
        '★Introduce.md': 'intro',
    }

    category = type_map.get(filename, 'unknown')

    if filename == '★Introduce.md':
        return f"""---
title: Ziro's Portfolio
description: AI/SW Engineer Portfolio Archive
pubDate: {today}
---
"""
    elif category == 'intel':
        return f"""---
title: Intel AI SW Academy Projects
description: AI/데이터 분석 프로젝트
type: intel
pubDate: {today}
---
"""
    elif category == 'mini':
        return f"""---
title: Mini & Personal Projects
description: 개인 역량 강화 토이 프로젝트
type: mini
pubDate: {today}
---
"""
    elif category == 'career':
        return f"""---
title: Career Projects
description: 실무 프로젝트 경력
type: career
pubDate: {today}
---
"""
    return ""


def process_file(source_path, dest_path, is_index=False):
    """파일 변환 및 저장"""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 변환 작업
    if not is_index:
        # 상세 파일: frontmatter 변환
        content = convert_frontmatter(content)
        # title이 없으면 추가
        if 'title:' not in content:
            # frontmatter 끝에 추가
            parts = content.split('---', 2)
            if len(parts) >= 2:
                filename = Path(source_path).stem
                title = filename
                frontmatter = parts[1] + f'\ntitle: {title}\n'
                content = '---' + frontmatter + '---' + parts[2]
    else:
        # 인덱스 파일: frontmatter 완전 교체
        filename = Path(source_path).name
        fm = generate_frontmatter(filename, source_path)
        # 기존 frontmatter 제거
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = fm + parts[2]
            else:
                content = fm + content
        else:
            content = fm + content

    # 공통 변환
    content = convert_wikilinks(content)
    content = convert_image_wikilinks(content)
    content = convert_obsidian_callouts(content)

    # 저장
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✓ {dest_path.name}')


def migrate_portfolio():
    """포트폴리오 마이그레이션 실행"""
    blog_root = Path('/Users/ziro/Ziro-kun.github.io')
    obsidian_root = Path('/Users/ziro/ziro_obs/Portfolio')
    dest_root = blog_root / 'src/content/portfolio'

    # Intel 프로젝트 (상세 문서)
    intel_docs = obsidian_root / 'Intel_Portfolio/문서들'
    for md_file in intel_docs.glob('*.md'):
        dest = dest_root / 'intel' / slugify(md_file.stem) / 'index.md'
        process_file(md_file, dest, is_index=False)

    # 인덱스 파일들
    index_files = {
        '★Introduce.md': dest_root / 'index.md',
        'Intel_Portfolio.md': dest_root / 'intel/index.md',
        'Mini Project Portfolio.md': dest_root / 'mini/index.md',
        'Project Portfolio.md': dest_root / 'career/index.md',
    }

    for src_name, dest_path in index_files.items():
        src_path = obsidian_root / src_name
        if src_path.exists():
            process_file(src_path, dest_path, is_index=True)


if __name__ == '__main__':
    migrate_portfolio()
    print('\n✅ 마이그레이션 완료!')
