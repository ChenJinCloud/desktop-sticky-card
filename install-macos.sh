#!/bin/bash
set -euo pipefail

if [ "$(uname -s)" != Darwin ]; then
    printf '%s\n' 'This installer requires macOS.' >&2
    exit 1
fi
install_home="${STICKY_CARD_INSTALL_HOME:-$HOME}"
repository="${STICKY_CARD_REPOSITORY:-https://github.com/ChenJinCloud/desktop-sticky-card.git}"
project="$install_home/.local/share/desktop-sticky-card"
bin="$install_home/.local/bin"
skill="$project/skills/desktop-sticky-card"

command -v git >/dev/null || { printf '%s\n' 'Git is required.' >&2; exit 1; }
if ! xcode-select -p >/dev/null 2>&1; then
    printf '%s\n' 'Install Apple Command Line Tools first: xcode-select --install' >&2
    exit 1
fi
for name in sticky-card sticky-card-start; do
    dest="$bin/$name"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        target="$project/mac/card.sh"
        [ "$name" = sticky-card-start ] && target="$project/mac/start.sh"
        expected="$(printf '#!/bin/bash\n# desktop-sticky-card managed launcher\nexec %q "$@"\n' "$target")"
        if [ -L "$dest" ] || [ ! -f "$dest" ] || [ "$(cat "$dest")" != "$expected" ]; then
            printf 'Refusing to overwrite existing command: %s\n' "$dest" >&2
            exit 1
        fi
    fi
done
for root in .agents .codex .claude .workbuddy; do
    dest="$install_home/$root/skills/desktop-sticky-card"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        if [ ! -L "$dest" ] || [ "$(readlink "$dest")" != "$skill" ]; then
            printf 'Refusing to overwrite existing skill: %s\n' "$dest" >&2
            exit 1
        fi
    fi
done

if [ -e "$project" ]; then
    if [ ! -d "$project/.git" ] || [ "$(git -C "$project" remote get-url origin)" != "$repository" ]; then
        printf 'Installation directory already exists and is not this repository: %s\n' "$project" >&2
        exit 1
    fi
    printf '%s\n' 'Existing installation found; its source and data will be preserved.'
else
    mkdir -p "$(dirname "$project")"
    if [ -n "${STICKY_CARD_REPOSITORY_REF:-}" ]; then
        git clone --quiet --branch "$STICKY_CARD_REPOSITORY_REF" "$repository" "$project"
    else
        git clone --quiet "$repository" "$project"
    fi
fi
if [ ! -f "$skill/SKILL.md" ]; then
    printf '%s\n' 'The checkout does not contain the portable skill. Update it before installing.' >&2
    exit 1
fi
if ! "$project/mac/python-with-tk.sh" -c 'import tkinter' >/dev/null 2>&1; then
    printf '%s\n' 'Python with Tk 8.6+ is required. See mac/README.md; e.g. install Homebrew python-tk@3.14.' >&2
    exit 1
fi


mkdir -p "$bin"
for name in sticky-card sticky-card-start; do
    dest="$bin/$name"
    if [ ! -e "$dest" ]; then
        target="$project/mac/card.sh"
        [ "$name" = sticky-card-start ] && target="$project/mac/start.sh"
        printf '#!/bin/bash\n# desktop-sticky-card managed launcher\nexec %q "$@"\n' "$target" > "$dest"
        chmod 755 "$dest"
    fi
done
for root in .agents .codex .claude .workbuddy; do
    mkdir -p "$install_home/$root/skills"
    dest="$install_home/$root/skills/desktop-sticky-card"
    if [ ! -L "$dest" ]; then ln -s "$skill" "$dest"; fi
done
if [ ! -e "$project/mac/card-content.md" ] && [ ! -L "$project/mac/card-content.md" ]; then
    cp "$project/mac/card-content.example.md" "$project/mac/card-content.md"
fi
printf '\n%s\n' 'Installation complete.' "CLI: $bin/sticky-card --help" "Start the card: $bin/sticky-card-start"
printf '%s\n' 'If ~/.local/bin is not on PATH, use the full paths above. Agent access depends on its local execution permissions.'
