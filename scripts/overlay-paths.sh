#!/usr/bin/env bash
# Public Plugin, Private Overlay resolver (https://github.com/danielrosehill/Public-Plugin-Private-Overlay).
# Finds this plugin's overlay (the user's data folder) and looks up role profiles overlay first.
#
#   overlay-paths.sh              data folder, the rule that picked it, machines.json state
#   overlay-paths.sh dir          data folder only
#   overlay-paths.sh templates    every role profile, overlay first: <name>\t<user|builtin>\t<path>
#   overlay-paths.sh template N   path of role profile N (user copy wins), exit 1 if none
#
# Resolution order (first match wins):
#   1. $BIOS_TUNING_HOME
#   2. $CLAUDE_USER_DATA/bios-tuning
#   3. ~/.claude-user-data/bios-tuning                         if ~/.claude-user-data exists
#   4. ${XDG_DATA_HOME:-~/.local/share}/claude-plugins/bios-tuning   if that root exists
#   5. ~/.claude-user-data/bios-tuning                         default
set -euo pipefail

NAME=bios-tuning
HOME_VAR=BIOS_TUNING_HOME
BUILTIN=templates/roles

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
XDG_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins"

if [[ -n "${!HOME_VAR:-}" ]]; then
  DIR="${!HOME_VAR}"; RULE="$HOME_VAR"
elif [[ -n "${CLAUDE_USER_DATA:-}" ]]; then
  DIR="$CLAUDE_USER_DATA/$NAME"; RULE="CLAUDE_USER_DATA"
elif [[ -d "$HOME/.claude-user-data" ]]; then
  DIR="$HOME/.claude-user-data/$NAME"; RULE="existing ~/.claude-user-data"
elif [[ -d "$XDG_ROOT" ]]; then
  DIR="$XDG_ROOT/$NAME"; RULE="existing $XDG_ROOT"
else
  DIR="$HOME/.claude-user-data/$NAME"; RULE="default"
fi

list_templates() {
  declare -A seen=()
  if [[ -d "$DIR/roles" ]]; then
    for f in "$DIR/roles"/*.md; do
      [[ -e "$f" ]] || continue
      b=$(basename "$f"); seen[$b]=1
      printf '%s\tuser\t%s\n' "$b" "$f"
    done
  fi
  for f in "$PLUGIN_ROOT/$BUILTIN"/*.md; do
    [[ -e "$f" ]] || continue
    b=$(basename "$f")
    [[ -n "${seen[$b]:-}" ]] && continue
    printf '%s\tbuiltin\t%s\n' "$b" "$f"
  done
}

case "${1:-}" in
  dir) echo "$DIR" ;;
  templates) list_templates ;;
  template)
    n="${2:?role name}"; [[ "$n" == *.md ]] || n="$n.md"
    if [[ -e "$DIR/roles/$n" ]]; then echo "$DIR/roles/$n"
    elif [[ -e "$PLUGIN_ROOT/$BUILTIN/$n" ]]; then echo "$PLUGIN_ROOT/$BUILTIN/$n"
    else echo "no role profile named '$n'" >&2; exit 1; fi ;;
  "")
    echo "data_dir: $DIR"
    echo "rule: $RULE"
    echo "plugin_root: $PLUGIN_ROOT"
    echo "machines: $([[ -f "$DIR/machines.json" ]] && echo present || echo missing)"
    ;;
  *) echo "usage: $0 [dir|templates|template NAME]" >&2; exit 2 ;;
esac
