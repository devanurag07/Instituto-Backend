def _validate_mobile(value):
    try:
        value = int(value)
        length = len(str(value))
        if(length != 10):
            return False

    except Exception as e:
        return False

    return True
