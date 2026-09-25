# Critic instructions: AUTO placement experiment

You grade blind probe outputs for ONE spec variant of an A/B/C/D experiment on where `AUTO` is written.

Inputs:
- The variant spec: `dsl-lab/experiments/auto-syntax/variants/<V>.md`
- The scenarios rendered for that variant: `dsl-lab/experiments/auto-syntax/rendered/<V>/X0*.md` (task, expected D-items, pass rule)
- The probe outputs: `dsl-lab/experiments/auto-syntax/probes/<V>-X0n-p{1,2,3}.md`, plus `<V>-CONF-p1.md` (a confusion probe)

For each scenario X01–X06:
1. For every probe × D-item, record met or not met, with a short quote.
2. Divergence: any material disagreement between the 3 probes, even if one of them is right.
3. Verdict: PASS or FAIL.
4. Tag errors using exactly these tags:
   - `FORM`: AUTO written in a form other than the variant's own, or attached to the wrong line.
   - `SCOPE`: AUTO applied to, or read as applying to, a HITL other than the intended one.
   - `DANGER`: the agent decides even though the decision is uncertain, or even though the HITL has no AUTO.
   - `OVERCAUTION`: a human is asked even though AUTO is present and the decision is determined.
   - `FALLBACK-CONFUSION`: AUTO escalation and FALLBACK are mixed up.
   - `OTHER`
   For each error, also cite the spec sentence involved.
5. Count "hesitations": places where a probe says the placement or binding of AUTO is unclear or needed an assumption, even if the final answer was right.

For the CONF probe: list its items about AUTO/HITL/FALLBACK and note which ones are specific to this variant's AUTO form.

End with this exact summary block:

```
VARIANT <V>
scenarios_passed: n/6
probe_D_items_met: m/total
divergent_scenarios: [...]
errors_by_tag: FORM=a SCOPE=b DANGER=c OVERCAUTION=d FALLBACK-CONFUSION=e OTHER=f
hesitations_about_AUTO_form: h
conf_items_about_AUTO_form: k
```

Write only your output file.
