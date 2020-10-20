class Stack(object):
    def __init__(self, maxlength=27):
        self.stack = []
        self.maxlength = maxlength
        self.top = 0

    def push(self, value):  # 进栈
        self.stack.append(value)
        if self.top >= self.maxlength:
            for i in self.stack[:-27]:
                self.stack.remove(i)
        self.top += 1

    def pop(self):  # 出栈
        if self.top == 0:
            raise StackEmptyException('Your stack is empty!')
        self.top -= 1
        el = self.stack[self.top]
        return el

    def is_empty(self):  # 如果栈为空
        return bool(self.stack)

    def top(self):
        # 取出目前stack中最新的元素
        return self.stack[-1]


class StackEmptyException(Exception):
    """自定义一个栈空出异常"""
    pass
