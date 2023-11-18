from celery import shared_task

@shared_task(ignore_result=False)
def sayHello():
    return "SayHello"


