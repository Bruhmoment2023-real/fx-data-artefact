"""Run one command, tee its output to a log, and record wall time, CPU time and peak memory
of the child process (Windows API via ctypes; no extra packages).

Usage: python runlog.py <logfile> <cwd> <cmd> [args...]
"""
import sys, time, subprocess, ctypes, datetime as dt
from ctypes import wintypes


class PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


def child_stats(handle):
    k32 = ctypes.WinDLL("kernel32", use_last_error=True); psapi = ctypes.WinDLL("psapi", use_last_error=True)
    k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    h = wintypes.HANDLE(handle)
    c, e, k, u = (wintypes.FILETIME() for _ in range(4))
    k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u))
    ft = lambda f: ((f.dwHighDateTime << 32) + f.dwLowDateTime) / 1e7
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb)
    return ft(k) + ft(u), pmc.PeakWorkingSetSize / 2 ** 20


if __name__ == "__main__":
    log, cwd, cmd = sys.argv[1], sys.argv[2], sys.argv[3:]
    t0 = time.time()
    with open(log, "w", encoding="utf-8", errors="replace") as fh:
        fh.write(f"# started {dt.datetime.now(dt.timezone.utc).isoformat()}\n# cwd {cwd}\n# cmd {' '.join(cmd)}\n")
        fh.flush()
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
        for line in p.stdout:
            fh.write(line); fh.flush()
        rc = p.wait()
        cpu, peak = child_stats(int(p._handle))
        msg = f"# exit={rc} wall_s={time.time()-t0:.1f} cpu_s={cpu:.1f} peak_rss_mb={peak:.0f}\n"
        fh.write(msg)
    print(log.split("/")[-1].split("\\")[-1], msg.strip())
