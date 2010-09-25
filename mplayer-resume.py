#!/usr/bin/python3
#TODO: refactor

import sys
from os.path import expanduser
import pickle
from subprocess import check_output
from os.path import exists

DUMP_FILE = "{0}/.mplayer_resume".format(expanduser("~"))
file_name = sys.argv[1]
mplayer = "/usr/bin/mplayer"
epsilon = 2 # time to roll back
flags = ['-fs', '-utf8']

def get_old_settings():
    if not exists(DUMP_FILE):
        return dict()
    with open(DUMP_FILE, 'rb') as f:
        data = pickle.load(f)
    return data

parse_mplayer_output = lambda x: x.split("A:")[-1].split("V:")[0].strip()

#def parse_mplayer_output(mp_out):
    #time_to_resume = mp_out.split("A:")[-1].split("V:")[0].strip()
    ##if time_to_resume.isdigit():
        ##time_to_resume = '0'
    #return time_to_resume

def dump_settings(new_settings, old_settings):
    old_settings.update(new_settings)
    with open(DUMP_FILE, 'wb') as f:
        pickle.dump(old_settings, f, pickle.HIGHEST_PROTOCOL)

# get old resume time from file
time_to_resume = get_old_settings().get(file_name, '0')
# roll it back
time_to_resume = str(float(time_to_resume) - epsilon)

# compose mplayer commad
cmd = [mplayer, '-ss', time_to_resume, file_name] + flags
# wait until it finish
mplayer_output = str(check_output(cmd))

# get new resume time
time_to_resume = parse_mplayer_output(mplayer_output)
settings_to_pickle = {file_name: time_to_resume}

# write resume time to file
dump_settings(settings_to_pickle, get_old_settings())
