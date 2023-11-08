import matplotlib as mpl 
mpl.use('Agg')
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, vmin=0.0, vmax=2.2, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, fontsize=20, rotation=-90, va="bottom")
    cbar.ax.tick_params(labelsize=17)
    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    # print(cbarlabel, col_labels, row_labels)
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels[::-1])
    ax.set_xlabel('Clients', fontsize=20)
    ax.set_ylabel('Servers', fontsize=20)
    ax.tick_params(axis='x', labelsize=15) 
    ax.tick_params(axis='y', labelsize=15) 

    # Let the horizontal axes labeling appear on top.
    # ax.tick_params(top=True, bottom=False,
    #                labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    # plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
    #          rotation_mode="anchor")

    # Turn spines off and create white grid.
    # ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            # text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            if data[i,j] > 1:
                text = im.axes.text(j, i, "o", **kw)
            else:
                text = im.axes.text(j, i, "x", **kw)
            texts.append(text)

    return texts

def get_avg_throughtput(fct_file):
  f = open(fct_file, mode='r')
  throughtputs = []
  fcts = []
  for line in f.read().splitlines():
    # print(line)
    data = line.split(' ')
    # print(line)
    size = int(data[4])
    fct = int(data[6])

    fcts.append(fct)
    """
    unit is Gbps
    """
    throughtput = float(size * 8) / (fct) 
    throughtputs.append(throughtput)
  f.close()
#   print(fct_file, len(throughtputs))
#   print(fct_file, np.percentile(fcts, 99.99) / 1e6)
  return np.average(throughtputs)

if __name__ == "__main__":

  clients = [i * 4 * 4 for i in range(1, 9)]
  servers = [i * 4 * 4 for i in range(1, 9)]
  # print(clients, servers)

#   fat_fct_fmt = "../mix/output/fat-tree/dcqcn/cs-model/pfc/web/C%d-S%d/fct.txt"
  # fc_fct_fmt = "../mix/output/fc/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  fat_fct_fmt = "../mix/output/fc-ecmp/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  fc_ecmp_fct_fmt = "../mix/output/fc-uniform/dcqcn/cs-model/64/pfc/web/C%d-S%d/fct.txt"
  
  fat_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  fc_ecmp_throughtputs = np.zeros((len(clients), len(servers)), dtype='float')
  hosts_every_rack = 4
  for i in range(len(clients)):
    for j in range(len(servers)):
      fat_fct_file = fat_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fat_throughtputs[i][j] = get_avg_throughtput(fat_fct_file)

      fc_ecmp_fct_file = fc_ecmp_fct_fmt % (clients[i] / hosts_every_rack, servers[j] / hosts_every_rack)
      fc_ecmp_throughtputs[i][j] = get_avg_throughtput(fc_ecmp_fct_file)
  normalized_throughtputs = fc_ecmp_throughtputs / fat_throughtputs
  
  for row in range(len(normalized_throughtputs)):
    normalized_throughtputs[row] = normalized_throughtputs[row][::-1]
  plt_throughtput = np.transpose(normalized_throughtputs)

  fig, ax = plt.subplots(figsize=(6,4))
  im, cbar = heatmap(plt_throughtput, clients, servers, ax=ax,
                    cmap="YlGnBu", cbarlabel="Normalized throughput")
  texts = annotate_heatmap(im, valfmt="{x:.1f} t")
  fig.tight_layout()

  fname = "images/" + os.path.basename(__file__).replace('.py', '.pdf')
  plt.savefig(fname)