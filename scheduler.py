#!/usr/bin/python3

'''
	Program to schedule todo items from a todo list
	for a user

	CSV file format
	todo item title, expected time in seconds, priority
'''

# todo: implement process_options
# todo: allow user to set work and break lengths
# todo: implement options
#       -preempt
#       -round_robin <time in mintes>

import sys
import csv
import vlc 
import threading 

from time import sleep


todo_list = []
todo_csvfile = "todo.csv"
options = []
alg = "sjf"


def run():
	global todo_list

	# set work at 50 minutes
	wrk = 20 

	# set break time to 17 minutes
	brk = 20  

	onbreak = False

	# sleep for x seconds every update
	sleep_time = 1

	# work and break control variables
	w = 0
	b = 0
	
	# main loop
	while len(todo_list) > 0: 
		sleep(sleep_time)

		clear = "\033c"
		print(clear)
		
		if onbreak: 
			b += 1
			print("BREAK TIME!\n")
			print("Time Remaining: {}".format(format_time(brk - b)))
			
			if b == brk:
				play_alarm()
				onbreak = not onbreak
				b = 0

			continue

		print("Next Break In: {}\n".format(format_time(wrk - w)))
			
		if w == wrk:
			play_alarm()
			onbreak = not onbreak 
			w = 0
			continue
		
		todo_list[0][1] -= sleep_time

		if todo_list[0][1] <= 0:
			
			play_alarm()

			inp = ""
			while inp not in ["y", "n"]:	
				inp = input("Time's up ::: Is job {} complete (y/n)? ")

			if inp == "n":
				valid = False
			
				seconds = 0
				while not valid:
					inp = input("Add Time (#s, #m, #h): ")
					seconds, not_valid = convert_to_seconds(inp)
				
				todo_list[0][1] = seconds 
				sort_todos()
			else:
				todo_list = todo_list[1:]

		write_to_file(todo_list, 'w')
		print_todos()

		w += 1


def play_alarm():
	t = threading.Thread(target=alarm)
	t.start()			


def alarm():
	mp3 = "alarm.mp3"
	player = vlc.MediaPlayer(mp3)
	player.play()


def format_time(s):

	m = int(s / 60)
	s = s % 60

	
	h = int(m / 60)
	m = m % 60

	h = str(h).zfill(2)
	m = str(m).zfill(2)
	s = str(s).zfill(2)

	return "{}:{}:{}".format(h, m, s)


def print_todos():
	global todo_list
	global alg

	print("Algorithm: {}\n".format(alg))

	print("{:<30} {:<15} {:<15} {:<15}".format("Task", "Time Remaining", "Priority", "val/sec * 1000"))

	for todo in todo_list:
		task = todo[0]
		time_remaining = format_time(todo[1])
		priority = todo[2]
		vps = float(todo[2] / todo[1]) * 1000
		
		print("{:<30} {:<15} {:<15} {:<15}".format(task, time_remaining, priority, vps))


def spop(s, i):
	s = list(s)
	s.pop(i)
	
	return "".join(s)


def convert_to_seconds(s):
	s = s.strip()
	seconds = 0

	if len(s) == 0: 
		return 0, False	 
	
	mult = s[-1]

	if mult == 'h':
		mult = 3600
		s = spop(s, -1)
	elif mult == 'm':
		mult = 60
		s = spop(s, -1)
	elif mult == 's':
		mult = -1
		s = spop(s, -1)
	else:
		mult = 1
	
	try:
		seconds = int(s) * mult
	except ValueError:
		print("Error: could not convert {} to seconds".format(s))
		print(
					"Available formats\n" +
					"#s\n" + 
					"#m\n" +
					"#h\n"
				 )
		return 0, False 
		
	return seconds, True 

		
def add_task(task, time_remaining, priority):

	try:
		priority = int(priority)
	except ValueError:
		print("Error: Priority {} must be an integer".format(priority))
		return False
	
	seconds, valid = convert_to_seconds(time_remaining)	
	if not valid: 
		print("Error: {} was not in a legal format")
		print_usage()
		return False
	
	if priority > 3 or priority < 0:
		print("Error: Priority must fall between 0 - 3")
		return False

	todo = [task, seconds, priority]
	
	write_to_file([todo], 'a')

	return True


def process_options():
	global todo_list
	global options
	global alg

	if options[0] == "-h":
		print_usage()
		sys.exit()

	if len(options) == 0: return 

	while len(options) > 0:
		option = options[0]
		options.pop(0)

		if option == "-alg":
			if len(options) < 1: return False
			alg = options.pop(0)
			if alg not in ["sjf", "pf", "vps"]: return False
		elif option == "-a":
			if len(options) < 3: return False
			task = options.pop(0)
			time_remaining = options.pop(0)
			priority = options.pop(0)
			add_task(task, time_remaining, priority)
			sys.exit(0)
		else:
			return False
			
	return True


def sort_todos():
	global todo_list
	global alg

	for i in range(len(todo_list)):
		for j in range(i + 1, len(todo_list)):
			a = 0
			b = 0
			if alg == "sjf":
				a = todo_list[i][1]
				b = todo_list[j][1]
			elif alg == "pf":
				a = todo_list[i][2]
				b = todo_list[j][2]
			elif alg == "vps":	
				a = float(todo_list[i][1] / 4 - todo_list[i][2])
				b = float(todo_list[j][1] / 4 - todo_list[j][2])
				
		
			if a > b:
				tmp = todo_list[i]
				todo_list[i] = todo_list[j]
				todo_list[j] = tmp


def read_todos():
	global todo_csvfile

	with open(todo_csvfile, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			row[1] = int(row[1])
			row[2] = int(row[2])
		
			todo_list.append(row)


def write_to_file(todos, mode):
	global todo_csvfile

	with open(todo_csvfile, mode) as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for todo in todos:
			writer.writerow(todo)


def print_usage():
	print("Usage: scheduler.py <option> <op args> ...")
	print("Add: scheduler.py -a <task> <time> <priority>")
	print("Help: scheduler.py -h\n")

	print("-alg: the algorithm to schedule your tasks\n" +
				"      sjf - shortest job first")	

if __name__ == "__main__":

	options_valid = True

	if len(sys.argv) > 1: 
		options = sys.argv[1:]
		options_valid = process_options()

	if options_valid == False:
		print("Options Error")
		print_usage()
		sys.exit(1)
	
	read_todos()
	sort_todos()
	run()


	
