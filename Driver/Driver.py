import ctypes
import psutil
from ctypes import wintypes

class Driver:
    _singleton = None

    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    @staticmethod
    def get_process_id(process_name):
        """Get the process ID by name."""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['pid']
        return 0

    def setup(self):
        """Initialize library and function pointers."""
        if not self._init_libraries():
            return False
        try:
            self.nt_user_function = self._get_proc_address(self.user32, "NtUserRegisterErrorReportingDialog")
            if not self.nt_user_function:
                self.nt_user_function = self._get_proc_address(self.win32u, "NtUserRegisterErrorReportingDialog")
            return bool(self.nt_user_function)
        except Exception as e:
            print(f"Setup failed: {e}")
            return False

    def _init_libraries(self):
        """Load necessary libraries."""
        try:
            self.user32 = ctypes.WinDLL("user32.dll")
            self.win32u = ctypes.WinDLL("win32u.dll")
            return True
        except Exception as e:
            print(f"Library initialization failed: {e}")
            return False

    def _get_proc_address(self, library, function_name):
        """Get the address of a function in the library."""
        try:
            return getattr(library, function_name)
        except AttributeError:
            return None

    def get_base_address(self, process_id):
        """Send a request to the driver to get the base address."""
        request = DRIVER_REQUEST()
        request.type = BASE
        request.pid = wintypes.HANDLE(process_id)
        self._send_request(request)
        return request.base

    def writem(self, address, buffer, size):
        """Send a request to the driver to write memory."""
        request = DRIVER_REQUEST()
        request.type = WRITE
        request.pid = wintypes.HANDLE(self.process_id)
        request.address = address
        request.buffer = buffer
        request.size = size
        self._send_request(request)

    def readm(self, address, buffer, size):
        """Send a request to the driver to read memory."""
        request = DRIVER_REQUEST()
        request.type = READ
        request.pid = wintypes.HANDLE(self.process_id)
        request.address = address
        request.buffer = buffer
        request.size = size
        self._send_request(request)

    def _send_request(self, request):
        """Send a request to the driver (stub)."""
        pass

class DRIVER_REQUEST(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("pid", wintypes.HANDLE),
        ("address", ctypes.c_void_p),
        ("buffer", ctypes.c_void_p),
        ("size", wintypes.DWORD),
        ("base", ctypes.c_void_p)
    ]

BASE = 1
WRITE = 2
READ = 3


if __name__ == "__main__":
    driver = Driver()
    if driver.setup():
        process_id = driver.get_process_id("example.exe")
        if process_id:
            base_address = driver.get_base_address(process_id)
            print(f"[+] Base address: {base_address}")
        else:
            print("[-] Process not found.")
    else:
        print("[-] Driver setup failed.")
