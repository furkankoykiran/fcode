# Architecture Decisions and Non-Goals

```
|=-----------------------------------------------------------------------------------=|
|  DOC: DECISIONS-V1.1  |  STATUS: CANONICAL  |  PROVENANCE: fcode CORE              |
|=-----------------------------------------------------------------------------------=|
```

---

## 1. Resolved Architecture Decisions

All core architectural decisions for Phase 0 and subsequent implementation phases are resolved. No items remain deferred or unassigned.

### Decision 1: Runtime Implementation Language
* **Adopted:** Rust for the future native core.
* **Rationale:** Rust delivers sub-15ms cold start times, minimal memory consumption under concurrent agent workloads, and a single self-contained static binary. Its compile-time memory safety prevents data races across concurrent multi-worker swarms without runtime garbage collection pauses.

### Decision 2: Interface Architecture
* **Adopted:** Terminal-first architecture.
* **Rationale:** Direct command-line ergonomics, fast keyboard navigation, Unix composability, and headless scriptability (`fcode exec` for automated CI/CD pipelines). Avoids heavy web wrappers and desktop UI overhead.

### Decision 3: Provider and Model Routing
* **Adopted:** Provider-neutral model routing.
* **Rationale:** Native streaming integration across leading proprietary models, open-weights services, and local endpoints (such as Ollama and vLLM). No proprietary vendor lock-in and no silent provider fallbacks.

### Decision 4: Capability and Extension Loading
* **Adopted:** On-demand Skills, Model Context Protocol (MCP), and plugin capability loading.
* **Rationale:** Dynamic loading based on task classification. Prevents context window bloat and token exhaustion, enforces granular permission boundaries, and implements fail-closed authorization.

### Decision 5: Autonomous Execution and Verification
* **Adopted:** Verification-first autonomous execution.
* **Rationale:** Code edits inside isolated ephemeral git worktrees remain provisional until test suites, linters, and typecheckers execute and pass. Human review packages require concrete execution evidence.

### Decision 6: Documentation and Wiki Frontend
* **Adopted:** Starlight as the future documentation and wiki frontend, with Markdown as the portable source content.
* **Rationale:** High-performance static site generation, accessible technical documentation ergonomics, and zero-config search. Source files remain portable GitHub-Flavored Markdown in `docs/` and root documentation.

### Decision 7: Repository Licensing
* **Adopted:** GNU AGPL-3.0-or-later for fcode source code.
* **Rationale:** Strong copyleft protects developer agency, guarantees network transparency for agentic software services, and prevents closed-source hoarding of core developer tooling.

---

## 2. Explicit Non-Goals

To maintain sharp engineering focus, `fcode` defines what it will not do:

1. **Not a Single-Vendor Wrapper:**
   `fcode` will not be tied exclusively to any single model vendor. It routes flexibly across multiple providers and local servers.

2. **Not a Heavy Desktop Electron GUI:**
   `fcode` will not distribute a 300MB Chromium shell. It is built terminal-native first, fast, and resource-conscious.

3. **Not "Vibe Coding" Without Verification:**
   `fcode` rejects speculative generation where an assistant makes unchecked edits and leaves verification to the user. Every proposed code change requires passing test, lint, or typecheck execution evidence.

4. **Not a Context Stuffer:**
   `fcode` will not inject dozens of static tool schemas and unneeded files into the active context window. Inactive capabilities remain indexed on disk and load dynamically on demand.

5. **Not Synthetic Marketing Theater:**
   `fcode` will never publish synthetic benchmark claims, unverified performance graphs, or misleading marketing assertions. Product claims must be reproducible by running standard test commands.
