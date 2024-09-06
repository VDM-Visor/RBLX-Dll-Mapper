import ctypes
import time
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'driver'))

from driver import Driver
from hooks import hook_function, unhook_function, restore_function, get_hwnd_of_process_id

def main():
    pDriver = Driver.get_singleton()
    pDriver.setup()

    while pDriver.process_id == 0:
        time.sleep(1)
        pDriver.process_id = pDriver.get_process_id("RobloxPlayerBeta.exe")

    process_handle = ctypes.windll.kernel32.OpenProcess(
        ctypes.wintypes.PROCESS_ALL_ACCESS,
        False,
        pDriver.process_id
    )

    if not process_handle:
        print("[-] Failed to open process.")
        return

    print(f"[+] Base: 0x{pDriver.base_address:X}")

    lib3 = ctypes.windll.kernel32.LoadLibraryW("C:\\Windows\\System32\\Wintrust.dll")

    if not lib3:
        print("[-] Failed to load Wintrust.dll")
        return

    hook_data = {
        'address': None,
        'original_bytes': bytearray(6)
    }

    hook_bytes = bytearray([0xB8, 0x00, 0x00, 0x00, 0x00, 0xC3])  # Overwrite bytes

    func_addy = ctypes.windll.kernel32.GetProcAddress(lib3, b"WinVerifyTrust")

    if func_addy:
        hook_data['address'] = func_addy
        ctypes.windll.kernel32.ReadProcessMemory(
            process_handle,
            func_addy,
            hook_data['original_bytes'],
            len(hook_data['original_bytes']),
            None
        )
        hook_function(func_addy, hook_bytes, hook_data, process_handle)

    ctypes.windll.kernel32.FreeLibrary(lib3)

    target_process_hwnd = get_hwnd_of_process_id(pDriver.process_id)
    tid = ctypes.windll.user32.GetWindowThreadProcessId(target_process_hwnd, None)

    print(f"tid: {tid}")

    dll = ctypes.windll.kernel32.LoadLibraryExW("roblox.dll", None, 0x00000001)  # DONT_RESOLVE_DLL_REFERENCES

    if not dll:
        print("[-] The DLL could not be found.")
        return

    addr = ctypes.windll.kernel32.GetProcAddress(dll, b"callback")

    if not addr:
        print("[-] DLL is invalid.")
        return

    handle = ctypes.windll.user32.SetWindowsHookExW(
        7,  # WH_GETMESSAGE
        addr,
        dll,
        tid
    )

    if not handle:
        print("[-] Hook failed")
        return

    ctypes.windll.user32.PostThreadMessageW(tid, 0xFFFF, 0, 0)  # WM_NULL

    input("Press Enter to continue...")

    unhook = ctypes.windll.user32.UnhookWindowsHookEx(handle)

    if not unhook:
        print("[-] Failed to unload.")
        return

    restore_function(hook_data, process_handle)
    ctypes.windll.kernel32.CloseHandle(process_handle)

    print("[+] Done\nPress any key to exit.")
    input()

if __name__ == "__main__":
    main()
