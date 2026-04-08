def isFirstTimeSetup(initialSetup: bool):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if initialSetup:
                return func(*args, **kwargs)
            else:
                print("Setup already completed")
                return None

        return wrapper

    return decorator
