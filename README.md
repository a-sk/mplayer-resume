#mplayer-resume.py

Watch the video you want with this script and it will remember its playback
position for next time.
	
	usage: mplayer-resume.py [-h] [-r int] fn ...
	
	mplayer-resume
	
	positional arguments:
	  fn                    file to play
	  flags                 mplayer arguments
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -r int, --resume int  time difference in seconds, negative number means a rollback
