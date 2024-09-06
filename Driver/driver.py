import ctypes
from ctypes import wintypes, c_void_p, c_size_t

class Driver:
    _singleton = None

    class DRIVER_REQUEST(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("pid", wintypes.HANDLE),
            ("address", c_void_p),
            ("buffer", c_void_p),
            ("size", c_size_t),
            ("base", c_void_p)
        ]

    REQUEST_TYPE_NONE = 0
    REQUEST_TYPE_BASE = 1
    REQUEST_TYPE_WRITE = 2
    REQUEST_TYPE_READ = 3

    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        self.nt_user_function = None
        self.process_id = None
        self.base_address = None
        self.user32 = None
        self.win32u = None

    @staticmethod
    def get_singleton():
        return Driver()

    def get_process_id(self, process_name):
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['pid']
        return 0

    def setup(self):
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

    def get_base_address(self):
        request = self.DRIVER_REQUEST()
        request.type = self.REQUEST_TYPE_BASE
        request.pid = wintypes.HANDLE(self.process_id)
        self._send_request(request)
        return request.base

    def writem(self, address, buffer, size):
        request = self.DRIVER_REQUEST()
        request.type = self.REQUEST_TYPE_WRITE
        request.pid = wintypes.HANDLE(self.process_id)
        request.address = c_void_p(address)
        request.buffer = c_void_p(ctypes.addressof(buffer))
        request.size = size
        self._send_request(request)

    def readm(self, address, buffer, size):
        request = self.DRIVER_REQUEST()
        request.type = self.REQUEST_TYPE_READ
        request.pid = wintypes.HANDLE(self.process_id)
        request.address = c_void_p(address)
        request.buffer = c_void_p(ctypes.addressof(buffer))
        request.size = size
        self._send_request(request)

    def _send_request(self, request):
        if self.nt_user_function:
            self.nt_user_function(ctypes.cast(ctypes.pointer(request), ctypes.c_void_p).value)
        else:
            raise RuntimeError("nt_user_function is not initialized")

    def write(self, address, value):
        self.writem(address, value, ctypes.sizeof(type(value)))

    def read(self, address, value_type):
        buffer = value_type()
        self.readm(address, buffer, ctypes.sizeof(buffer))
        return buffer
