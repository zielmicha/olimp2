import time
import sandbox_client
import json
import os
import tempfile

TASK_DIR = os.environ.get('TASK_DIR', '.')

def check(task, data, callback):
    taskdir = 'task_%s' % task
    if taskdir not in os.listdir(TASK_DIR):
        raise ValueError('bad task %r' % task)
    taskdir = TASK_DIR + '/' + taskdir

    sandbox = sandbox_client.Sandbox(os.environ.get('SANDBOX_SOCK', '/var/run/sandboxd/sock'))
    sandbox.timeout = 30
    sandbox.tar.add('test_runner.py', arcname='init')

    dataf = tempfile.NamedTemporaryFile()
    dataf.write(data)
    dataf.flush()

    sandbox.tar.add(dataf.name, arcname='program')
    sandbox.tar.add(taskdir, arcname='task')

    sandbox.start()

    for line in sandbox.output:
        callback(json.loads(line))
    callback({'type': 'end'})

if __name__ == '__main__':
    import sys
    def callback(v): print v
    check(sys.argv[1], open(sys.argv[2]).read(), callback)
