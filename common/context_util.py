class TestContext:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def update(self, data):
        self._data.update(data)

    def clear(self):
        self._data.clear()

    def all(self):
        return self._data.copy()


test_context = TestContext()
