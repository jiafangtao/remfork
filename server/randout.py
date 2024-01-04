import datetime
import sys
import time
import random

print(f"hello from {sys.argv[0]}")

_MAX = 100

out = 0
err = 0

def timestamp():
    return datetime.datetime.now().isoformat()


while out < _MAX and err < _MAX:
    choice = random.randint(0, 1)
    if choice > 0:
        sys.stdout.write(f'{timestamp()} <out> {out}...\n')
        sys.stdout.flush()
        out += 1
    else:
        sys.stderr.write(f'{timestamp()} <err> {err}...\n')
        sys.stderr.flush()
        err += 1
    time.sleep(1)

sys.stdout.write(f'{timestamp()} end.\n')
