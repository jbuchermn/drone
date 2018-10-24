from subprocess import Popen, PIPE

command = "/usr/bin/sudo /sbin/shutdown --halt now"
process = Popen(command.split(), stdout=PIPE)
process.communicate()
