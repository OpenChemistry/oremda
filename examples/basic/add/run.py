from oremda import operator


@operator
def add(data, params):
    return data + params.get('value', 0)
