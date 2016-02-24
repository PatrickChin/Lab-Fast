from random import random
from pandas import read_csv
from bokeh.models import ColumnDataSource, BoxSelectTool, WheelZoomTool, PanTool
from bokeh.plotting import figure, output_file, show

output_file("index.html")

df = read_csv('./rawdata/7V.csv', header=None, names=['time','current','voltage','temperature'])

TOOLS = [BoxSelectTool(dimensions=['width']), WheelZoomTool(dimensions=['width']), PanTool(dimensions=['width'])]

s = ColumnDataSource(data=df)
p = figure(plot_width=600, plot_height=400, tools=TOOLS, title="Select Here", webgl=True)
p.line('time', 'temperature', color='color', source=s, line_width=2)

show(p)
