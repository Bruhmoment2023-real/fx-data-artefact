"""Run a script in-process via runpy and print own CPU seconds and peak working set at exit.
Usage: python runstat.py script.py [args...]   (cwd and sys.path[0] = script's folder, like normal)"""
import sys, os, runpy, time, ctypes
from ctypes import wintypes

class PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("a", ctypes.c_size_t), ("b", ctypes.c_size_t),
                ("c", ctypes.c_size_t), ("d", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

def stats():
    k32 = ctypes.WinDLL("kernel32"); ps = ctypes.WinDLL("psapi")
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    h = k32.GetCurrentProcess()
    ps.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    m = PMC(); m.cb = ctypes.sizeof(PMC); ps.GetProcessMemoryInfo(h, ctypes.byref(m), m.cb)
    t = os.times()
    return t.user + t.system, m.PeakWorkingSetSize / 2**20

if __name__ == "__main__":
    script = os.path.abspath(sys.argv[1]); sys.argv = sys.argv[1:]
    sys.path.insert(0, os.path.dirname(script))
    t0 = time.time()
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        cpu, peak = stats()
        print(f"# runstat script={os.path.basename(script)} wall_s={time.time()-t0:.1f} cpu_s={cpu:.1f} peak_rss_mb={peak:.0f}", flush=True)
