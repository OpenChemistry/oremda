from oremda.operator import operator


@operator
def multiply(data, params):
    return data * params.get('value', 1)
