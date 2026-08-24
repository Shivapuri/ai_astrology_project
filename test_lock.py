import os, time
def acquire_lock(lockfile, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.1)
    return False

def release_lock(lockfile):
    try:
        os.remove(lockfile)
    except FileNotFoundError:
        pass

print(acquire_lock("test.lock"))
release_lock("test.lock")
