---
paths:
  - "scripts/**"
  - "src/**"
  - "tests/**"
---

# Source Code Licensing and SPDX Invariant

All source code files, scripts, and executable modules within `fcode` must include canonical SPDX license headers.

## Standard Header Formats

### Rust, C, JavaScript, TypeScript
```rust
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 Furkan Köykıran
```

### Python, Shell, Bash, YAML
```python
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Furkan Köykıran
```

## Governance Invariants

1. **Mandatory Header:** Every new source file added to the repository must begin with the SPDX identifier and copyright notice.
2. **License Compatibility:** All contributions fall under GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later).
3. **No Proprietary Markers:** Reject third-party proprietary notices or conflicting permissive licenses that erode copyleft protections without authorization.
