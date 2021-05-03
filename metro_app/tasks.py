import time

def test_task(delay):
    print('Starting task')
    time.sleep(delay)
    print('Ending task')
    return 0
