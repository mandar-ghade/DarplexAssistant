from time import perf_counter, sleep
from typing import Callable

class Data:
    i = 0

class TaskTimer:
    def __init__(self,  func: Callable, seconds: float) -> None:
        self.timeout = seconds
        self.func = func
        self.is_cancelled = False

    def start(self) -> None:
        while(self.func()) and not self.is_cancelled:
            sleep(self.timeout)

    def cancel(self) -> None:
        self.is_cancelled = True

def test() -> bool:
    Data.i += 1
    print(f'Test: {Data.i}')
    return True

timer_obj = TaskTimer(test, 1)
timer_obj.start()
sleep(5)
timer_obj.cancel()
