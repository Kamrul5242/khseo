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

**Capability check / ready banner** (show only when the user asks what KHSEO can do here)
```text
KHSEO READY
File access: [available/unavailable]   Terminal: [..]   Web fetch: [..]   Browser/JS render: [..]
Git: [..]   Write access: [available/read-only]   Deployment: [unavailable unless granted]
Mode: Universal
```
