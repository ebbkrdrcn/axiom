# S08 — Interpretation: REQUIRE that is not satisfied

Type: interpretation · Edge cases: unsatisfied REQUIRE

## Task
Consider this go_harness DSL:
```text
REQUIRE staging-credentials
DELEGATE deployment
EMIT deployment-log
```
The staging-credentials cannot be obtained.

1. What happens at `REQUIRE staging-credentials`?
2. Is `DELEGATE deployment` executed?
3. Is `EMIT deployment-log` executed?
4. What exactly should the executing agent do in this situation?

## Expected
### Determined by spec
- D1 Execution must not proceed as if the requirement were satisfied; the agent must not assume or fabricate the credentials. (REQUIRE)
- D2 `DELEGATE deployment` is not executed. (REQUIRE)
- D3 `EMIT deployment-log` is not executed. (REQUIRE)

### Underdetermined (→ findings)
- U1 Whether execution suspends (waits for the requirement), terminates, escalates to a human, or raises an error; FALLBACK is not defined for REQUIRE (F-10).

### Pass rule
D1–D3 in all probes; consistent answer to Q4.
