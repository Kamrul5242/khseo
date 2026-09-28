# Template — Approval, Proposed Change, Assumption, Readiness

**Approval request (R3/R4)**
```text
KHSEO APPROVAL REQUIRED
Proposed action:  [exact action]
Reason:           [why]
Affected:         [files / pages / routes / systems]
Priority / Risk:  [P? / R?]
Backup:           [Available — id | Not available]
Rollback:         [Available | Limited | Not available]
Expected result:  [result]
Approve? (yes / no / modify scope)
```

**Proposed change (R2 review)**
```text
PROPOSED CHANGE
Change / Why / Affected / Risk / Expected impact / Validation
```

**Assumption**
```text
ASSUMPTION  [what]   REASON  [why]   IMPACT  [what depends on it]   CONFIDENCE  [high/medium/low]
```

**Conflict**
```text
Verified:        [established]
Conflicting:     [source A says X] / [source B says Y]
KHSEO assessment:[evidence-based interpretation]
Recommended:     [action]
```

**Capability handshake** (mandatory before tool-dependent work; see SKILL.md §2)
```text
KHSEO CAPABILITY CHECK
Web fetch:          AVAILABLE | UNAVAILABLE
Browser / JS render: AVAILABLE | UNAVAILABLE
Terminal / code:    AVAILABLE | UNAVAILABLE
Filesystem read:    AVAILABLE | UNAVAILABLE
Write access:       AVAILABLE | READ-ONLY
Git:                AVAILABLE | UNAVAILABLE
Search:             AVAILABLE | UNAVAILABLE
Deployment:         UNAVAILABLE unless the host grants it AND the user approves (separate gate)
Consequence:        [e.g. "No browser → JavaScript rendering: NOT TESTED"]
```
Machine form: [schemas/capabilities.schema.json](../schemas/capabilities.schema.json).
