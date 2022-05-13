from io import BytesIO
import matplotlib.pyplot as plt
from discord import File
import numpy as np


def make(deltas: list[list[int]]) -> File:
    xdata = [0]
    ydata = [0]
    for i, l in enumerate(deltas):
        xdata.extend([i+1 + j/len(l) for j in range(len(l))])
        ydata.extend(l)
    fig = plt.figure(facecolor='#2f3136', tight_layout=True, figsize=(5, 2))
    ax = fig.add_subplot(111, xmargin=0, facecolor='#2f3136')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('w')
    ax.spines['left'].set_color('w')
    ax.tick_params(colors='w', left=False, bottom=False)
    ax.grid(color='w', ls=':', dash_capstyle='round')
    ax.set_axisbelow(False)
    ax.plot(xdata, np.cumsum(ydata), color='w')
    binary = BytesIO()
    fig.savefig(binary, format='png')
    binary.seek(0)
    file = File(fp=binary, filename='stats.png')
    binary.close()
    return file
