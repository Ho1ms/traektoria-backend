def validate_data(data, keys):
    for header in keys:
        if header not in data:
            break
    else:
        return True
    return False