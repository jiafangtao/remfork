import selectors
import subprocess

# a reactor
sel = selectors.DefaultSelector()

class ForkCommand:
    def __init__(self, data: dict):
        print("Received command fork", data)
        
        self.wkdir = data.get("wkdir")
        self.cmdline = [data["cmd"]]

        if data.get("args"):
            self.cmdline.extend(data["args"].split())


    async def run(self, context):
        print(f"(debug) Run command {self.cmdline}")
        with subprocess.Popen(self.cmdline, cwd=self.wkdir, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            print(f"(debug) new process is created with pid={proc.pid}")
            await context.begin_proc(proc.pid)

            sel.register(proc.stdout, selectors.EVENT_READ, {"ctx": context, "cb": handle_stdout})
            sel.register(proc.stderr, selectors.EVENT_READ, {"ctx": context, "cb": handle_stderr})
            
            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data["cb"]
                    context = key.data["ctx"]
                    await callback(key.fileobj, context)

                retcode = proc.poll()

                if retcode is not None:
                    print(f"(debug) retcode={retcode}")

                    last_out, last_err = proc.communicate()
                    print(f"last out - {last_out}")
                    print(f"last err - {last_err}")

                    await context.end_proc(proc.pid, retcode)
                    print(f"(debug) child process has finished.")
                    break

            sel.unregister(proc.stdout)
            sel.unregister(proc.stderr)

async def handle_stdout(fileobj, context):
    line = fileobj.readline()
    if line:
        await context.log_stdout(line)
        print(f"(debug) {line}")


async def handle_stderr(fileobj, context):
    line = fileobj.readline()
    if line:
        await context.log_stderr(line)
        print(f"(debug) {line}")
