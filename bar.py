import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import OrderedDict


class Bar:
    def __init__(self, *args, **kwargs):
        if 'axes' in kwargs:
            self.axes = kwargs['axes']
        else:
            plt.figure(*args, **kwargs)
            self.axes = plt.gca()

        self.data = OrderedDict()
        self.labels = []
        self.colors = []
        self.groups = None
        self.bar_spacing: float = 0.2
        self.group_spacing: int = 1
        self.group_label_axis_label_spacing: float = .1

        self.xtick_settings = {}

    def add_series(self, X: list, Y: list, label: str = None, color=None):
        for x, y in zip(X, Y):
            self.data.setdefault(x, [])
            self.data[x].append(y)
        self.labels.append(label)
        self.colors.append(color)
        self.render()

    def _render_single(self, data, origin=0, use_labels=True):
        nbars_per_label = len(list(data.values())[0])
        width = 1/nbars_per_label * (1 - self.bar_spacing)

        for n in range(nbars_per_label):
            loc = [origin + i + n/nbars_per_label * (1 - self.bar_spacing) - .5 + self.bar_spacing/2 for i in range(len(data))]
            self.axes.bar(loc, [x[n] for x in data.values()], width=width, align='edge', label=self.labels[n] if use_labels else None, color=self.colors[n])

    def render(self):
        self.axes.cla()
        if self.groups is None:
            self._render_single(self.data)
            indices = [i for i, _ in enumerate(self.data.keys())]
            self.axes.set_xticks(indices, self.data.keys(), **self.xtick_settings)
        else:
            origin = 0
            xtick_labels = []
            xtick_locs = []
            for groupname, groupxs in self.groups.items():
                data = {x: self.data[x] for x in groupxs}
                self._render_single(data, origin=origin, use_labels=origin == 0)
                xtick_labels.extend(groupxs)
                xtick_locs.extend(range(origin, origin + len(groupxs)))
                self.axes.text(origin + len(data)/2 - .5, -.1, groupname, transform=self.axes.get_xaxis_transform(), fontweight='heavy', va='top', ha='center')
                origin += len(data) + self.group_spacing

            self.axes.set_xticks(xtick_locs, xtick_labels, **self.xtick_settings)
        self.axes.legend()

    def set_xtick_settings(self, **kwargs):
        self.xtick_settings = kwargs
        self.render()

    def set_group(self, groupname: str, groupxs: list):
        if self.groups is None:
            self.groups = OrderedDict()
        self.groups[groupname] = groupxs
        self.render()

    def sort(self, label: str, reverse=False):
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
    bar.set_group('First', ['a', 'b', 'c'])
    bar.set_group('Second', ['a', 'c'])
    bar.set_xtick_settings(rotation=90)
    bar.sort('st. dev.')

    bar = Bar(axes=axs[1])
    bar.add_series(['a', 'b', 'c'], [3, 6, 2.5], label='mean', color='red')
    bar.add_series(['a', 'b', 'c'], [1, 2, 1], label='st. dev.', color='green')
    bar.set_group('First', ['a', 'b', 'c'])
    bar.set_group('Second', ['a', 'c'])
    bar.sort('mean')

    fig.tight_layout()
    bar.show()
