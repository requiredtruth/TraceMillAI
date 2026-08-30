# TraceMillAI

TraceMillAI reduces a failing JSONL agent execution trace to the smallest sequence its replay predicate still recognizes as failure. It implements cached delta debugging over whole events and produces replayable JSONL plus factual run counts.

```bash
python -m tracemillai trace.jsonl --out minimized.jsonl -- python reproduce.py '{trace}'
```

The predicate is an executable contract: nonzero means failure by default, or select an exact code with `--failing-code`. TraceMillAI proves the original fails, removes chunks, increases granularity, caches identical candidates, and stops at `--max-runs`.

## Honest boundary

The tool executes the predicate command with your current user permissions; it is not a sandbox. Delta debugging finds a 1-minimal sequence under its removal strategy, not a proven global minimum when failures are flaky or order-dependent.

## Test

`python -m unittest discover -s tests -v`

## Fund more development

Donations increase RequiredTruth development production. See [SUPPORT.md](SUPPORT.md); confirmed donors may claim a transaction hash in an issue and request a specific direction.

Apache-2.0 licensed.


## Install and run

```sh
chmod +x install.sh run.sh
./install.sh
./run.sh --help
```


## Standard launcher

`./run.sh` is the normal entry point. It runs `./install.sh` automatically when setup is missing, then opens the PySide6 control panel with live output and actions for trace minimization, the demo, tests, repair, and stop. Leave the argument field blank for a deterministic bundled failure-reduction demo; it writes only to temporary storage and removes that storage afterward. Enter `TRACE.jsonl [options] -- PREDICATE` to analyze another trace. The GUI test action runs compilation and the real unit suite through `./test.sh`. Use `./cli.sh` for CLI-only operation.
