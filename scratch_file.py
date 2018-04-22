def f():
    x = int("four")

try:
    f()
except ValueError as e:
    print("error: {}".format(repr(e)))


print("Done")