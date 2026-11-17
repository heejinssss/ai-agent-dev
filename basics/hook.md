```json
/* .claude/settings.json (hooks 부분) */
"PreToolUse": [{ "matcher": "Bash|Write|Edit",
  "hooks": [{ "type": "command", "command": "python3 .claude/hooks/guard.py" }] }]
```

```python
# .claude/hooks/guard.py
import json, sys
e = json.load(sys.stdin)            # 도구 이름 · 입력
i = e.get('tool_input', {})
bad = ['rm -rf', 'push --force', 'reset --hard']
if any(b in i.get('command', '') for b in bad) \
   or i.get('file_path', '').endswith('.env'):
    print('차단: 위험 명령 · 비밀 파일', file=sys.stderr)
    sys.exit(2)                     # 2 = 막고 이유를 Claude에게
```