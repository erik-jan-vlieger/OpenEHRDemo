---
description: How to commit and push to Git/GitHub efficiently
---
// turbo-all

## Git Commit & Push Workflow

**CRITICAL**: Git commands (add, commit, push) for repos under ~50MB finish in seconds. NEVER send them to background.

### Rules

1. **Always use `WaitMsBeforeAsync: 10000`** (the maximum) for ALL git commands: `git add`, `git commit`, `git push`, `git status`, `git log`.
2. **Never poll** with `command_status` for git commands — they should complete synchronously.
3. **Combine commands** in a single shell line to minimize round-trips:
   ```bash
   git add -A && git commit -m "message" && git push
   ```
4. **Always set `SafeToAutoRun: false`** for commits and pushes (they mutate state).
5. **Remove lock files first** if a previous git command was terminated mid-execution:
   ```bash
   rm -f .git/index.lock && git add -A && git commit -m "message" && git push
   ```

### Example

```
run_command:
  CommandLine: "rm -f .git/index.lock && git add -A && git commit -m 'feat: description' && git push"
  Cwd: /path/to/repo
  SafeToAutoRun: false
  WaitMsBeforeAsync: 10000
```

### What NOT to do

- ❌ `WaitMsBeforeAsync: 5000` → sends to background, then you're stuck polling
- ❌ Separate `git add`, then `git commit`, then `git push` as three tool calls
- ❌ Using `command_status` to wait for git operations
