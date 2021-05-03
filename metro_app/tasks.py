import time
from django_rq import job

@job
def test_task(delay):
    print('Starting task')
    time.sleep(delay)
    print('Ending task')
    return 0

@job('simulations')
def test_task_simulation(delay):
    print('Starting simulation task')
    time.sleep(delay)
    print('Ending simulation task')
    return 0
