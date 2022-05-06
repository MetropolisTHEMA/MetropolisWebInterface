from django.core.files.storage import default_storage
from datetime import timedelta
from .models import BackgroundTask


def str_hook(task):
    """Hook for async task that return a string."""
    db_task = BackgroundTask.objects.get(id=task.id)
    db_task.time_taken = timedelta(seconds=task.time_taken())
    db_task.result = str(task.result)
    if task.success:
        db_task.status = BackgroundTask.FINISHED
    else:
        db_task.status = BackgroundTask.FAILED
    # Delete files in the arguments.
    for arg in task.args:
        if isinstance(arg, str) and default_storage.exists(arg):
            default_storage.delete(arg)
    db_task.save()
