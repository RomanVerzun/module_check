import numpy as np
import collections


dq = collections.deque(range(10), maxlen=10)
dq.appendleft(-50)
print(dq)
print(dq.rotate(3))
print(dq)