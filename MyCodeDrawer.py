
import matplotlib
import matplotlib.pyplot as pyplot
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
from settings import *


class MyCodeDrawer():

    def __init__(self, fields, dates, data, title):
        self.group = []
        for g in fields.split(' '):
            self.group.append(g)

        self.dates = dates
        self.data = data
        self.title = title

    def draw(self, path=None, title=""):

        if path is not None:
            matplotlib.use('Agg')

        index_d = 0
        _fig, ax = pyplot.subplots(
            len(self.group), 1,
            sharex=True, sharey=False)
        _fig.set_size_inches(9, 9)

        for i in range(len(self.group)):
            cnum = 0

            for plot in self.group[i].split(','):

                if (len(self.group) == 1):

                    if (plot.count('.') == 0):
                        ax.plot(self.dates, self.data[index_d],
                                "C%d" % cnum)
                        index_d += 1
                    else:
                        ax.scatter(
                            self.data[index_d],
                            self.data[index_d+1],
                            c=self.data[index_d+2],
                            s=20)
                        index_d += 3
                        # break
                else:
                    if (plot.count('.') == 0):

                        ax[i].plot(
                            self.dates, self.data[index_d],
                            "C%d" % cnum)
                        index_d += 1
                    else:
                        # print("index {}".format(str(index_d)))
                        ax[i].scatter(
                            self.data[index_d],
                            self.data[index_d+1],
                            c=self.data[index_d+2],
                            s=20)
                        index_d += 3
                cnum += 1
        _fig.autofmt_xdate()
        #_fig.canvas.set_window_title(self.title)

        if path is None:
            pyplot.show()
        else:
            rcParams['axes.unicode_minus'] = False
            myfont = FontProperties(fname=f'"settings['data_root']}/msjh.ttc", size=15)
            if len(self.group) > 1:
                ax[0].set_title(title, fontproperties=myfont)
            else:
                ax.set_title(title, fontproperties=myfont)
            pyplot.savefig(path)
        pyplot.close("all")
