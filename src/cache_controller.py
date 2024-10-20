import redis 

class CacheController:
    def __init__(self, host:str = 'host.docker.internal', port:int=6379):
        self.redis = None
        # self.connect()
        self.host = host
        self.port = port
        self._internal_queue = []

    def connect(self):
        try:
            self.redis = redis.Redis(host=self.host, port=self.port, db=0)
            self.redis.ping()
        except Exception as e:
            raise Exception(f'Error connecting to Redis: {str(e)}')

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, value):
        self.redis.set(key, value)

    def delete(self, key):
        self.redis.delete(key)