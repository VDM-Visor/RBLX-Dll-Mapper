import ctypes
import sys

class LibraryManager:
    def __init__(self):
        self.user32 = None
        self.win32u = None

    def init(self):
        try:
            self.user32 = ctypes.WinDLL("user32.dll")
            self.win32u = ctypes.WinDLL("win32u.dll")

            if not self.user32 or not self.win32u:
                return False
            user32_handle = ctypes.windll.kernel32.GetModuleHandleW("user32.dll")
            win32u_handle = ctypes.windll.kernel32.GetModuleHandleW("win32u.dll")

            if not user32_handle or not win32u_handle:
                return False

            return True
        except Exception as e:
            print(f"[-] Error: {e}", file=sys.stderr)
            return False

if __name__ == "__main__":
    manager = LibraryManager()
    if manager.init():
        print("[+] Libraries loaded")
    else:
        print("[-] Failed to load libraries")
