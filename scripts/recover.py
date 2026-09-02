import json
import urllib.parse
import re
import os

transcript_path = r'C:\Users\Admin\.gemini\antigravity\brain\4536e477-ff4b-4cf5-bba0-4ba9e704ae60\.system_generated\logs\transcript_full.jsonl'
files = {}

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'Showing lines' in line:
            try:
                data = json.loads(line)
                content = data.get('content', '')
                if 'file:///' in content:
                    raw_path = content.split('file:///')[1].split('\x60')[0]
                    path = urllib.parse.unquote(raw_path).replace('/', '\\\\')
                    
                    code_lines = []
                    in_code = False
                    for l in content.split('\n'):
                        if 'The following code has been modified' in l:
                            in_code = True
                            continue
                        if in_code:
                            if 'The above content shows' in l or 'The above content does NOT' in l:
                                in_code = False
                                continue
                            m = re.match(r'^\d+:\s(.*)$', l)
                            if m:
                                code_lines.append(m.group(1))
                            elif re.match(r'^\d+:$', l):
                                code_lines.append('')
                    
                    if code_lines:
                        # Append if not first chunk, else replace
                        if path not in files:
                            files[path] = code_lines
                        else:
                            files[path].extend(code_lines)
            except Exception as e:
                print('Error:', e)

for path, code_lines in files.items():
    if path.endswith('.py') or path.endswith('.md'):
        with open(path, 'w', encoding='utf-8') as out_f:
            out_f.write('\n'.join(code_lines) + '\n')
        print('Recovered', path)
