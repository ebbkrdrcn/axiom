#!/usr/bin/env bash
# Build blind probe inputs: each file = current DSL spec + one task, nothing else.
# usage: tools/build_probes.sh <iteration NN> <outdir>
set -euo pipefail
NN=$1; OUT=$2; LAB=$(cd "$(dirname "$0")/.." && pwd)
SPEC="$LAB/iterations/$NN/DSL.md"
mkdir -p "$OUT/in" "$OUT/out"
header() {
  cat <<'H'
You are given the complete specification of a small process DSL and one task.
Use ONLY the specification below. Where the specification does not determine
something you need, say so explicitly and state what you assumed.

<specification>
H
  cat "$SPEC"
  printf '\n</specification>\n\n<task>\n'
}
for f in "$LAB"/scenarios/*.md; do
  id=$(basename "$f" .md | cut -d- -f1)
  { header; awk '/^## Task/{on=1;next} /^## Expected/{on=0} on' "$f"; printf '</task>\n'; } > "$OUT/in/$id.md"
done
{ header; cat <<'T'
Read the specification carefully as if you had to write or execute processes
with it. List EVERY place that is unclear, contradictory, or underspecified.
For each item: cite the section heading, quote the relevant text, explain the
problem, and show how two reasonable readers could interpret it differently.
Order items by how likely they are to cause a wrong process or wrong execution.
T
printf '</task>\n'; } > "$OUT/in/CONF.md"
ls "$OUT/in"
