import functools
import unittest
from time import sleep
from .. import async_tasks


class TestLogger(async_tasks.Logger):
    def log_in_task(selt, task, obj):
        pass

    def str_task(self, task):
        return ""

    def on_build_end(self, tasks, seconds):
        pass

    def on_end_executing(self, task, seconds):
        pass

    def on_added_to_queue(self, task):
        pass

    def on_build_start(self, tasks):
        pass

    @classmethod
    def str_task_list(cls, tasks):
        return ""

    def on_start_executing(self, task):
        pass


class TestBuildSimple(unittest.TestCase):

    def make_task_delay(number):
        def returnWithWhait(logger):
            sleep(1)
            return number
        return async_tasks.Task(returnWithWhait, [])

    def make_task(number):
        return async_tasks.Task(lambda logger: number, [])

    def test_single_thread_result(self):
        r = range(0, 100)
        numbers = list(map(self.make_task, r))

        @async_tasks.task(*numbers)
        def return_sum(logger):
            return functools.reduce(lambda a, b: a + b.result, numbers, 0)

        @async_tasks.task(return_sum)
        def exit(logger):
            return return_sum.result

        async_tasks.run(exit, 1, TestLogger())
        self.assertEqual(return_sum.result, sum(r))

    def test_multi_thread_result(self):
        r = range(0, 100)
        numbers = list(map(self.make_task_delay(), r))

        @async_tasks.task(*numbers)
        def return_sum(logger):
            return functools.reduce(lambda a, b: a + b.result, numbers, 0)

        @async_tasks.task(return_sum)
        def exit(logger):
            return return_sum.result

        async_tasks.run(exit, 100, TestLogger())
        self.assertEqual(return_sum.result, sum(r))


if __name__ == "__main__":
    unittest.main(verbosity=2)

