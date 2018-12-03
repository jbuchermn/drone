from subprocess import Popen, PIPE

def shutdown():
    print("Shutting system down...")
    command = "/usr/bin/sudo /sbin/shutdown --halt now"
    process = Popen(command.split(), stdout=PIPE)
    process.communicate()


def auto_hotspot(force=False):
    print("Calling /usr/bin/autohotspot %s..." % ("force" if force else ""))
    command = "/usr/bin/sudo /usr/bin/autohotspot %s" % ("force" if force
                                                         else "")
    process = Popen(command.split(), stdout=PIPE)
    process.communicate()
