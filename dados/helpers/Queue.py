import json


class Queue:
    def __init__(self, max_size: int=0):
        self.__base_sequence: list = []
        self.__max_size: int = max_size

    @staticmethod
    def from_list(origin_list: list, list_size_max_size: bool=False):
        size = 0
        if list_size_max_size:
            size = len(origin_list)

        q = Queue(max_size=size)

        origin_list.reverse()
        for element in origin_list:
            q.put(element)
        return q

    @property
    def length(self):
        return len(self.__base_sequence)

    def to_list(self):
        return self.__base_sequence

    def clone(self):
        return Queue.from_list(self.__base_sequence)

    def extend_from_list(self, extension: list):
        self.__base_sequence = extension + self.__base_sequence

    def get(self, base = False):
        if self.length == 0:
            raise EmptyQueueAccessAttemptException

        if(base == False):
            return self.__base_sequence.pop(-1)
        else:
            return self.__base_sequence[:-1]

    def put(self, element):
        if self.__max_size and self.length == self.__max_size:
            raise FullQueueInsertionAttemptException

        self.__base_sequence.insert(0, element)

    def to_json(self):
        return json.dumps(self.__base_sequence)

    def from_json(self, json_obj):
        self.__base_sequence = json.loads(json_obj)

    def __repr__(self):
        return f"Queue: {self.__base_sequence}"

    def __iter__(self):
        return QueueIter(self)


class QueueIter:
    def __init__(self, queue: Queue):
        self.queue = queue

    def __iter__(self):
        return self

    def __next__(self):
        if self.queue.length == 0:
            raise StopIteration
        return self.queue.get()


class FullQueueInsertionAttemptException(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Queue is full"

    def __repr__(self):
        return self.msg


class EmptyQueueAccessAttemptException(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "Queue is empty"

    def __repr__(self):
        return self.msg
