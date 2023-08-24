
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import OrderedDict
# from yplot import config


class Bar:
    def __init__(self, *args, **kwargs):
        self.group_label_loc: float = kwargs.pop('group_label_loc', None)

        # we will make use of pyplots axes instead of global functions
        # user can give their own axes
        if 'axes' in kwargs:
            self.axes = kwargs['axes']
        else:
        # if not given, we will make a new plot and the get the current axes of that plot
            plt.figure(*args, **kwargs)
            self.axes = plt.gca()

        self.data = OrderedDict()
        self.labels = []
        self.colors = []
        self.groups = None
        self.bar_spacing: float = 0.25
        self.group_spacing: int = 1
        # self.group_label_axis_label_spacing: float = .1


        self.xtick_settings = {}
        self.legend_settings = {}
        self.bar_settings = dict(align='edge', edgecolor='#030203', linewidth=1)

    def add_series(self, X: list, Y: list, label: str = None, color=None):
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
            self.data.setdefault(x, [])
            # add the new data to that list
            self.data[x].append(y)

        # add label and color for later use
        self.labels.append(label)
        self.colors.append(color)
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
            self.axes.bar(loc, [x[n] for x in data.values()], width=width, label=self.labels[n] if use_labels else None, color=self.colors[n], **self.bar_settings)

    def render(self):
        # upon rendering, first clear the current axes
        self.axes.cla()

        # if there is no groups present, render the data as is
        if self.groups is None:
            self._render_single(self.data)
            indices = [i for i, _ in enumerate(self.data.keys())]
            self.axes.set_xticks(indices, self.data.keys(), **self.xtick_settings)

        # if there are groups, we must construct new datastructures for each group
        else:
            # we increment origin accordingly
            origin = 0
            xtick_labels = []
            xtick_locs = []
            for groupname, groupxs in self.groups.items():
                data = {x: self.data[x] for x in groupxs}
                self._render_single(data, origin=origin, use_labels=origin == 0)
                xtick_labels.extend(groupxs)
                xtick_locs.extend(range(origin, origin + len(groupxs)))
                if self.group_label_loc is None:
                    group_label_loc = self.axes.get_ylim()[0] - (self.axes.get_ylim()[1] - self.axes.get_ylim()[0]) * .2
                else:
                    group_label_loc = self.group_label_loc
                print(group_label_loc)
                self.axes.text(origin + len(data)/2 - .5, group_label_loc, groupname, fontweight='heavy', va='top', ha='center')
                origin += len(data) + self.group_spacing

            self.axes.set_xticks(xtick_locs, xtick_labels, **self.xtick_settings)
        self.axes.legend(**self.legend_settings)

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
            order = np.argsort([val[label_idx] for key, val in self.data.items()])
            xs = [list(self.data.keys())[i] for i in order]
            self.data = OrderedDict({x: self.data[x] for x in xs})
        else:
            for groupname, groupxs in self.groups.items():
                f = -1 if reverse else 1
                order = np.argsort([self.data[x][label_idx] * f for x in groupxs])
                self.groups[groupname] = [groupxs[i] for i in order]
        self.render()

    def show(self):
        plt.show()


if __name__ == '__main__':
    fig, axs = plt.subplots(2, 1)
    bar = Bar(axes=axs[0])
    bar.add_series(['a', 'b', 'c'], [3, 6, 2.5], label='mean', color='red')
    bar.add_series(['a', 'b', 'c'], [1, 2, 1], label='st. dev.', color='green')
    bar.set_xtick_settings(rotation=90)
    bar.sort('st. dev.')

    bar = Bar(axes=axs[1])
    bar.add_series(['a', 'b', 'c'], [3, 6, 2.5], label='mean', color='red')
    bar.add_series(['a', 'b', 'c'], [1, 2, 1], label='st. dev.', color='green')
    bar.set_group('First', ['a', 'b', 'c'])
    bar.set_group('Second', ['a', 'c'])
    bar.sort('mean')
    bar.set_legend_settings(ncols=2, loc='upper right', frameon=False)

    fig.tight_layout()
    bar.show()
