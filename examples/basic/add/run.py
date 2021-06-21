from oremda import operator

@operator
def add(meta, data, parameters):
    value = parameters.get('value', 0)
    input_data = data.get('scalars')

    output = {
        'scalars': input_data + value
    }

    return meta, output
