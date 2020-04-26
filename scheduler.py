import abc
import threading
import sched
import database
import firmware
from datetime import datetime
import time


def run_schedule(scheduler):
    while(True):
        if not scheduler.empty():
            scheduler.run()


class Scheduler():

    def __init__(self, app):
        self.app = app
        self._lock = threading.Lock()
        self._scheduler = sched.scheduler()
        self._current_event = None
        self._next_event_thread = None


        next_event = database.get_next_program()
        if next_event is not None:
            self._schedule_event(next_event)

        threading.Thread(target=run_schedule, args=(self._scheduler, ), daemon=True).start()


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

        if self._next_event_thread is not None:
            self._scheduler.cancel(self._next_event_thread)
            self._next_event_thread = None

        self._schedule_event(event)


    def _schedule_event(self, event):
        '''
        Schedules the passed event
        '''

        if not isinstance(event, Scheduler.ProgramEvent):
            raise TypeError("Scheduler _schedule_event not passed an event, had type %s" % (type(event).__name__,))

        if self._next_event_thread is not None and self._next_event_thread in self._scheduler.queue:
            raise ValueError("Cannot schedule event if the is already one scheduled. Please cancel it first!")

        if isinstance(event, Scheduler.StartEvent):
            self._next_event_thread = self._scheduler.enter(event.event_time.timestamp() - time.time(), 0, event.invoke, argument=(self, event.duration, event.speed))
        elif isinstance(event, Scheduler.StopEvent):
            self._next_event_thread = self._scheduler.enter(event.event_time.timestamp() - time.time(), 0, event.invoke, argument=(self,))
        else:
            raise TypeError("Scheduler _schedule_event does not handle derived ProgramEvent class %s" % (type(event).__name__,))


    class ProgramEvent():
        def __init__(self, event_time):
            self.event_time = event_time


        def invoke(self, scheduler, *args, **kwargs):
            scheduler._current_event = self


    class StartEvent(ProgramEvent):
        def __init__(self, event_time, duration, speed):
            super().__init__(event_time)
            self.duration = duration
            self.speed = speed


        def invoke(self, scheduler, duration, speed):
            '''
            Turns on filter
            Adds stop event
            '''
            super().invoke(scheduler)
            firmware.set_speed(speed)
            stop_event = Scheduler.StopEvent(datetime.now() + duration)
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

