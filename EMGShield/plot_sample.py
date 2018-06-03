import json
import os

import plotters

sample_dir = "collected_data/passwords/ale"
sample_name = "2018-06-03_7.json"
with open(os.path.join(sample_dir, sample_name)) as fp:
    sample = json.load(fp)

    plotter = plotters.mpl.DynamicPlotter(channels=1, x_range=10000,min_val=0,max_val=2000, linewidth=1.0)
    for i in range(0, len(sample['channel0'])):
        plotter.plotdata([sample['channel0'][i]])
    input("enter to exit")
