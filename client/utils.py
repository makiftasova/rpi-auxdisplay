import time
import threading


class LoopTask(threading.Thread):
    def __init__(self, interval=5, sleep_length=0.2, group=None, name=None, args=(), kwargs=None,
                 *, daemon=None):
        """
        Executes self.loop() method until explicitly canceled. override LoopTask.loop() method in a
        subclass to use LoopTask. use LoopTask.cancel() method to stop task.

        :param interval: wait after each loop, in minutes. could be a floating point value
        :param sleep_length: time interval to check if thread should be stopped, in seconds,
        could be a floating point value
        """
        super(LoopTask, self).__init__(group=group, name=name, args=args, daemon=daemon,
                                       kwargs=kwargs)
        self.__looptask_interval = int(interval * 60)
        self.__looptask_loop = True
        self.__looptask_sleep_time = sleep_length

    def loop(self):
        """
        Override this method to use LoopTask. THis method will be called after given interval
        :return:
        """
        pass

    def run(self):
        while self.__looptask_loop:
            self.loop()
            __sleep_begin = time.time()
            while True:
                if time.time() - __sleep_begin >= self.__looptask_interval:
                    break
                if self.__looptask_loop is False:
                    break
                time.sleep(self.__looptask_sleep_time)

    def cancel(self):
        self.__looptask_loop = False

    def is_stopped(self):
        return self.__looptask_loop is False
