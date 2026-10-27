"""Run owned tools in a kill-on-close Windows job, including their descendants."""
import ctypes
from ctypes import wintypes
import subprocess
import threading
import time

from build_operation import checkpoint

OWNER_JOB = None
OWNER_LOCK = threading.Lock()


class BasicLimits(ctypes.Structure):
    _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64),
                ('flags', wintypes.DWORD), ('minimum', ctypes.c_size_t), ('maximum', ctypes.c_size_t),
                ('active_limit', wintypes.DWORD), ('affinity', ctypes.c_size_t),
                ('priority', wintypes.DWORD), ('scheduling', wintypes.DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [('basic', BasicLimits), ('io', ctypes.c_uint64 * 6),
                ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t),
                ('peak_process_memory', ctypes.c_size_t), ('peak_job_memory', ctypes.c_size_t)]


class Accounting(ctypes.Structure):
    _fields_ = [('times', ctypes.c_int64 * 4), ('faults', wintypes.DWORD),
                ('total', wintypes.DWORD), ('active', wintypes.DWORD), ('terminated', wintypes.DWORD)]


class ToolJob:
    def __init__(self):
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            'SetInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
            'QueryInformationJobObject': ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
                                           ctypes.c_void_p], wintypes.BOOL),
            'AssignProcessToJobObject': ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            'TerminateJobObject': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            'OpenProcess': ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = arguments, result
        self.handle = self.kernel.CreateJobObjectW(None, None)
        self.require(self.handle)
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        try:
            self.require(self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        except Exception:
            self.kernel.CloseHandle(self.handle)
            raise

    @staticmethod
    def require(result):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())

    def assign_and_resume(self, process):
        handle = self.kernel.OpenProcess(0x901, False, process.pid)
        self.require(handle)
        try:
            self.require(self.kernel.AssignProcessToJobObject(self.handle, handle))
            resume = ctypes.WinDLL('ntdll').NtResumeProcess
            resume.argtypes, resume.restype = [wintypes.HANDLE], wintypes.LONG
            if resume(handle) != 0:
                raise OSError('Could not resume owned packaging tool')
        finally:
            self.kernel.CloseHandle(handle)

    def own_current_process(self):
        # The lifetime job covers the gap between suspended process creation
        # and assignment to the cancellable per-tool job. Keep its handle for
        # the app lifetime; Windows closes it on exit, killing all descendants.
        self.require(self.kernel.AssignProcessToJobObject(self.handle, wintypes.HANDLE(-1)))

    def close(self):
        try:
            self.require(self.kernel.TerminateJobObject(self.handle, 1))
            # Descendants can still hold workspace files after the primary
            # exits. Do not release the workspace lease until all have stopped.
            accounting = Accounting()
            while True:
                self.require(self.kernel.QueryInformationJobObject(
                    self.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None))
                if not accounting.active:
                    break
                time.sleep(0.01)
        finally:
            self.kernel.CloseHandle(self.handle)


def capture_owned(command, **kwargs):
    global OWNER_JOB
    checkpoint()
    with OWNER_LOCK:
        if OWNER_JOB is None:
            owner = ToolJob()
            try:
                owner.own_current_process()
            except Exception:
                owner.close()
                raise
            OWNER_JOB = owner
    job = ToolJob()
    try:
        # Suspended creation closes the race where a tool could spawn children
        # before being assigned to the job. Job setup failure is fatal.
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW | 0x4, **kwargs) as process:
            try:
                job.assign_and_resume(process)
                while True:
                    checkpoint()
                    try:
                        stdout, stderr = process.communicate(timeout=0.1)
                        checkpoint()
                        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
                    except subprocess.TimeoutExpired:
                        pass
            finally:
                job.close()
                job = None
                if process.poll() is None:
                    process.kill()
                process.communicate()
    finally:
        if job is not None:
            job.close()
