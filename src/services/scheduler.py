import rpyc

from settings import settings


class SchedulerClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        self.conn = rpyc.connect(self.host, self.port)
        self.proxy = self.conn.root
        return self

    def __exit__(self, *args):
        self.conn.close()

    def add_job(self, func: str, *args, **kwargs) -> str:
        """
        Add a job to the data store.

        :param func_or_task_id: either a callable or an ID of an existing task
            definition
        :param args: positional arguments to be passed to the task function
        :param kwargs: keyword arguments to be passed to the task function
        :param tags: strings that can be used to categorize and filter the job
        :param result_expiration_time: the minimum time (as seconds, or timedelta) to
            keep the result of the job available for fetching (the result won't be saved at all if that time is 0)
        :return: the ID of the newly created job
        """
        return self.proxy.add_job(func, *args, **kwargs)

    def get_job_result(self, job_id):
        return self.proxy.get_job_result(job_id)

    def get_schedules(self):
        return self.proxy.get_schedules()


def get_scheduler():
    with SchedulerClient(settings.scheduler_rpc_host, settings.scheduler_rpc_port) as client:
        yield client
