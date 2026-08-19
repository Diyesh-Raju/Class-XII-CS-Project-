from __future__ import annotations

class ClassA:
    # Use quotes around ClassB because it is defined below
    def process_data(self, b: "ClassB"):
        print(b.value)


class ClassB:

    def __init__(self):
        self.value = 42
a=ClassA()
b=ClassB()
a.process_data(b=b)
x=[1,2,3,4]
y=[5,6,7]
print(x+y)
a={"u":1}
z=y.index(6)
print(a["u"],z)