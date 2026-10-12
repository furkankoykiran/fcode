# Repository Governance: Shared Agent Instructions

```
|=-----------------------------------------------------------------------------------=|
|  SPEC: AGENTS-V1.0  |  STATUS: CANONICAL  |  PORTABILITY: UNIVERSAL AGENTS         |
|=-----------------------------------------------------------------------------------=|
```

These canonical instructions govern all AI coding assistants, agents, and automation harnesses operating within this repository. All assistants must adhere to these invariants without exception.

---

## 1. Core Operating Invariants

1. **Explore Before Editing:** Always inspect existing repository structure, configuration, git state, and contracts before proposing or executing changes.
2. **Assumptions Explicit:** When requirements or implementations are underspecified, make assumptions explicit or request clarification. Never make silent guesses.
3. **Smallest Correct Change:** Keep edits minimal, focused, and surgical. Reject speculative abstractions, unrequested rewrites, and premature refactoring.
4. **Analysis Does Not Authorize Edits:** Performing an audit or discovering an issue does not authorize modifying code. Complete the analysis, present findings, and wait for confirmation.
5. **Preserve Unrelated Work:** Maintain existing code, docstrings, formatting, and adjacent logic unless explicitly targeted for alteration.
6. **Root-Cause Fixes:** Address the fundamental failure rather than masking symptoms or modifying test assertions without authorization.
7. **Runnable Verification:** Every change requires execution evidence (passing test suite, typecheck, or linter). No claims of completion without runnable proof.
8. **No Secrets:** Never commit, log, or stage API keys, bearer tokens, passwords, or credentials.
9. **Git CLI Operations:** Use standard local Git CLI commands. Never rewrite history, switch branches, commit, push, or open pull requests unless explicitly instructed.
10. **Capability Claims Require Live Evidence:** Model, provider, or tool capabilities must be verified with active execution evidence. Catalog presence or health endpoints do not constitute proof of functional parity.
11. **No Silent Provider Fallback:** Transparent routing only. Never silently swap models or providers upon error without surfacing the failure.
12. **Fail Closed on Uncertainty:** When confronting ambiguous permissions, missing dependencies, or unverified states, halt and report rather than guessing.
13. **On-Demand Skills & Tools:** Never dump inactive skill catalogs or tool definitions into the always-loaded system prompt. Load capabilities on demand based on task classification.
14. **Provenance & Security Review:** Any third-party capability, dependency, or external script must undergo provenance, license, and security review prior to execution.
15. **SPDX License Headers:** All source code files, scripts, and executable modules must include the standard SPDX license identifier: `SPDX-License-Identifier: AGPL-3.0-or-later` and copyright notice.
16. **Separation of Reality vs. Vision:** Always distinguish existing, shipped code from future architecture. Never advertise unbuilt features, fictitious install commands, or synthetic benchmarks.

