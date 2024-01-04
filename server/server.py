import argparse
import sys
from datetime import datetime
from aiohttp import web
import socketio
from contexts.procctx import AioProcContext
from sink import AioSink

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


async def health(request):
    return web.Response(text="healthy")

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    #NOTE: this is for type of "chat_message" (I'm not that much into history of socketio)
    print(f"message {data} from client {sid}")

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.on('ping')
async def handle_ping(sid, data):
    await sio.emit("pong", data=str(datetime.now()), to=sid)

@sio.on('echo')
async def handle_echo(sid, data):
    print("echo: ", data)
    await sio.emit("echo", data=data, to=sid)

@sio.on('request.fork')
async def handle_fork(sid, data):
    from cmds import fork
    cmd = fork.ForkCommand(data)
    context = AioProcContext(sio, sid, AioSink(sio, sid, "ps.stdout"), AioSink(sio, sid, "ps.stderr"))
    try:
        await cmd.run(context)
    except Exception as ex:
        print("oops, we got an exception,", ex)
        await sio.emit("ps.exception", data=str(ex), to=sid)
        await sio.emit("ps.exit", data=f"fork failed with pid={context.curr_pid}", to=sid)

@sio.on('request.kill')
async def handle_kill(sid, data):
    from cmds import kill
    cmd = kill.KillCommand(sio, sid, data)
    context = AioProcContext(sio, sid, AioSink(sio, sid, "stdout"))
    await cmd.run(context)

app.router.add_get('/health', health)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="solver wrapper")
    parser.add_argument('--port', default=80)

    args = parser.parse_args()
    web.run_app(app, port=args.port)