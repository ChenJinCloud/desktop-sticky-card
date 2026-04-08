"""
Sticky Card Chat Terminal
Interactive terminal for managing card tasks.
"""

import os
import sys
import re
import subprocess

import cardlib


def show_card():
    lines = cardlib.read_lines()
    if not lines:
        print("  (empty)\n")
        return
    print()
    for line in lines:
        s = line.rstrip()
        if not s:
            print()
        elif re.match(r'^#', s):
            print(f"  {s}")
        elif re.match(r'^[-*]\s*\[x\]', s, re.IGNORECASE):
            text = re.sub(r'^[-*]\s*\[x\]\s*', '', s, flags=re.IGNORECASE)
            print(f"  \u2611 {text}")
        elif re.match(r'^[-*]\s*\[\s?\]', s):
            text = re.sub(r'^[-*]\s*\[\s?\]\s*', '', s)
            print(f"  \u2610 {text}")
        elif re.match(r'^-{3,}$', s):
            print("  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
        else:
            print(f"  {s}")
    print()


def show_tasks_numbered():
    lines = cardlib.read_lines()
    tasks = cardlib.get_tasks(lines)
    if not tasks:
        print("  (no tasks)\n")
        return
    print()
    for idx, (_, done, text) in enumerate(tasks, 1):
        mark = "\u2611" if done else "\u2610"
        print(f"  {idx}. {mark} {text}")
    print()


def show_help():
    print("""
  \u256d\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e
  \u2502  type anything        \u2192 add as task        \u2502
  \u2502  done 1               \u2192 check task #1      \u2502
  \u2502  undo 1               \u2192 uncheck task #1    \u2502
  \u2502  rm 1                 \u2192 delete task #1     \u2502
  \u2502  clear                \u2192 clear done tasks   \u2502
  \u2502  list                 \u2192 numbered task list \u2502
  \u2502  show                 \u2192 full card view     \u2502
  \u2502  title xxx            \u2192 set card title     \u2502
  \u2502  replace xxx          \u2192 replace all content\u2502
  \u2502  edit                 \u2192 open in editor     \u2502
  \u2502  help                 \u2192 this help          \u2502
  \u2502  exit                 \u2192 quit               \u2502
  \u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f
""")


# Command dispatch table: pattern -> handler
COMMANDS = [
    (r'^(?:exit|quit|q|bye|\u9000\u51fa)$',
     lambda m: "EXIT"),
    (r'^(?:help|\?|\uff1f|\u5e2e\u52a9)$',
     lambda m: show_help()),
    (r'^(?:show|card|\u770b\u770b|\u770b|\u5361\u7247)$',
     lambda m: show_card()),
    (r'^(?:list|tasks|ls|\u5217\u8868|\u4efb\u52a1)$',
     lambda m: show_tasks_numbered()),
    (r'^(?:done|\u5b8c\u6210|\u52fe\u9009|\u2713|v)\s*(\d+)$',
     lambda m: _do_toggle(int(m.group(1)), True)),
    (r'^(?:undo|\u6062\u590d|\u53d6\u6d88|\u64a4\u9500)\s*(\d+)$',
     lambda m: _do_toggle(int(m.group(1)), False)),
    (r'^(?:rm|del|remove|\u5220\u9664|\u5220)\s*(\d+)$',
     lambda m: _do_remove(int(m.group(1)))),
    (r'^(?:clear|\u6e05\u7a7a|\u6e05\u9664)$',
     lambda m: print(f"  cleared {cardlib.clear_done()} done tasks\n")),
    (r'^(?:title|\u6807\u9898)\s+(.+)$',
     lambda m: (cardlib.set_title(m.group(1)), print(f"  title \u2192 {m.group(1)}\n"))),
    (r'^(?:replace|\u66ff\u6362|\u8986\u5199|write)\s+(.+)$',
     lambda m: (cardlib.overwrite(m.group(1)), print("  content replaced\n"))),
    (r'^edit$',
     lambda m: subprocess.run([os.environ.get("EDITOR", "nano"), cardlib.CONTENT_FILE])),
]


def _do_toggle(num, to_done):
    ok, text = cardlib.toggle_task(num, to_done)
    if ok:
        mark = "\u2713" if to_done else "\u25cb"
        print(f"  {mark} {text}\n")
    else:
        print(f"  error: {text}\n")


def _do_remove(num):
    ok, text = cardlib.remove_task(num)
    if ok:
        print(f"  \u2717 deleted: {text}\n")
    else:
        print(f"  error: {text}\n")


def parse_and_execute(user_input):
    text = user_input.strip()
    if not text:
        return True

    for pattern, handler in COMMANDS:
        m = re.match(pattern, text, re.IGNORECASE)
        if m:
            result = handler(m)
            return result != "EXIT"

    # Default: add as task(s)
    tasks = cardlib.split_multi_tasks(text)
    cardlib.add_tasks(tasks)
    for t in tasks:
        print(f"  \u2713 added: {t}")
    print()
    return True


def main():
    print()
    print("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510")
    print('  \u2502   Sticky Card \u00b7 Chat Terminal      \u2502')
    print('  \u2502   type to add tasks, "help" for more \u2502')
    print("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")
    show_card()

    while True:
        try:
            user_input = input("  > ")
            if not parse_and_execute(user_input):
                print("  bye \U0001f44b\n")
                break
        except (EOFError, KeyboardInterrupt):
            print("\n  bye \U0001f44b\n")
            break


if __name__ == "__main__":
    main()
