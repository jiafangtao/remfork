import sys
from contexts.procerror import ProcError


class ProcContext:
    MAX_LIVE_PROC_COUNT = 1
    MAX_DEAD_PROC_COUNT = 200

    def __init__(self, stdout_sink=sys.stdout, stderr_sink=sys.stderr):
        self.stdout_sink = stdout_sink
        self.stderr_sink = stderr_sink
        self.live_procs = []
        self.dead_procs = []

    async def begin_proc(self, pid):
        if self._is_alive(pid):
            return

        if self._can_add_more():
            self.live_procs.append({pid: {}})
            await self.notify_pid(pid)
        else:
            raise ProcError("out of capacity")

    async def end_proc(self, pid, retcode):
        #TODO: move the proc from live to dead group
        pass

    async def log_stdout(self, line):
        await self.stdout_sink.write(line)

    async def log_stderr(self, line):
        await self.stderr_sink.write(line)

    async def notify_pid(self, pid):
        pass

    def _proc_count(self):
        return len(self.procs)
    
    def _can_add_more(self):
        return len(self.live_procs) < self.MAX_LIVE_PROC_COUNT

    def _is_alive(self, pid):
        for proc in self.live_procs:
            if proc.pid == pid:
                return True
            
        return False

class AioProcContext(ProcContext):
    def __init__(self, server, sid, stdout_sink=sys.stdout, stderr_sink=sys.stderr):
        self.server = server
        self.sid = sid
        self.curr_pid = None
        super().__init__(stdout_sink, stderr_sink)

    async def begin_proc(self, pid):
        await super().begin_proc(pid)
        self.curr_pid = pid

        await self.notify_pid(pid)

    async def end_proc(self, pid, retcode):
        """
        The hook called when the process has ended.
        retcode maybe none if the process was terminated.
        """
        await super().end_proc(pid, retcode)
        await self.server.emit("ps.exit", data=f"pid={pid}, retcode={retcode}", to=self.sid)

    async def notify_pid(self, pid):
        await super().notify_pid(pid)

        print(f"notifying the client with pid {pid} ...")
        await self.server.emit("ps.pid", data=pid, to=self.sid)
