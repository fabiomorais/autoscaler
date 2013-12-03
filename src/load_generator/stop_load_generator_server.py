import cStringIO
import pycurl
import subprocess
import sys

file_pattern = str(sys.argv[1])

master_key = file_pattern

pids = []

command = []
command.append('ps')
command.append('-ef')

result    = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
result    = result.split('\n')
lines     = filter(lambda x: master_key in x , result)

for i in range(0,len(lines)):
	new_line = ';'.join(lines[i].split()).split(';')
	pids.append(new_line[1])

command = []
command.append('kill')
command.append('-9')

for i in range(0,len(pids)):
	command.append(pids[i])

result    = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]

print 'done'
