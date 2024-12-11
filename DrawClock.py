"""from bokeh.plotting import figure, show

fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
counts = [5, 3, 4, 2, 4, 6]

p = figure(x_range=fruits, height=350, title="Fruit Counts",
           toolbar_location=None, tools="")

p.vbar(x=fruits, top=counts, width=0.9)

p.xgrid.grid_line_color = None
p.y_range.start = 0

show(p)


import numpy as np

from bokeh.io import curdoc, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot

N = 9
x = np.linspace(-2, 2, N)
y = x**2
r = x/12.0+0.4

source = ColumnDataSource(dict(x=x, y=y, r=r))

plot = Plot(
    title=None, width=300, height=300,
    min_border=0, toolbar_location=None)

glyph = AnnularWedge(x="x", y="y", inner_radius=.2, outer_radius="r", start_angle=0.6, end_angle=4.1, fill_color="#8888ee")
plot.add_glyph(source, glyph)

xaxis = LinearAxis()
plot.add_layout(xaxis, 'below')

yaxis = LinearAxis()
plot.add_layout(yaxis, 'left')

plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

# curdoc().add_root(plot)

show(plot)"""

import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot, Rect

N = 9
x = np.linspace(-2, 2, N)
y = x**2
r = x/12.0+0.4

source = ColumnDataSource(dict(x=x, y=y, r=r))

plot = Plot(
    title=None, width=1000, height=1000,
    min_border=0, toolbar_location=None)#,x_range=(0, 1000), y_range=(0, 1000))

# glyph = AnnularWedge(x="x", y="y", inner_radius=.2, outer_radius="r", start_angle=0.6, end_angle=4.1, fill_color="#8888ee")
# plot.add_glyph(source, glyph)


clockHand = AnnularWedge(x=234, y=456, inner_radius=0, outer_radius=100, start_angle=0.2, end_angle=0.3, fill_color="#ee8888")
plot.add_glyph(clockHand)

glyph = Rect(x=234, y=456, width=100, height=10, angle=-0.7, fill_color="#cab2d6")
plot.add_glyph(source, glyph)


# xaxis = LinearAxis()
# plot.add_layout(xaxis, 'below')

# yaxis = LinearAxis()
# plot.add_layout(yaxis, 'left')

# plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
# plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))


# fig.x_range = Range1d(0, 1000) 
# fig.y_range = Range1d(0, 1000) 

figure.x_range.start = 0
figure.x_range.end = 1000

show(plot)