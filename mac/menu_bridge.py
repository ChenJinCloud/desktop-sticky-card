"""macOS status item process and native window capture protection."""
import ctypes
import ctypes.util
import os
import queue
import subprocess
import threading


def protect_window(title):
    """Set NSWindowSharingNone on this process's named Tk window."""
    objc = ctypes.CDLL(ctypes.util.find_library("objc"))
    objc.objc_getClass.argtypes = [ctypes.c_char_p]
    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.argtypes = [ctypes.c_char_p]
    objc.sel_registerName.restype = ctypes.c_void_p
    def selector(name):
        return objc.sel_registerName(name.encode())
    msg0 = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(("objc_msgSend", objc))
    msg1 = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)(("objc_msgSend", objc))
    app = msg0(objc.objc_getClass(b"NSApplication"), selector("sharedApplication"))
    windows = msg0(app, selector("windows"))
    for index in range(msg0(windows, selector("count"))):
        window = msg1(windows, selector("objectAtIndex:"), index)
        name = msg0(window, selector("title"))
        name_ptr = msg0(name, selector("UTF8String")) if name else None
        if name_ptr and ctypes.string_at(name_ptr).decode("utf-8") == title:
            msg1(window, selector("setSharingType:"), 0)
            return msg0(window, selector("sharingType")) in (None, 0)
    return False


class MenuBridge:
    def __init__(self, script):
        self.events = queue.Queue()
        self.process = subprocess.Popen(
            ["/usr/bin/swift", os.fspath(script)], stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
        )
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.process.stdout:
            self.events.put(line.strip())
        self.events.put("closed")

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
