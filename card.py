"""
card CLI - single-command interface for card content.
Usage: card [show|add|done|undo|rm|clear|title|write|edit] [args]
"""

import sys
import os
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cardlib


def show():
    lines = cardlib.read_lines()
    tasks = cardlib.get_tasks(lines)
    if not tasks:
        print("".join(lines) if lines else "(empty)")
        return
    print()
    for idx, (_, done, text) in enumerate(tasks, 1):
        mark = "\u2713" if done else " "
        print(f"  {idx}. [{mark}] {text}")
    print()


def usage():
    print("""
  card CLI

  card               show tasks
  card add <text>    add task
  card done <n>      check task
  card undo <n>      uncheck task
  card rm <n>        delete task
  card clear         clear done tasks
  card title <text>  set title
  card write <text>  replace all content
  card edit          open in editor
""")


def main():
    args = sys.argv[1:]
    if not args:
        show()
        return

    cmd = args[0].lower()
    rest = " ".join(args[1:])

    if cmd == "show":
        show()
    elif cmd == "add" and rest:
        for t in cardlib.add_tasks(cardlib.split_multi_tasks(rest)):
            print(f"  + {t}")
    elif cmd == "done" and rest:
        ok, text = cardlib.toggle_task(int(rest), True)
        print(f"  \u2713 {text}" if ok else f"  error: {text}")
    elif cmd == "undo" and rest:
        ok, text = cardlib.toggle_task(int(rest), False)
        print(f"  \u25cb {text}" if ok else f"  error: {text}")
    elif cmd == "rm" and rest:
        ok, text = cardlib.remove_task(int(rest))
        print(f"  - {text}" if ok else f"  error: {text}")
    elif cmd == "clear":
        print(f"  cleared {cardlib.clear_done()} done tasks")
    elif cmd == "title" and rest:
        cardlib.set_title(rest)
        print(f"  title \u2192 {rest}")
    elif cmd == "write" and rest:
        cardlib.overwrite(rest)
        print("  content updated")
    elif cmd == "edit":
        subprocess.run([os.environ.get("EDITOR", "notepad"), cardlib.CONTENT_FILE])
    else:
        usage()


if __name__ == "__main__":
    main()
