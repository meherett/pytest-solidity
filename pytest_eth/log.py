#!/usr/bin/env python3

from collections import Mapping


class Log(Mapping):
    
    def __new__(cls, event, args):
        obj = super().__new__(cls)
        obj.event = event
        obj.args = args
        return obj

    def __eq__(self, other):
        if not isinstance(other, Log):
            return False
        if self.event != other.event:
            return False
        return self.args == other.args

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    def __getitem__(self, key):
        return self.args[key]
