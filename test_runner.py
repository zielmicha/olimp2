#!/usr/bin/env python
import subprocess
import os
import yaml
import json
import traceback
import sys
import time

def main():
    null = open('/dev/null', 'w')
    os.dup2(null.fileno(), 2)
    try:
        main0()
    except Exception:
        message(traceback.format_exc(), 'error')

def main0():
    message('Starting...', 'progress')
    task = os.environ.get('TASK', 'task')
    program = os.path.abspath(os.environ.get('PROGRAM', 'program'))
    compile_program(program)

    os.chdir(task)
    run_tests(program)

def compile_program(program):
    r = subprocess.check_output(['file', '--mime', program])
    mime = r.split(':')[1].split(';')[0].strip()
    if mime == 'application/x-executable':
        message('Detected Linux compiled program')
        os.chmod(program, 0o755)
    elif mime == 'application/x-dosexec':
        message('Detected Windows compiled program')
        os.rename('program', 'program.exe')
        with open('program', 'w') as f:
            f.write('#!/bin/sh\nwine program.exe\nexit 0\n')
        os.chmod(program, 0o755)
    elif mime.startswith('text/'):
        # attempt to compile
        os.rename('program', 'program.cpp')
        call(['g++', 'program.cpp', '-O2', '-o', 'program', '-Wno-unused-result'])
        os.unlink('program.cpp')
        message('Compilation successful')
    else:
        message('Unknown source file (%s)' % mime, 'error')
        sys.exit(1)

def run_tests(program):
    for test in yaml.safe_load(open('def.yaml'))['tests']:
        run_test(program, test)

def run_test(program_path, test):
    if isinstance(test, basestring):
        test = {'input': 'cat %s.in' % test, 'checker': 'oicompare $DEST %s.out' % test}
    name = test.get('name', test['input'])
    if name.startswith('cat '):
        name = name[4:]
    start_time = time.time()
    message('%s' % name, 'progress')
    generator = subprocess.Popen(test['input'], shell=True,
                                 stdout=subprocess.PIPE)
    output = open('out', 'w')
    program = subprocess.Popen([program_path],
                               stdin=generator.stdout,
                               stdout=output)
    code = program.wait()
    if code != 0:
        message('Program exited with error code %d' % code, 'error')
        return
    checker = subprocess.Popen(
        test['checker'], shell=True,
        env=dict(os.environ, DEST='out'),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    for line in checker.stdout:
        if line.strip() != 'OK':
            message(line, 'error')
    if checker.wait() == 0:
        message('OK, %.1f s' % (time.time() - start_time))
    else:
        message('ANS', 'error')

def call(argv):
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, ''):
        message(line, 'warning')

def message(msg, kind='msg'):
    print json.dumps({'val': msg.rstrip(), 'type': kind})
    sys.stdout.flush()

if __name__ == '__main__':
    main()
