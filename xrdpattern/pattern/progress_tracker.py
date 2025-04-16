import time
from collections.abc import Collection
from typing import Iterator

import progressbar
from progressbar import ProgressBar


# ---------------------------------------------------------

class TrackedInt:
    def __init__(self, start_value : int, finish_value : int):
        if start_value >= finish_value:
            raise ValueError(f'Start value {start_value} must be less than finish value {finish_value}')
        self._value : int = start_value
        self.progressbar = ProgressBar(min_value=start_value, max_value=finish_value)
        self.progressbar.update()

    def increment(self, to_add : int = 1):
        self._value += to_add

        if self.progressbar.finished():
            return

        if self._value >= self.progressbar.max_value:
            self.finish()
            return

        self.progressbar.update(value=self._value)

    def finish(self):
        self.progressbar.finish()

    def is_finished(self) -> bool:
        return self.progressbar.finished()

    def get_value(self) -> int:
        return self._value

    @classmethod
    def wrap_output(cls):
        progressbar.streams.wrap_stderr()
        progressbar.streams.wrap_stdout()

    # ------------------
    # int operators

    def __iadd__(self, other):
        if not isinstance(other, int):
            raise ValueError("Only integers can be added to a TrackedInt.")
        self.increment(to_add=other)
        return self

    def __add__(self, other):
        raise NotImplementedError(f'Can only add to tracked integer in place')

    def __eq__(self, other):
        if isinstance(other, TrackedInt):
            return self._value == other._value
        elif isinstance(other, int):
            return self._value == other
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, TrackedInt):
            return self._value < other._value
        elif isinstance(other, int):
            return self._value < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, TrackedInt):
            return self._value <= other._value
        elif isinstance(other, int):
            return self._value <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, TrackedInt):
            return self._value > other._value
        elif isinstance(other, int):
            return self._value > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, TrackedInt):
            return self._value >= other._value
        elif isinstance(other, int):
            return self._value >= other
        return NotImplemented

    def as_range(self) -> Iterator[int]:
        while self._value < int(self.progressbar.max_value):
            yield self._value
            self.increment(to_add=1)

    def __str__(self):
        return str(self._value)




class TrackedCollection(Iterator):
    def __init__(self, iterable : Collection):
        self.inner : Iterator = iter(iterable)
        self.tracking_int : TrackedInt = TrackedInt(start_value=0, finish_value=len(iterable))

    def __next__(self) -> object:
        self.tracking_int.increment(to_add=1)
        return next(self.inner)


if __name__ == "__main__":
    this = TrackedInt(start_value=1, finish_value=10)
    for k in this.as_range():
        print(f'k = {k}')
        time.sleep(0.1)

    for j in TrackedCollection(range(10)):
        time.sleep(0.1)
        print(f'j = {j}')
