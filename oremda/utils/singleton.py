class SingletonMetaclass(type):
    """A metaclass for singletons"""

    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance


class Singleton(metaclass=SingletonMetaclass):
    """Inherit from this class to easily use the metaclass singleton..."""

    pass
