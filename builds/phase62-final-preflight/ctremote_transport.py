"""Pinned ctremote WinMM Link path, library only; no command CLI.

send adds prepare/timeout checks and retains unfinished driver buffers. No
uploader, port enumeration or Link construction occurs at import time.
"""
import ctypes,queue,sys,time
from ctypes import wintypes
_NOR_PENDING_SENDS=[]
# ---------------------------------------------------------------- WinMM
winmm = None
_NOR_PENDING_INPUTS=[]
def _api():
    global winmm
    if winmm is None:
        if sys.platform != 'win32':raise OSError('WinMM requires Windows')
        winmm=ctypes.WinDLL('winmm')
    return winmm
CALLBACK_FUNCTION = 0x30000
MIM_LONGDATA = 0x3C4
MHDR_DONE = 1


class MIDIHDR(ctypes.Structure):
    _fields_ = [("lpData", ctypes.c_void_p), ("dwBufferLength", wintypes.DWORD), ("dwBytesRecorded", wintypes.DWORD), ("dwUser", ctypes.c_void_p),
                ("dwFlags", wintypes.DWORD), ("lpNext", ctypes.c_void_p), ("reserved", ctypes.c_void_p), ("dwOffset", wintypes.DWORD),
                ("dwReserved", ctypes.c_void_p * 8)]


class MIDIINCAPSW(ctypes.Structure):
    _fields_ = [("wMid", wintypes.WORD), ("wPid", wintypes.WORD), ("vDriverVersion", wintypes.UINT), ("szPname", wintypes.WCHAR * 32), ("dwSupport", wintypes.DWORD)]


class MIDIOUTCAPSW(ctypes.Structure):
    _fields_ = [("wMid", wintypes.WORD), ("wPid", wintypes.WORD), ("vDriverVersion", wintypes.UINT), ("szPname", wintypes.WCHAR * 32), ("wTechnology", wintypes.WORD),
                ("wVoices", wintypes.WORD), ("wNotes", wintypes.WORD), ("wChannelMask", wintypes.WORD), ("dwSupport", wintypes.DWORD)]


MIDIINPROC = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)(   # CFUNCTYPE elsewhere: importable on Linux for the emulation tests
    None, wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)


def ports():
    _api()
    ins, outs = [], []
    for i in range(winmm.midiInGetNumDevs()):
        c = MIDIINCAPSW(); r=winmm.midiInGetDevCapsW(i, ctypes.byref(c), ctypes.sizeof(c))
        if r:raise OSError('input capability query failed: '+str(r))
        ins.append(c.szPname)
    for i in range(winmm.midiOutGetNumDevs()):
        c = MIDIOUTCAPSW(); r=winmm.midiOutGetDevCapsW(i, ctypes.byref(c), ctypes.sizeof(c))
        if r:raise OSError('output capability query failed: '+str(r))
        outs.append(c.szPname)
    return ins, outs


class Link:
    def __init__(self, name="Circuit"):
        ins, outs = ports()
        ii = [i for i, n in enumerate(ins) if name.lower() in n.lower()]
        oo = [i for i, n in enumerate(outs) if name.lower() in n.lower()]
        if len(ii)!=1 or len(oo)!=1:
            raise OSError(f"MIDI port selection requires one input and output: {name!r}; inputs={ins}; outputs={outs}")
        self.q=queue.Queue();self.hin=wintypes.HANDLE();self.hout=wintypes.HANDLE()
        self.bufs=[];self.input_open=False;self.output_open=False;self.closed=False
        self.cb=MIDIINPROC(self._cb)
        def check(result,label):
            if result:raise OSError(label+' failed: '+str(result))
        try:
            check(winmm.midiInOpen(ctypes.byref(self.hin),ii[0],self.cb,None,CALLBACK_FUNCTION),'midiInOpen');self.input_open=True
            check(winmm.midiOutOpen(ctypes.byref(self.hout),oo[0],None,None,0),'midiOutOpen');self.output_open=True
            for _ in range(8):
                b=ctypes.create_string_buffer(1024);hd=MIDIHDR();hd.lpData=ctypes.cast(b,ctypes.c_void_p);hd.dwBufferLength=1024
                check(winmm.midiInPrepareHeader(self.hin,ctypes.byref(hd),ctypes.sizeof(hd)),'midiInPrepareHeader')
                self.bufs.append((b,hd))
                check(winmm.midiInAddBuffer(self.hin,ctypes.byref(hd),ctypes.sizeof(hd)),'midiInAddBuffer')
            check(winmm.midiInStart(self.hin),'midiInStart');self.seq=0
        except BaseException:
            self.close();raise

    def _cb(self, h, msg, inst, p1, p2):
        if msg == MIM_LONGDATA and p1:
            hd = ctypes.cast(p1, ctypes.POINTER(MIDIHDR)).contents
            if hd.dwBytesRecorded:
                self.q.put((ctypes.string_at(hd.lpData, hd.dwBytesRecorded), p1))
            else:
                self.q.put((b"", p1))

    def _readd(self, p1):
        winmm.midiInAddBuffer(self.hin, ctypes.c_void_p(p1), ctypes.sizeof(MIDIHDR))

    def send(self, data):
        b=ctypes.create_string_buffer(bytes(data),len(data));hd=MIDIHDR();hd.lpData=ctypes.cast(b,ctypes.c_void_p);hd.dwBufferLength=len(data)
        r=winmm.midiOutPrepareHeader(self.hout,ctypes.byref(hd),ctypes.sizeof(hd))
        if r:raise OSError('midiOutPrepareHeader failed: '+str(r))
        r=winmm.midiOutLongMsg(self.hout,ctypes.byref(hd),ctypes.sizeof(hd))
        if r:
            winmm.midiOutUnprepareHeader(self.hout,ctypes.byref(hd),ctypes.sizeof(hd))
            raise OSError('midiOutLongMsg failed: '+str(r))
        deadline=time.time()+2.0
        while not hd.dwFlags & MHDR_DONE and time.time()<deadline:time.sleep(0.001)
        if not hd.dwFlags & MHDR_DONE:
            _NOR_PENDING_SENDS.append((b,hd,self))
            raise TimeoutError('WinMM output did not complete; buffer retained; DO NOT RETRY')
        r=winmm.midiOutUnprepareHeader(self.hout,ctypes.byref(hd),ctypes.sizeof(hd))
        if r:
            _NOR_PENDING_SENDS.append((b,hd,self));raise OSError('output buffer release failed: '+str(r))

    def close(self):
        if self.closed:return
        self.closed=True
        # Reset returns host input buffers; it sends no MIDI/storage command.
        if self.input_open:
            winmm.midiInStop(self.hin);winmm.midiInReset(self.hin)
            for b,hd in self.bufs:
                r=winmm.midiInUnprepareHeader(self.hin,ctypes.byref(hd),ctypes.sizeof(hd))
                if r:_NOR_PENDING_INPUTS.append((b,hd,self))
            winmm.midiInClose(self.hin);self.input_open=False
        if self.output_open:
            winmm.midiOutClose(self.hout);self.output_open=False
