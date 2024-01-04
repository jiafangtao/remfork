class AioSink:
    '''A sink for socketio async server'''
    def __init__(self, async_server, socket_id, event_type="message"):
        self.aio = async_server
        self.sid = socket_id
        self.event_type = event_type

    async def write(self, line):
        await self.aio.emit(self.event_type, line, to=self.sid)


class NoopSink:
    def write(self, line):
        pass
