import sys
import argparse
import asyncio
import socketio
import fork

async def main():
    debug("running socket.io client ......")
    args = parse_args(sys.argv[1:])

    sio = socketio.AsyncClient()
    await sio.connect(f'http://{args.host}:{args.port}')
    debug(f"my sid is {sio.sid}")
    await sio.emit('echo', 'hello from client should be echoed back ...')

    if args.action == "fork":
        await sio.emit('request.fork', fork.make_request(args))
    elif args.action == "kill":
        # TODO: not implemented yet
        await sio.emit("request.kill", None)

    @sio.on("echo")
    def on_echo(data):
        debug(f"event echo: {data}")

    @sio.on("ps.pid")
    def on_pid(data):
        debug(f"pid: {data}")

    @sio.on("ps.stdout")
    def on_stdout(data):
        print(f"{data}")
    
    @sio.on("ps.stderr")
    def on_stderr(data):
        print(f"{data}")

    @sio.on('ps.exit')
    async def on_exit(data):
        debug("process ends, I'd quit")
        await sio.disconnect()

    @sio.on("*")
    def catch_all(event, data):
        debug(f"event={event}, data={data}")
    
    await sio.wait()
    debug("exit after wait is done ......")

def parse_args(args):
    parser = argparse.ArgumentParser(description="A stub to proxy fork command to remote server.")
    parser.add_argument("--host", default="localhost", help="Hostname or ip of remote server")
    parser.add_argument("--port", "-p", default=8080, type=int, required=False)
    parser.add_argument("--action", default="fork", help="Which action to take. It can be fork or kill")
    parser.add_argument("--cmd", "-x", required=True, help="Command to be run")
    parser.add_argument("--args", required=False, help="Arguments to the command")
    parser.add_argument("--wkdir", required=False, help="Working directory of the command")
    
    return parser.parse_args(args)

def debug(msg):
    #TODO: write to a file to avoid mess up stdout and stderr
    print(f"(debug) {msg}")


if __name__ == '__main__':
    asyncio.run(main())
