import heapq


class PriorityQueue(object):
    def __init__(self):
        self._queue = []
        self._index = 0

    def __repr__(self):
        return "{0}".format(self._queue)

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        if self._queue:
            return heapq.heappop(self._queue)[-1]
        else:
            return None

    def clear(self):
        del self._queue[:]
        self._index = 0

