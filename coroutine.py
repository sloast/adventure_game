from collections import deque
from typing import List, Dict, Callable, Type


class Override: pass
class Wait: pass
class Halt: pass
class Allow: pass
class TextOutput: pass
class MapAction: pass
class Cancel: pass


class Coroutine:
    active: List['Coroutine'] = []
    suspended: Dict[Type, deque] = {}
    input_enabled: bool = True

    def __init__(self,
                 func: Callable,
                 iterations: int,
                 singular_type: Type = None,
                 duplicate_action: Type = Override,
                 forbid_input: bool = False,
                 delay: int = 0,
                 jump: int = 1,
                 delay_first: bool = False,
                 execute: bool = True,
                 start_func: Callable = None,
                 end_func: Callable = None,
                 **kwargs):
        self.func = func
        self.start_func = start_func
        self.end_func = end_func
        self.iterations: int = iterations
        self.i: int = 0
        self.delay = delay
        self.jump = jump
        self.time_remaining = delay if delay_first else 0
        self.type = singular_type
        self.action = duplicate_action
        self.forbid_input = forbid_input
        self.kwargs = kwargs
        if execute:
            self.add(self)

    def execute(self):
        self.add(self)

    @classmethod
    def check_input(cls):
        for item in cls.active:
            if item.forbid_input:
                cls.input_enabled = False
                return False
        cls.input_enabled = True
        return True

    @classmethod
    def input(cls):
        return cls.input_enabled

    @classmethod
    def remove(cls, item: 'Coroutine') -> None:
        cls.active.remove(item)
        cls.check_input()

    @classmethod
    def running(cls, ctype: Type) -> bool:
        if ctype is None:
            return False
        for item in cls.active:
            if item.type == ctype:
                return True
        return False

    @classmethod
    def purge(cls, ctype: Type):
        if ctype is None:
            return
        for item in cls.active:
            if item.type == ctype:
                cls.active.remove(item)

    @classmethod
    def add(cls, item: 'Coroutine') -> bool:
        if item.type:
            if item.action == Override:
                cls.purge(item.type)
            elif item.action == Halt:
                return False
            elif item.action == Wait:
                pass

        cls.active.append(item)
        cls.check_input()
        if item.start_func:
            item.start_func()
        return True

    def run(self) -> bool:
        out = self.func(self.i, self.iterations, **self.kwargs)
        self.i += self.jump
        if out == -1 or self.i >= self.iterations:
            self.remove(self)
            if self.type in self.suspended and len(self.suspended[self.type]) > 0:
                self.add(self.suspended[self.type].popleft())
            if self.end_func:
                self.end_func()
            return True
        else:
            self.time_remaining = self.delay if out is None else out
            return False

    def ready(self):
        return self.time_remaining <= 0

    def tick(self):
        self.time_remaining -= 1

    @classmethod
    def none(cls):
        pass

    @classmethod
    def update(cls):
        for item in cls.active:
            item.run() if item.ready() else item.tick()

    @classmethod
    def invoke(cls, func: Callable, delay: int = 0, **kwargs):
        Coroutine(func, 1, delay=delay, delay_first=True, **kwargs)
