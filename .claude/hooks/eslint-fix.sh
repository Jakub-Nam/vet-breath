#!/usr/bin/env bash
# PostToolUse hook — after Claude edits a frontend .ts/.html file, run ESLint --fix on it.
# Auto-fixable problems are repaired silently; anything left over goes to stderr with
# exit 2, which feeds the errors back to Claude so it fixes them in the same turn.
set -u

payload=$(cat)

file=$(printf '%s' "$payload" | node -e '
let s = "";
process.stdin.on("data", (d) => (s += d)).on("end", () => {
  try {
    const j = JSON.parse(s);
    process.stdout.write(j.tool_input?.file_path ?? j.tool_response?.filePath ?? "");
  } catch {
    process.stdout.write("");
  }
});
')

case "$file" in
  *[Ff]rontend*.ts | *[Ff]rontend*.html) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}/frontend" 2>/dev/null || exit 0
[ -x ./node_modules/.bin/eslint ] || exit 0

if ! out=$(./node_modules/.bin/eslint --fix "$file" 2>&1); then
  printf '%s\n' "$out" >&2
  exit 2
fi
exit 0
