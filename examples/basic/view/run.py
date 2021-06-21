from oremda import operator

@operator
def view(meta, data, parameters):
    print('Meta:', meta, 'Data:', data, flush=True)

    return {}, {}
