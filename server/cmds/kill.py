class KillCommand:
    def __init__(self, async_server, sid, data):
        self.server = async_server
        self.cid = sid
        self.data = data

        #TODO: parse pid
        self.pid = 12345

    def run(self, context):
        if self.pid:
            context.end_proc(self.pid)