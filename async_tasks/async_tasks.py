import functools

import concurrent
from collections import Set
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime
from threading import Lock

tasks = []


class Logger(object):
    def on_end_executing(self, task, seconds):
        print("task %s is completed in %s seconds" % (task, seconds))

    def on_start_executing(self, task):
        print("task %s is started" % task)

    def on_added_to_queue(self, task):
        print("task %s is added to queue" % task)

    def on_build_start(self, tasks):
        print('build started %s' % Task.str_task_list(tasks))

    def on_build_end(self, tasks, seconds):
        print('build ended %s in %s seconds ' % (Task.str_task_list(tasks), seconds))

    def log_in_task(selt, task, obj):
        print('   %s:  %s' % (task.name, str(obj)))


class LoggerWrapper(object):

    def __init__(self, logger):
        self.logger = logger
        self.messages = {}
        self.print_lock = Lock()

    def on_start_executing(self, task):
        self.messages[task] = []

    def on_end_executing(self, task, seconds):
        self.log_messages_of_task(task, self.messages[task], seconds)

    def on_build_end(self, tasks, seconds):
        self.logger.on_build_end(tasks, seconds)

    def on_build_start(self, tasks):
        self.logger.on_build_start(tasks)

    def on_added_to_queue(self, task):
        self.logger.on_added_to_queue(task)

    def log_in_task(self, task, obj):
        self.messages[task].append(obj)

    def log_messages_of_task(self, task, objects, seconds):
        with self.print_lock:
            self.logger.on_start_executing(task)
            for o in objects: self.logger.log_in_task(task, o)
            self.logger.on_end_executing(task, seconds)


class Task(object):
    def __init__(self, func, dependencies):
        self.func = func
        self.name = func.__name__
        self.dependencies = dependencies
        tasks.append(self)

    def __call__(self, *args, **kwargs):
        if self.logger:
            self.logger.on_start_executing(self)
        t = datetime.now()
        r = self.func.__call__(lambda s: self.logger.log_in_task(self, s))
        if self.logger:
            self.logger.on_end_executing(self,  (datetime.now() - t).seconds)
        return r

    @classmethod
    def is_task(cls, obj):
        return isinstance(obj, cls)

    def set_future(self, future):
        self.future = future

    def set_logger(self, logger):
        self.logger = logger

    @classmethod
    def str_task_list(cls, tasks):
        def str_item(index, dep, size):
            if index is 0:
                if index is not size - 1:
                    return '(' + dep.name + ', '
                else:
                    return '(' + dep.name + ')'
            elif index is not size - 1:
                return dep.name + ', '
            else:
                return dep.name + ')'

        return functools.reduce(lambda ite_list, index_dep: ite_list + str_item(index_dep[0], index_dep[1], len(tasks)),
                                enumerate(tasks), '')

    def __str__(self):
        return self.name + Task.str_task_list(self.dependencies)


def task(*dependencies):
    for d in filter(lambda x: not Task.is_task(x), dependencies):
        raise Exception("%s is not a task. Each dependency should be a task." % d.__str__())
    return lambda fn: Task(fn, dependencies)


def inner_run(current_task, future_tasks, executor, notifer):
    for d in current_task.dependencies:
        if d not in future_tasks:
            notifer.on_added_to_queue(d)
        future_d = inner_run(d, future_tasks, executor, notifer)
        future_tasks.add(future_d)

    for f in concurrent.futures.as_completed(map(lambda t: t.future, current_task.dependencies)):
        f.result()

    if current_task not in future_tasks:
        current_task.set_logger(notifer)
        current_task.future = executor.submit(current_task)
        future_tasks.add(current_task)
    return current_task


def run(task_, workers, logger=Logger()):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        run_on_executor(task_, executor, logger)


def get_all_dependecies(task):
    tasks = []
    for d in task.dependencies:
        tasks.append(d)
        for d2 in get_all_dependecies(d):
            tasks.append(d2)
    s = {}
    for t in tasks:
        s[t] = []
    return s.keys()


def run_on_executor(task_, executor, logger=Logger()):
    logger_wrapper = LoggerWrapper(logger)

    deps = list(get_all_dependecies(task_))
    deps.append(task_)

    logger_wrapper.on_build_start(deps)

    def stater():
        futured_task = inner_run(task_, set(), executor, logger_wrapper)
        return futured_task.future.result()

    t = datetime.now()

    stater()

    logger_wrapper.on_build_end(deps, (datetime.now() - t).seconds)
