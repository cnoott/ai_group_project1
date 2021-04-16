class A:
    blah1_is_beautiful = True
    blah2_is_beautiful = True
    blah3_is_beautiful = True

    def __init__(self):
        self.blah1_is_beautiful = A.blah1_is_beautiful
        self.blah2_is_beautiful = A.blah2_is_beautiful
        self.blah3_is_beautiful = A.blah3_is_beautiful


class B:
    def __init__(self):
        self.null_is_null = None

    def change_some_values(self):
        A.blah1_is_beautiful = False
        A.blah2_is_beautiful = False
        A.blah3_is_beautiful = False


obj1 = B()
obj1.change_some_values()
obj2 = A()
print(obj2.blah1_is_beautiful)