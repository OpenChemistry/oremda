from oremda import operator


@operator
def view(data, params):
    print('VIEW DATA', data, flush=True)
    return data
