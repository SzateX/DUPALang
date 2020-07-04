class Stack(object):
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]


class CallStack(Stack):
    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self.items))
        s = f'CALL STACK\n{s}\n'
        return s

    def __repr__(self):
        return self.__str__()