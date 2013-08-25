#!/usr/bin/python

import sys
import os
import json
import argparse
import subprocess

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
        return json.dump(data, fp)

def save_position(file_name, position):
    cache = _get_cache()
    cache[file_name] = float(position)
    _save_cache(cache)

def get_position(file_name):
    cache = _get_cache()
    if cache.get(file_name):
        return cache[file_name]

def parse_args():
    parser = argparse.ArgumentParser(description='mplayer-resume')
    parser.add_argument('file', nargs=1, type=str, metavar='filename', help='file to play')
    parser.add_argument('-r', '--resume', nargs=1, type=int, metavar='int', default=2,
            help='time difference in seconds, negative number means a rollback')
    parser.add_argument('flags', nargs=argparse.REMAINDER, default=None,
            metavar='margs', help='mplayer arguments')

    return (vars(parser.parse_args()), parser)

def main():
    args, parser = parse_args()
    file_name = args['file'][0]
    resume = args['resume']
    if type(resume) == list:
        resume = resume[0]

    maybe_mkdir(os.path.dirname(DUMP_FILE))

    resume_time = get_position(file_name) or 0
    if resume_time:
        resume_time = float(resume_time + resume)

    cmd = ' '.join([mplayer, '-ss', str(resume_time), file_name] + args['flags'])
    child = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    mplayer_output = str()
    while True:
        out = child.stderr.read(1).decode()
        if out == '' and child.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()
            mplayer_output += out

    try:
        pos = float(parse_mplayer_output(mplayer_output))
    except:
        sys.exit()
    save_position(file_name, pos)

if __name__ == '__main__':
    main()

# vim: expandtab
