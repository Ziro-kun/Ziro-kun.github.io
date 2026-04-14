import os
import re

directory = 'src/content/blog'
fixed_count = 0

for filename in os.listdir(directory):
    if filename.endswith('.md') or filename.endswith('.mdx'):
        path = os.path.join(directory, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not match:
                continue
                
            frontmatter = match.group(1)
            lines = frontmatter.split('\n')
            modified = False
            
            for i, line in enumerate(lines):
                if line.startswith('title:') or line.startswith('description:'):
                    parts = line.split(':', 1)
                    if len(parts) < 2: continue
                    
                    key = parts[0]
                    value = parts[1].strip()
                    
                    # Check for problematic double quotes nesting
                    # If it's wrapped in double quotes and contains internal double quotes
                    if value.startswith('"') and value.endswith('"'):
                        inner = value[1:-1]
                        if '"' in inner:
                            # Switch to single quote wrapping
                            # YAML escapes ' by doubling it: ''
                            escaped_inner = inner.replace("'", "''")
                            lines[i] = f"{key}: '{escaped_inner}'"
                            modified = True
                            print(f"  Fixed {key} in {filename}")
            
            if modified:
                new_frontmatter = '\n'.join(lines)
                # Replace only the first occurrence (the frontmatter)
                new_content = content.replace(frontmatter, new_frontmatter, 1)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"\nFinished! Total files fixed: {fixed_count}")
