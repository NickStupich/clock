import numpy as np

from bokeh.plotting import figure, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot, Rect, Circle, Range1d


n_rows = 3
n_cols = 8
clock_positions_base = np.ones((n_rows, n_cols, 2)) * 270

#dimensions
border_padding = 50
distance_between_clocks = 300
border_outline_padding = 20

hand_length = 130
hand_width = 25
clock_radius = 140

plot_width = 2500
plot_height = 1000 

#colors - black and rose gold
hand_color = "#d08050"
background_color = "#111111"
individual_recess_line_color = "#333333"
individual_recess_fill_color = "#222222"


def draw_full_clock_by_source(plot, source):
    plot.renderers = []

    #background border
    x = (border_padding * 2 + distance_between_clocks * (n_cols))/2 
    y = (border_padding * 2 + distance_between_clocks * (n_rows))/2 
    w = (border_padding * 2 + distance_between_clocks * (n_cols)) - 2 * border_outline_padding
    h = (border_padding * 2 + distance_between_clocks * (n_rows)) - 2 * border_outline_padding

    glyph = Rect(x=x, y=y, width=w, height=h, fill_color=background_color)
    plot.add_glyph(glyph)


    glyph = Circle(x='centers_x', y='centers_y', radius=clock_radius, line_color=individual_recess_line_color, fill_color=individual_recess_fill_color, line_width=1)
    plot.add_glyph(source, glyph)

    glyph = Rect(x='hour_rect_centers_x', y='hour_rect_centers_y', width=hand_length, height=hand_width, angle='hour_angles', fill_color=hand_color)
    plot.add_glyph(source, glyph)

    glyph = Rect(x='minute_rect_centers_x', y='minute_rect_centers_y', width=hand_length, height=hand_width, angle='minute_angles', fill_color=hand_color)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='centers_x', y='centers_y', radius=hand_width/2, fill_color=hand_color, line_width=1)
    plot.add_glyph(source, glyph)


def create_plot():
    plot = Plot(
            title=None, width=plot_width, height=plot_height,
            min_border=0, toolbar_location=None,
            x_range=Range1d(0, plot_width), y_range=Range1d(0, plot_height))

    return plot


def angles_to_source_dict(angles):
    flat_angles = angles.reshape((-1, 2)) * np.pi / 180
    centers = np.array([
            (border_padding + (col + 0.5) * distance_between_clocks, border_padding + (row + 0.5) * distance_between_clocks) 
        for row in range(n_rows)[::-1] #drawn bottom to top
        for col in range(n_cols)
        ])

    hour_angles = flat_angles[:, 0]
    minute_angles = flat_angles[:, 1]

    centers_x = centers[:, 0]
    centers_y = centers[:, 1]

    hour_rect_centers_x = centers_x + np.cos(hour_angles) * hand_length/2
    hour_rect_centers_y = centers_y + np.sin(hour_angles) * hand_length/2

    minute_rect_centers_x = centers_x + np.cos(minute_angles) * hand_length/2
    minute_rect_centers_y = centers_y + np.sin(minute_angles) * hand_length / 2

    source_dict = {
        'hour_angles': hour_angles, 
        'minute_angles': minute_angles,

        'hour_rect_centers_x' : hour_rect_centers_x,
        'hour_rect_centers_y' : hour_rect_centers_y,

        'minute_rect_centers_x' : minute_rect_centers_x,
        'minute_rect_centers_y' : minute_rect_centers_y,

        'centers_x': centers_x,
        'centers_y': centers_y,
    }

    return source_dict
    

if __name__ == "__main__":

    plot2 = create_plot()
    angles = clock_positions_base

    draw_full_clock_by_source(plot2, ColumnDataSource(angles_to_source_dict(angles)))
    show(plot2)