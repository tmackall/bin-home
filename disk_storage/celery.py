from __future__ import absolute_import

from celery import Celery

app = Celery('disk_storage',
             broker='amqp://',
             backend='amqp://',
             include=['disk_storage.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
