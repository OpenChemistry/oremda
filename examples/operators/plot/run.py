import matplotlib.pyplot as plt

from oremda import operator

@operator
def plot(meta, data, parameters):
    filename = parameters.get('filename')
    x_label = parameters.get('xLabel', 'x')
    y_label = parameters.get('yLabel', 'y')

    x0 = data.get('x0')
    y0 = data.get('y0')
    x1 = data.get('x1')
    y1 = data.get('y1')

    fg, ax = plt.subplots(1, 1)

    if x0 is not None and y0 is not None:
        ax.plot(x0, y0)

    if x1 is not None and y1 is not None:
        ax.plot(x1, y1)

    ax.set(xlabel=x_label, ylabel=y_label)

    fg.savefig(f'/data/{filename}', dpi=fg.dpi)

    return {}, {}
