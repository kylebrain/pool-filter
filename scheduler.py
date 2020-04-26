import abc
import threading
import sched
import database
import firmware
from datetime import datetime
import time


class Scheduler():

    def __init__(self):
        self._lock = threading.Lock()
        self._current_event = None
        self._next_event = None

        self._run_event_thread = threading.Thread(target=self._run_event, daemon=True)
        self._run_event_thread.start()

        with self._lock:
            self.update_next_event()


    def _run_event(self):
        while True:
            with self._lock:
                if self._next_event is not None and self._next_event.event_time.timestamp() <= time.time():
                    event = self._next_event
                    self._next_event = None
                    event.invoke(self)
            time.sleep(1)


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
        REQUIRES LOCK
        '''

        if self._next_event is not None:
            self._next_event = None

        self._schedule_event(event)


    def update_next_event(self):
        '''
        REQUIRES LOCK
        '''
        next_event = database.get_next_program()
        if next_event is not None:
            self._next_event = None
            self._schedule_event(next_event)


    def _schedule_event(self, event):
        '''
        Schedules the passed event
        REQUIRES LOCK
        '''

        if not isinstance(event, Scheduler.ProgramEvent):
            raise TypeError("Scheduler _schedule_event not passed an event, had type %s" % (type(event).__name__,))

        if self._next_event is not None:
            raise ValueError("Cannot schedule event if the is already one scheduled. Please remove it first!")

        self._next_event = event


    class ProgramEvent():
        def __init__(self, event_time):
            self.event_time = event_time


        def invoke(self, scheduler):
            scheduler._current_event = self


    class StartEvent(ProgramEvent):
        def __init__(self, event_time, duration, speed):
            super().__init__(event_time)
            self.duration = duration
            self.speed = speed


        def invoke(self, scheduler):
            '''
            Turns on filter
            Adds stop event
            '''
            super().invoke(scheduler)
            firmware.set_speed(self.speed)
            stop_event = Scheduler.StopEvent(datetime.now() + self.duration)
            scheduler._schedule_event(stop_event)


    class StopEvent(ProgramEvent):
        def invoke(self, scheduler):
            '''
            Turns off filter
            Adds start event for next program
            '''
            super().invoke(scheduler)
            firmware.set_speed(0)
            next_event = database.get_next_program()
            if next_event is not None:
                scheduler._schedule_event(next_event)

