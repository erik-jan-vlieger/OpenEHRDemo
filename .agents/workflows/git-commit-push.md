---
description: How to commit and push to Git/GitHub efficiently
---
// turbo-all

## Git Commit & Push Workflow

**CRITICAL**: Git commands finish fast locally. Push can take longer over network. Either way: fire and move on.

### Rules

1. **Combine in één regel** — nooit losse add/commit/push calls:
   ```bash
   git add -A && git commit -m "message" && git push
   ```
2. **`WaitMsBeforeAsync: 8000`** — wacht 8 seconden. Als het klaar is: goed. Als het naar background gaat: ook goed, ga gewoon door.
3. **NOOIT `command_status` aanroepen op git-commando's.** Ze zijn of snel klaar, of ze draaien op de achtergrond en komen goed. Pollen is zinloos en irritant voor de gebruiker.
4. **Verifieer succes via `git log --oneline -1`** in een nieuwe korte run_command als je wil bevestigen dat de commit er is — dat is altijd snel.
5. **`SafeToAutoRun: false`** voor commits en pushes (ze muteren state).
6. **Lock file cleanup als nodig**:
   ```bash
   rm -f .git/index.lock && git add -A && git commit -m "message" && git push
   ```

### Aanpak na de run_command

- Als de output `main -> main` of een commit hash toont: ✅ klaar, vertel de gebruiker en ga verder.
- Als het naar background gaat: ✅ ook klaar, ga gewoon verder zonder te wachten of pollen.
- Optioneel: doe ONE snelle `git log --oneline -1` (WaitMsBeforeAsync: 3000, SafeToAutoRun: true) als bevestiging.

### Voorbeeld

```
run_command:
  CommandLine: "rm -f .git/index.lock && git add -A && git commit -m 'feat: description' && git push"
  Cwd: /path/to/repo
  SafeToAutoRun: false
  WaitMsBeforeAsync: 8000
```

Dan eventueel:
```
run_command:
  CommandLine: "git log --oneline -1"
  SafeToAutoRun: true
  WaitMsBeforeAsync: 3000
```

### Wat NIET te doen

- ❌ Na een git-commando `command_status` aanroepen en blijven pollen → dit blokkeert de gebruiker minutenlang
- ❌ Drie losse tool calls voor add, commit, push
- ❌ Wachten tot push "klaar" is — het is vuur-en-vergeet
