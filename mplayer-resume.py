#!/usr/bin/python

import sys
import os
import json
import argparse
import subprocess
import time

DUMP_FILE = os.path.expandvars("$HOME/.cache/mplayer/resume-cache")
mplayer = "/usr/bin/mplayer"

parse_mplayer_output = lambda x: x.split("A:")[-1].split("V:")[0].strip()

def maybe_mkdir(path):
    if not os.path.exists(path):
        return os.makedirs(path)

def _get_cache():
    if not os.path.exists(DUMP_FILE):
        return {}
    with open(DUMP_FILE) as fp:
        return json.load(fp)

def _save_cache(data):
    with open(DUMP_FILE, 'w') as fp:
        return json.dump(data, fp, indent=2)

def save_position(file_name, position):
    cache = _get_cache()
    cache[file_name] = float(position)
    _save_cache(cache)

def reset_position(file_name):
    cache = _get_cache()
    cache.pop(file_name)
    _save_cache(cache)

def get_position(file_name):
    cache = _get_cache()
    if cache.get(file_name):
        return cache[file_name]

def parse_args():
    parser = argparse.ArgumentParser(description='mplayer-resume')
    parser.add_argument('-r', '--resume', nargs=1, type=int, metavar='int', default=-2,
            help='time difference in seconds, negative number means a rollback')
    parser.add_argument('flags', nargs=argparse.REMAINDER, default=None,
            metavar='margs', help='mplayer arguments')

    return (vars(parser.parse_args()), parser)

def run_mplayer(args):
    fifo_file = "/tmp/mplayer-%d" % (time.time())
    os.mkfifo(fifo_file)
    cmd = [mplayer, '-slave', '--input=file=%s' % (fifo_file)] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        retcode = p.poll()
        stdout = p.stdout.readline().decode(sys.stdout.encoding)
        stderr = p.stdout.readline().decode(sys.stderr.encoding)
        yield stdout, stderr, fifo_file
        if retcode is not None:
            os.remove(fifo_file)
            break

def main():
    args, parser = parse_args()
    resume = args['resume']
    if type(resume) == list: resume = resume[0]
    mflags = args['flags']
    file_name = None

    maybe_mkdir(os.path.dirname(DUMP_FILE))

    for stdout, stderr, fifo_file in run_mplayer(mflags):
        sys.stdout.write(stdout)
        sys.stdout.write(stderr)

        if stderr.endswith("Exiting... (End of file)\n"):
            reset_position(file_name)
            return

        if stdout.startswith('A:'):
            lastpos = stdout

        if stderr.startswith('A:'):
            lastpos = stderr

        if stderr.startswith('Playing '):
            file_name = os.path.abspath(stderr[8:-2])

            resume_time = get_position(file_name) or 0
            resume_time = resume_time + resume

            with open(fifo_file, 'w') as fifo:
                fifo.write('seek %d\n' % resume_time)

    if file_name:
        pos = parse_mplayer_output(lastpos)
        save_position(file_name, pos)

if __name__ == '__main__':
    main()
# vim: expandtab
