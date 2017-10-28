# -*- coding: utf-8 -*-

import unittest
from core.tasks import Worker, TasksManager, TimeoutError
import time
import random


class TasksTest(unittest.TestCase):
    """ Test Case des méthodes du module 'tasks' """

    def test_worker(self):

        def add(a, b):
            return a + b

        worker = Worker(add, (2, 3))
        worker.start()
        self.assertEqual(worker.get_result(), 5)

        def long_add(a, b):
            time.sleep(13)  # This test will be long to run
            return a + b

        worker2 = Worker(long_add, (4, 5))
        worker2.start()
        with self.assertRaises(TimeoutError):
            worker2.get_result()

    def test_task_manager(self):

        def task(a, b):
            time.sleep(random.random())
            return a + b

        tm = TasksManager()
        tm.new_task(task, (5, 1))
        self.assertEqual(tm.next_result(), 6)

        tm.new_task(task, (2, 0))
        tm.new_task(task, (3, 4))
        tm.new_task(task, (1, 3))
        self.assertEqual(tm.results_list(), [2, 7, 4])
