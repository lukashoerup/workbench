# Agent roles — who builds, who reviews

Changed: 2026-09-12. Owner: Lukas. Reason: OpenAI usage limits are hit repeatedly, so
Claude takes substantially more of the work and Astra less. This file is the record of the
provider/model assignment; enduring rules stay in `CLAUDE.md` and, on the direction
branch, `docs/WORKBENCH.md`. Until that branch routes its active assignment sentences
here (`docs/workbench-direction.md`, `context/STACK.md`, `docs/claude-project-instructions.md`;
listed in the pilot task's handoff), a swap must also update or mark historical those
sentences. Once routed, a swap is an edit to this table and the Changed line.

| Role | Provider and model | Paid for by | Cadence |
|---|---|---|---|
| Builder | Anthropic, Claude Fable 5.1 (`claude-fable-5-1`) | Claude Max subscription; usage credits off | Research, planning, implementation, tests, docs, routine checks and repairs, review of Codex-built work |
| Reviewer | OpenAI, GPT-6 Astra, via ChatGPT Work or Codex | ChatGPT subscription included usage; near exhaustion on 2026-09-12 | One short review per meaningful acceptance point, not per edit |
| Fallback | none | none authorized | Missing review stays pending, never approval |

Reviewer setup, once, by Lukas: `docs/astra-work-setup.md`. Daily use afterwards: Claude
applies the `astra-review` label; nobody relays anything.

## What the allocation means in practice
- Claude does not wait for Astra to research, plan or prepare routine steps.
- Routine changes are grouped into one PR. Deterministic checks run first: pytest,
  shellcheck, the docs invariants.
- One Astra review is requested at an acceptance point: a PR ready to merge, a changed
  direction, a data-handling change. The request names the exact head revision and asks
  at most three questions.
- Small approved fixes get no Astra review. CI plus builder evidence is the record,
  marked "unreviewed".
- If Astra is unavailable or out of allowance, the review is recorded as pending with an
  owner and a next retry. Lukas may override explicitly. Nothing switches billing or model.

## Hard limits, unchanged by any swap
- No API keys, overage, usage credits or credit purchases for either provider.
- Session links and other account-scoped identifiers stay out of this public repository.
- A written role is not a running integration. What is actually connected is recorded in
  `docs/workflow-rollout.md` on the direction branch and in the pilot task file.

## Swap procedure
1. Edit the table and the Changed line, with the reason.
2. Run the tests; `tests/test_roles.py` checks the table is still complete and unpaid.
3. Until the pointers above are integrated, update the direction-branch sentences too.
4. Commit with the reason. Tell the next session in plain language. Project rules are
   unaffected.
