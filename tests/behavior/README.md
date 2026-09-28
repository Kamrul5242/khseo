# Behavior tests: offline contract vs live agent

KHSEO is mostly an **instruction contract** for an AI agent. That behavior is tested in two
different ways, and they prove different things.

| | Offline contract tests | Live agent-behavior tests |
|---|---|---|
| Command | `python tests/run_tests.py` | `python tests/behavior/run_live.py --cmd "<agent command>"` |
| Runs in CI | **Yes**, every push and PR | **No**, run manually |
| Calls an LLM | **No** | **Yes** (costs model calls) |
| Deterministic | Yes | No: model, host and prompt all vary |
| Proves | every scenario is **governed by real spec text**: each `spec` anchor must exist verbatim in the rules, commands or workflows, so a rule can't be silently weakened or deleted; the patterns are valid, and the checker catches known-bad replies | a specific host + model + installed KHSEO **actually behaves** as the scenario expects (asks approval, refuses to copy content, doesn't invent numbers…) |
| Doesn't prove | that any model obeys the rules | that other models, hosts or versions will behave the same |

So a green CI badge means **the contract is intact**, not that "the AI passed".

## Scenarios

[scenarios.json](scenarios.json) holds each scenario's `request`, the `context` given to the
agent, `spec` anchors (file + exact phrase) and `expect` regexes (`must` / `must_not`,
case-insensitive).

## Running the live tests

The agent must already have KHSEO loaded (e.g. installed as a skill). The command must read a
prompt on stdin and print the reply:

```bash
python tests/behavior/run_live.py --cmd "claude -p"
python tests/behavior/run_live.py --cmd "claude -p" --only approval_required_r3,guarantee_top3
```

Record the date, host, model and KHSEO version (`VERSION`) with the results. Recommended
before any release that changes governance (see [RELEASING.md](../../RELEASING.md)).

## Adding a scenario

1. Write the rule in the spec first (rules/, commands.md or workflows/).
2. Add the scenario with a `spec` anchor quoting that rule verbatim.
3. `python tests/run_tests.py` must pass. If it fails, the anchor doesn't match the spec.
