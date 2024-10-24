import logging

from django.core.cache import caches


logger = logging.getLogger(__name__)


class CacheUtil:
    _instance = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cache = cls.__initialize_cache()
        return cls._instance

    @staticmethod
    def __initialize_cache():
        """Attempts RedisCache, defaults to LocMemCache"""
        try:
            cache = caches['redis']
            cache.get('key')
            logger.info('Using Redis cache.')
            return cache
        except Exception as e:
            logger.warning(f'Error using Redis cache: {e}')
            logger.info('Using LocMem cache.')
        return caches['default']

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        return self.cache.set(key, value)

    def delete(self, key):
        return self.cache.delete(key)


cache = CacheUtil()
