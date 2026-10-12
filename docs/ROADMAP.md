# Phased Product Roadmap & Actionable TODOs

```
|=-----------------------------------------------------------------------------------=|
|  DOC: ROADMAP-V1.0  |  STATUS: WORKING PLAN  |  PROVENANCE: fcode CORE             |
|=-----------------------------------------------------------------------------------=|
```

---

## Phase Overview

```
+-----------------------------------------------------------------------------------+
| [PHASE 0: FOUNDATION]                                          STATUS: IN PROGRESS|
| Identity, Governance, Research Survey, and Repository Foundation                  |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| [PHASE 1: NATIVE HARNESS CORE]                                  STATUS: PLANNED  |
| Provider Routing, Primitive Tools, Streaming CLI, and Sandbox Boundaries          |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| [PHASE 2: PROMPT SYNTHESIZER & CAPABILITIES]                     STATUS: PLANNED  |
| Intent Analysis, Spec-Driven Compiler, On-Demand Skills & MCP Integration         |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| [PHASE 3: CONCURRENT SWARMS & VERIFICATION]                      STATUS: PLANNED  |
| Git Worktree Isolation, Conflict Daemon, Automated Test Convergence Loops         |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
| [PHASE 4: DEVELOPER PREVIEW & HARDENING]                         STATUS: PLANNED  |
| Headless CI Execution (`fcode exec`), Artifact Reviews, Community Dogfooding      |
+-----------------------------------------------------------------------------------+
```

---

## Detailed Phase Breakdown

### Phase 0: Foundation, Identity & Governance *(Current Milestone)*
- [x] **Architecture and Foundation Specifications:** Author canonical docs (`docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/DECISIONS_AND_NON_GOALS.md`, `DESIGN.md`).
- [x] **Agent Governance Architecture:** Author canonical portable `AGENTS.md`, thin `CLAUDE.md`, scoped `.claude/rules/`, and `.gitignore` safety for `CLAUDE.local.md`.
- [x] **Repository Licensing:** Adopt canonical GNU AGPL-3.0-or-later in root `LICENSE`.
- [x] **Brand Kit & Mascot:** Author canonical master vector mark (`[f/]`), original mascot (`syn`), frozen vector wordmark outlines, automated generator script, and verification test suite.
- [ ] **Human Review & Approval:** Present complete uncommitted working tree for review.

### Phase 1: Native Harness Core & Universal Providers
- [ ] **Native Core in Rust:** Implement core engine in Rust (sub-15ms cold boot, single static binary, safe memory concurrency).
- [ ] **Universal Provider Layer:** Implement direct streaming API clients for:
  - Anthropic Messages API
  - OpenAI Chat Completions / Responses API
  - Google Gemini API
  - OpenRouter API
  - Local OpenAI-compatible endpoints (Ollama, vLLM, LM Studio)
- [ ] **Primitive Tool Execution Engine:** Implement minimal, high-discipline tools (`read_file`, `write_file`, `edit_file`, `run_command`) with strict output budgeting and truncation protection.
- [ ] **Basic Terminal Streaming Interface:** Keyboard-driven terminal output with sub-20ms feedback, TrueColor rendering, and clean ANSI degradation.
- [ ] **Process Execution Sandbox:** OS-level command execution with approval tiers (suggest-only, interactive confirmation, sandboxed auto-exec).

### Phase 2: Prompt Synthesizer & Capability Hub
- [ ] **Intent Ingestion & Ambiguity Engine:**
  - Build repository AST indexer using Tree-Sitter.
  - Implement heuristic ambiguity detector to surface underspecified requirements before code generation.
  - Interactive clarification prompt modal for user intent alignment.
- [ ] **Spec Compiler:** Generate structured internal task trees (`spec.md` & `tasks.md` format) from synthesized intent.
- [ ] **On-Demand Skill Hub:**
  - Implement on-demand skill loader (`fcode skills add / list / invoke`).
  - Strict context budgeting: inject skills into active prompt only during relevant tasks.
- [ ] **MCP Protocol Integration:** Support `stdio` and `sse` Model Context Protocol servers with permission boundaries.

### Phase 3: Concurrent Swarms & Verification Loops
- [ ] **Git Worktree Isolation:**
  - Implement automated ephemeral worktree provisioning (`fcode worktree spawn <task-id>`).
  - Isolate speculative changes from the primary branch.
- [ ] **Server-Side Conflict Monitor Daemon:**
  - Filesystem watch daemon (`inotify` / `kqueue`) to track concurrent agent edits.
  - Early collision detection to prevent stale diff overwrites.
- [ ] **Verification & Convergence Engine:**
  - Automatic test, typecheck, and lint runner integration.
  - Iterative root-cause repair loop (feeding test failures back to the worker model).
  - Bounded convergence limits to prevent endless retry loops.

### Phase 4: Developer Preview & Ecosystem
- [ ] **Headless Scriptable CLI (`fcode exec`):** Support non-interactive execution for CI/CD pipelines and automated PR generation.
- [ ] **Review Artifact Generator:** Automated generation of human review packages (diffs, test outputs, execution transcripts).
- [ ] **Skill Crystallization:** Generalize successful multi-step task completions into reusable project-specific skills.
- [ ] **Public Dogfooding & Installer:** Multi-platform installation scripts (`curl | sh`, Homebrew tap, binary releases) and comprehensive developer documentation.
- [ ] **Documentation Frontend:** Deploy Starlight documentation and wiki frontend powered by Markdown source files.

