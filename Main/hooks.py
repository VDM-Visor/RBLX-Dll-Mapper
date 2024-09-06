import ctypes
from ctypes import wintypes

def hook_function(function_address, new_bytes, hook_data, process_handle):
    ctypes.windll.kernel32.WriteProcessMemory(
        process_handle,
        function_address,
        new_bytes,
        len(new_bytes),
        None
    )
    print(f"[+] Hooked func at {hex(function_address)}")

def unhook_function(function_address, original_bytes, hook_data, process_handle):
    ctypes.windll.kernel32.WriteProcessMemory(
        process_handle,
        function_address,
        original_bytes,
        len(original_bytes),
        None
    )
    print(f"[+] Unhooked function at {hex(function_address)}")

def restore_function(hook_data, process_handle):
    ctypes.windll.kernel32.WriteProcessMemory(
        process_handle,
        hook_data['address'],
        hook_data['original_bytes'],
        len(hook_data['original_bytes']),
        None
    )
    print(f"[+] Restored function at {hex(hook_data['address'])}")

def get_hwnd_of_process_id(target_process_id):
    hwndout = wintypes.HWND(0)
    
    def enum_window_proc(hwnd, lParam):
        nonlocal hwndout
        _, process_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        if process_id == lParam:
            hwndout = hwnd
            return False
        return True
    
    ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(enum_window_proc), target_process_id)
    return hwndout
