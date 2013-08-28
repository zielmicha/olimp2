import time

def check(task, data, callback):
    for i in xrange(12):
        callback({'type': 'msg', 'val': 'done %d' % i})
        time.sleep(3)
    callback({'type': 'end'})
