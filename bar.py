import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import OrderedDict


Greens = mpl.colors.ListedColormap(['#c8eed7', '#76d69c', '#27834b'])
Reds = mpl.colors.ListedColormap(['#eec8d7', '#d6769c', '#83274b'])
Blues = mpl.colors.ListedColormap(['#ccd5ed', '#8097d3', '#1944b0'])

font = {'family': 'helvetica',
        'size': 7}

mpl.rc('font', **font)

single_width = 8.4/2.54
double_width = 17.8/2.54

single_height = 6.3/2.54
double_height = 8.4/2.54

dpi = 300


class Figure:
    def __init__(self, *args, **kwargs):
        self.group_label_loc: float = kwargs.pop('group_label_loc', None)

        self.out_file = kwargs.pop('out_file', None)

        # we will make use of pyplots axes instead of global functions
        # user can give their own axes
        if 'axes' in kwargs:
            self.axes = kwargs['axes']
        else:
        # if not given, we will make a new plot and the get the current axes of that plot
            plt.figure(*args, **kwargs)
            self.axes = plt.gca()

        self.labels = []
        self.colors = []
        self.xtick_settings = {}
        self.legend_settings = {}
        self._hlines = []

    def hlines(self, y, span=None, **kwargs):
        self._hlines.append([y, span, kwargs])
        self.render()

    def _render_pre(self):
        self.axes.cla()

    def _render_post(self):
        xlim = self.axes.get_xlim()
        for hline in self._hlines:
            self.axes.hlines(hline[0], *xlim, **hline[2])
        self.axes.set_xlim(xlim)
        self.axes.legend(**self.legend_settings)

    def __enter__(self):
        self._old_hatch_width = mpl.rcParams['hatch.linewidth']
        mpl.rcParams['hatch.linewidth'] = 0.3  # previous pdf hatch linewidth
        return self

    def __exit__(self, *args, **kwargs):
        if self.out_file is None:
            mpl.rcParams['figure.dpi'] = dpi
            plt.tight_layout()
            self.show()
        else:
            plt.savefig(self.out_file, dpi=dpi, bbox_inches='tight')
        mpl.rcParams['hatch.linewidth'] = self._old_hatch_width  # previous pdf hatch linewidth

    def ylim(self, *args, **kwargs):
        self.axes.set_ylim(*args, **kwargs)

    def xlim(self, *args, **kwargs):
        self.axes.set_xlim(*args, **kwargs)

    def ylabel(self, *args, **kwargs):
        self.axes.set_ylabel(*args, **kwargs)

    def xlabel(self, *args, **kwargs):
        self.axes.set_xlabel(*args, **kwargs)


class Bar(Figure):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bar_data = OrderedDict()
        self.hatches = []
        self.groups = None
        self.bar_spacing: float = 0.25
        self.group_spacing: int = 1
        # self.group_label_axis_label_spacing: float = .1

        self.bar_settings = dict(align='edge', edgecolor='#030203', linewidth=.5)

    def add_series(self, X: list, Y: list, label: str = None, color=None, hatch=None):
        ''' Add data to plot.
            
            Arguments
            =========
            X: list of labels for the bars. These labels will be on the x-axis
            Y: list of values or bar-heights for this series
            label: str name of the dataseries. This will be used in the legend upon rendering
            color: str or tuple of RGB values, color in any pyplot format which will be used to color the bars
        ''' 
        # add the new data to the internal data storage
        for x, y in zip(X, Y):
            # if the label does not exist, default to empty list
            self.bar_data.setdefault(x, [])
            # add the new data to that list
            self.bar_data[x].append(y)

        # add label and color for later use
        self.labels.append(label)
        self.colors.append(color)
        self.hatches.append(hatch)
        self.render()

    def _render_single(self, data, origin=0, use_labels=True):
        # internal method used to render a single group of data
        # origin denotes the x-axis value the group starts at
        # use_labels is used to determine if the label argument should be given to pyplot
        # use this argument to prevent multiple of the same series to appear in the legend

        # determine number of bars to render per x-value
        nbars_per_label = len(list(data.values())[0])
        # determine the width of each bar. This depends on the number of bars and also the spacing
        width = 1/nbars_per_label * (1 - self.bar_spacing)

        # for each series we will draw the bars
        for n in range(nbars_per_label):
            # the locations are calculated such that they are centered around the x-axis value. This enables centered x-axis labels
            loc = [origin + i + n/nbars_per_label * (1 - self.bar_spacing) - .5 + self.bar_spacing/2 for i in range(len(data))]
            self.axes.bar(loc, [x[n] for x in data.values()], width=width, label=self.labels[n] if use_labels else None, color=self.colors[n], hatch=self.hatches[n], **self.bar_settings)

    def render(self):
        self._render_pre()
        # if there is no groups present, render the data as is
        if self.groups is None:
            self._render_single(self.bar_data)
            indices = [i for i, _ in enumerate(self.bar_data.keys())]
            self.axes.set_xticks(indices, self.bar_data.keys(), **self.xtick_settings)

        # if there are groups, we must construct new datastructures for each group
        else:
            # we increment origin accordingly
            origin = 0
            xtick_labels = []
            xtick_locs = []
            for groupname, groupxs in self.groups.items():
                data = {x: self.bar_data[x] for x in groupxs}
                self._render_single(data, origin=origin, use_labels=origin == 0)
                xtick_labels.extend(groupxs)
                xtick_locs.extend(range(origin, origin + len(groupxs)))
                if self.group_label_loc is None:
                    group_label_loc = self.axes.get_ylim()[0] - (self.axes.get_ylim()[1] - self.axes.get_ylim()[0]) * .2
                else:
                    group_label_loc = self.group_label_loc

                self.axes.text(origin + len(data)/2 - .5, group_label_loc, groupname, fontweight='heavy', va='top', ha='center')
                origin += len(data) + self.group_spacing

            self.axes.set_xticks(xtick_locs, xtick_labels, **self.xtick_settings)
        self._render_post()
        

    def set_xtick_settings(self, **kwargs):
        self.xtick_settings.update(kwargs)
        self.render()

    def set_legend_settings(self, **kwargs):
        self.legend_settings.update(kwargs)
        self.render()

    def set_bar_settings(self, **kwargs):
        self.bar_settings.update(kwargs)
        self.render()

    def set_group(self, groupname: str, groupxs: list):
        if self.groups is None:
            self.groups = OrderedDict()
        self.groups[groupname] = groupxs
        self.render()

    def sort(self, label: str, reverse: bool = False):
        '''Method used to sort the bars prior to rendering

        Arguments
        =========
        label: str name of the series to sort on
        reverse: bool, specifies whether to sort large to small or small to large
        '''
        label_idx = self.labels.index(label)
        if self.groups is None:
            order = np.argsort([val[label_idx] for key, val in self.bar_data.items()])
            xs = [list(self.bar_data.keys())[i] for i in order]
            self.bar_data = OrderedDict({x: self.bar_data[x] for x in xs})
        else:
            for groupname, groupxs in self.groups.items():
                f = -1 if reverse else 1
                order = np.argsort([self.bar_data[x][label_idx] * f for x in groupxs])
                self.groups[groupname] = [groupxs[i] for i in order]
        self.render()

    def show(self):
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    rads = [r'$^•$BH$_2$', r'$^•$CH$_3$', r'$^•$NH$_2$', r'$^•$OH', r'$^•$SH']

    with Bar(figsize=(single_width, single_height)) as bar:
        bar.add_series(rads, [0.75, 1.054, 1.038, 0.97, 1.032],  label='BS1',  color=Reds(0.0))
        bar.add_series(rads, [0.75, 1.049, 1.033, 0.966, 1.027], label='BS1+', color=Reds(0.0), hatch='/////')
        bar.add_series(rads, [0.75, 1.049, 1.033, 0.966, 1.027], label='BS2',  color=Reds(0.5))
        bar.add_series(rads, [0.75, 1.054, 1.038, 0.97, 1.032],  label='BS2+', color=Reds(0.5), hatch='/////')
        bar.add_series(rads, [0.75, 1.054, 1.038, 0.97, 1.032],  label='BS3',  color=Reds(1.0))
        bar.add_series(rads, [0.75, 1.049, 1.033, 0.966, 1.027], label='BS3+', color=Reds(1.0), hatch='/////')
        bar.hlines(.75*1.1, color='r', linestyle='dashed', linewidth=.7)  # draw a red dashed line at 10% deviation
        bar.set_legend_settings(ncols=3, loc='upper center', frameon=False)
        bar.ylim(0.75, 1.15)
        bar.ylabel(r'$\langle S^2 \rangle$')
        bar.xlabel('Radical')
