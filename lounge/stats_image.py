from io import BytesIO
import matplotlib.pyplot as plt
from discord import File
from .components import SeasonDivision


def make(mmrs: list[list[int]], season: int) -> File:
    xdata = []
    ydata = []
    for i, l in enumerate(mmrs):
        xdata.extend([i + j/len(l) for j in range(len(l))])
        ydata.extend(l)
    fig = plt.figure(facecolor='#2f3136', tight_layout=True)
    ax = fig.add_subplot(111, xmargin=0, facecolor='#2f3136')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(colors='w', left=False, bottom=False)
    ax.grid(color='w', ls=':', dash_capstyle='round')
    ax.set_axisbelow(False)
    try:
        division = SeasonDivision(season)
        ax.plot(xdata, ydata, color='black', lw=9, solid_capstyle='round', alpha=0.3)
        min_ylim, max_ylim = ax.get_ylim()
        ax.set_facecolor(division.top_color)
        for span in division.spans:
            if min_ylim <= span.max and span.min <= max_ylim:
                ax.axhspan(span.min, span.max, color=span.color)
                ax.axhline(span.max, color='w')
        for line in division.lines:
            if min_ylim <= line and line <= max_ylim:
                ax.axhline(line, color='w')
        ax.set_ylim((min_ylim, max_ylim))
        if min_ylim < 0:
            ax.axhspan(min_ylim, 0, color='#2f3136')
    except ValueError:
        pass
    ax.plot(xdata, ydata, color='w', solid_capstyle='round')
    binary = BytesIO()
    fig.savefig(binary, format='png')
    binary.seek(0)
    file = File(fp=binary, filename='stats.png')
    binary.close()
    return file
