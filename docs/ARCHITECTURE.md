# Architecture Thesis

```
|=-----------------------------------------------------------------------------------=|
|  DOC: ARCHITECTURE-V1.0  |  STATUS: WORKING SPEC  |  PROVENANCE: fcode CORE        |
|=-----------------------------------------------------------------------------------=|
```

---

## 1. System Overview

`fcode` is structured as a decoupled, multi-tier autonomous software engineering harness. It transforms raw human intent into verified software changes by separating **intent synthesis**, **capability orchestration**, **isolated execution**, and **deterministic verification**.

```
+-----------------------------------------------------------------------------------+
|                                  DEVELOPER INTENT                                 |
|                     ("Refactor auth session store to use Redis")                   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        TIER 1: AUTOMATIC PROMPT SYNTHESIZER                       |
|                                                                                   |
|   +-----------------------+   +----------------------+   +--------------------+   |
|   |   Repository Probe    |   | Ambiguity Detector   |   | Spec & Plan        |   |
|   |   (AST, git, config)  |-->| (Detect unstated     |-->| Compiler           |   |
|   |                       |   |  assumptions/drift)  |   | (Formal task tree) |   |
|   +-----------------------+   +----------------------+   +--------------------+   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     TIER 2: CAPABILITY & ORCHESTRATION ENGINE                     |
|                                                                                   |
|   +-----------------------+   +----------------------+   +--------------------+   |
|   | Model Router          |   | On-Demand Skill Hub  |   | MCP Server Bridge  |   |
|   | (Reasoning vs Worker) |   | (Dynamic loading)    |   | (Sandboxed stdio)  |   |
|   +-----------------------+   +----------------------+   +--------------------+   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     TIER 3: HIGH-PERFORMANCE NATIVE HARNESS                       |
|                             (Native Execution & Swarms)                           |
|                                                                                   |
|   +-----------------------+   +----------------------+   +--------------------+   |
|   | Isolated Git          |   | Server-Side File     |   | Sub-20ms Terminal  |   |
|   | Worktree Runners      |   | Conflict Monitor     |   | Stream & UI        |   |
|   +-----------------------+   +----------------------+   +--------------------+   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     TIER 4: VERIFICATION & CONVERGENCE LOOP                       |
|                                                                                   |
|   +-----------------------+   +----------------------+   +--------------------+   |
|   | Test & Linter Runner  |   | Typecheck / Compiler |   | Atomic Git Diff    |   |
|   | (Automated execution) |-->| Verification         |-->| Convergence Audit  |   |
|   +-----------------------+   +----------------------+   +--------------------+   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                           VERIFIED SOFTWARE CHANGE                                |
|                        (Clean diff ready for approval)                            |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### Subsystem 1: Automatic Prompt Synthesizer
The Prompt Synthesizer solves the fundamental bottleneck in coding agents: prompt ambiguity and lack of grounding.
1. **Repository Probe:** Reads repository manifests, git status, tree-sitter AST symbol definitions, and architecture rules (`AGENTS.md`) without dumping file contents into context.
2. **Ambiguity Detector:** Compares user prompt against codebase realities. Identifies underspecified requirements (e.g., edge cases, error handling, backward compatibility). If uncertainty exceeds a threshold, it surfaces structured clarification prompts before code changes start.
3. **Spec Compiler:** Converts validated intent into an internal execution specification, breaking tasks into an ordered dependency tree of atomic micro-changes.
4. **Orchestrator:** Assigns optimal model roles (e.g., high-reasoning model for architectural planning, fast coding model for code emission) and loads only relevant Skills and MCP tools.

### Subsystem 2: Capability and Extension Registry
To prevent prompt context bloat and maintain security boundaries:
1. **On-Demand Loading:** Skills, MCP tools, and subagents are never dumped into the always-loaded system prompt. They are indexed in an ephemeral catalog and loaded dynamically only when the task spec requires them.
2. **Provenance and Security Verification:** Every external tool, hook, and skill package must declare its source provenance, license, and required permissions (read, write, network, shell).
3. **Fail-Closed Execution:** If a capability cannot be verified or its permissions are ambiguous, the harness fails closed and requests explicit operator authorization.

### Subsystem 3: Native Execution Harness
1. **Sub-15ms Startup (Rust Native Core):** Single static binary compiled in Rust delivering instant startup without runtime interpreter or Electron overhead.
2. **Isolated Worktrees:** Multi-agent swarms execute in isolated git worktrees (`git worktree add`), allowing multiple hypotheses or parallel tasks to run without dirtying the working directory.
3. **Server-Side Conflict Monitoring:** Active daemon monitors filesystem watch events (`inotify`/`kqueue`). If two concurrent workers touch overlapping files, execution pauses immediately to resolve stale diffs.
4. **Universal Provider Abstraction:** First-class support for OpenAI, Anthropic, Gemini, OpenRouter, and local OpenAI-compatible endpoints (Ollama, vLLM, LM Studio) without proxy hacks.

### Subsystem 4: Verification & Convergence Engine
1. **Zero Unverified Edits:** Code generation is strictly provisional until verified against the repository's native test suites, typecheckers, and linters.
2. **Root-Cause Convergence:** If a verification test fails, the error output is fed back into the worker agent with the original spec. The agent must solve the root cause rather than patching symptoms or modifying test assertions without authorization.
3. **Atomic Reversibility:** If convergence cannot be achieved within a bounded cycle limit, changes in the isolated worktree are discarded cleanly.

---

## 3. State Machine & Execution Lifecycle

```
    [IDLE]
       |  (User Intent Input)
       v
[PROMPT SYNTHESIS] <----> [AMBIGUITY RESOLUTION] (If user clarification needed)
       |
       v (Executable Spec Produced)
[ORCHESTRATION & ROUTING] (Select Models, Skills, MCPs)
       |
       v
[WORKTREE ISOLATION] (Spawn worker in clean sandbox / worktree)
       |
       v
[CODE EXECUTION] <-----> [LSP / AST QUERY]
       |
       v (File changes applied)
[CONFLICT CHECK] ------> (Conflict Detected: Rebase / Resynchronize)
       | (Clean)
       v
[RUNNABLE VERIFICATION] (Run tests, linters, types)
       |
       +--- [FAILED] ---> (Iterate Root-Cause Fix, max N attempts)
       |
       v [PASSED]
[HUMAN REVIEW PACKAGE] (Present atomic diff, verification proof, and logs)
```

---

## 4. Architectural Invariants

* **Contract Over Concurrency:** No agent may write to the primary repository working tree without producing a passing verification report from its isolated worktree.
* **Context Budgeting:** Never exceed 40% of the active context window with static tool schemas or repository file dumps. Leverage tree-sitter indexing, LSP symbol queries, and on-demand skill imports.
* **No Silent Fallback:** If a model provider returns an error, rate limit, or degraded response, the error must be surfaced explicitly. Silent switching between dissimilar models without operator consent is prohibited.
* **Local-First Authority:** The local Git repository and local filesystem remain the sole source of truth. Remote caches and model responses are transient.

