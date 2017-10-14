# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue


class Worker(Thread):

    def __init__(self, target, args):
        Thread.__init__(self)
        self._target = target
        self._args = args
        self._return = None

    def run(self):
        self._return = self._target(*self._args)

    def get_result(self):
        Thread.join(self)
        return self._return


class TasksManager:

    def __init__(self, queue=None):
        self._queue = queue if queue else Queue()

    @property
    def queue(self):
        return self._queue

    def new_task(self, target, args=()):
        thread = Worker(target=target, args=args)
        thread.start()
        self._queue.put(thread)

    def next_result(self):
        return self._queue.get().get_result()

    def results_list(self):
        results = list()
        while not self._queue.empty():
            results.append(self._queue.get().get_result())

        return results
