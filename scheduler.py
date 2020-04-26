import abc
import threading
import sched
import database

class Scheduler():

    def __init__(self):
        self._lock = threading.Lock()
        self._scheduler = sched.scheduler()
        self._current_event = None
        self._next_event = None
        self._next_event_thread = None

        self._schedule_event(database.get_next_program())


    def acquire(self):
        self._lock.acquire()


    def release(self):
        self._lock.release()


    def __enter__(self):
        self.acquire()


    def __exit__(self, type, value, traceback):
        self.release()


    def override_current_event(self, event):
        '''
        Cancels the current next event
        Invokes the passed event
        '''
        pass


    def _schedule_event(self, event):
        '''
        Schedules the passed event
        '''
        pass


    class ProgramEvent():
        def __init__(self, event_time):
            self.event_time = event_time


        @abc.abstractmethod
        def invoke(self, *args, **kwargs):
            pass


    class StartEvent(ProgramEvent):
        def __init__(self, event_time, duration, speed):
            super().__init__(event_time)
            self.duration = duration
            self.speed = speed


        def invoke(self, duration, speed):
            '''
            Turns on filter
            Adds stop event
            '''
            pass


    class StopEvent(ProgramEvent):
        def invoke(self):
            '''
            Turns off filter
            Adds start event for next program
            '''
            pass

