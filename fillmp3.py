#!/usr/bin/python
import argparse
import os
import random
import re
import shutil
import sys
import urllib.request

units = {"ki" : 2**10, "mi" : 2**20, "gi": 2**30, "k" : 10**3, "m" : 10**6, "g" : 10**9}

def main():
	parser = argparse.ArgumentParser(description='Fill a music player with random songs.')

	parser.add_argument('-f', '--fill', action='store_true', default=True, dest='fill', 
		help='Fills all the remaining free space on the device')
	parser.add_argument('-n', '--number', action='store', dest='number', 
		default=-1, 
		help='Copies a certain number of songs')
	parser.add_argument('-s', '--size', action='store', type=str, dest='size',
		help="Only copies up to a maximum amount of data in bytes. Accepts ISO/IEC unit abbreviations, e.g. MB, KiB etc")
	parser.add_argument('-p', '--playlist', action='store', type=argparse.FileType('r'), dest='playlist')
	parser.add_argument('-t', '--try-smaller-files', action='store_const', const=-1, default=0,
		dest='try_small', metavar='tries',
		help="Continues to try and find a smaller file to copy if one file doesn't fit.  May be slow")
	parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', 
		help="Displays the filenames of the copied files")

	parser.add_argument('target', metavar='target', type=str, help='The target directory on the device')
	
	args = parser.parse_args()
	fill(args)


def fill(args):
	files = parse_playlist(args.playlist)
	files_left = args.number
	space_left = 0

	if(args.fill):
		st = os.statvfs(args.target)
		space_left = st.f_bavail * st.f_frsize
	
	if(args.size):
		space_left = parse_size(args.size)
	#print(space_left)

	tries = 0
	while(files_left != 0):
		file_name = random.choice(list(files.keys()))
		size = files[file_name]

		del files[file_name]

		if(size > space_left):
			if(tries >= args.try_small):
				break
			else:
				tries += 1
				continue

		shutil.copy(file_name, args.target)
		space_left -= size
		files_left -= 1
		tries = 0
		
		if(args.verbose):
			print(file_name)


def parse_playlist(playlist):
	files = dict()
	for line in playlist:
		
		if(line[0] == '#'):
			continue

		file_name = urllib.parse.unquote(urllib.parse.urlparse(line.strip()).path)
		
		files[file_name] = os.stat(file_name).st_size

	return files

def parse_size(size_string):
	pattern = r"\s*(?P<number>[0-9]+)\s*((?P<prefix>[kmg]i?)?b?)?\s*"
	reobject = re.compile(pattern, re.I)
	match = reobject.match(size_string)
	if(not match):
		print("Incorrect size specification: ", size_string)
		quit()
	
	number = int(match.group("number"))
	prefix = match.group("prefix").lower()
	if(prefix in units):
		number *= units[prefix]
	return number


if __name__ == "__main__":
	main()

