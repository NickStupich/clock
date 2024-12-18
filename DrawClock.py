import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot, Rect, Circle
from bokeh.models import Range1d


n_rows = 3
n_cols = 8

def draw_single_clock(center, angles):
    hand_length = 130
    hand_width = 20
    clock_radius = 140

    hand_color = "#cab2d6"

    angle_minute, angle_hour = angles

    hour_rect_center = (center[0] + np.cos(angle_hour) * hand_length/2, center[1] + np.sin(angle_hour) * hand_length/2)
    minute_rect_center = (center[0] + np.cos(angle_minute) * hand_length/2, center[1] + np.sin(angle_minute) * hand_length / 2)

    glyph = Circle(x=center[0], y=center[1], radius=clock_radius, line_color="#3288bd", fill_color="#eeeeee", line_width=1)
    plot.add_glyph(glyph)

    glyph = Rect(x=hour_rect_center[0], y=hour_rect_center[1], width=hand_length, height=hand_width, angle=angle_hour, fill_color=hand_color)
    plot.add_glyph(glyph)

    glyph = Rect(x=minute_rect_center[0], y=minute_rect_center[1], width=hand_length, height=hand_width, angle=angle_minute, fill_color=hand_color)
    plot.add_glyph(glyph)

    glyph = Circle(x=center[0], y=center[1], radius=hand_width, fill_color=hand_color, line_width=1)
    plot.add_glyph(glyph)


def draw_full_clock(angles):

    border_padding = 50
    distance_between_clocks = 300
    border_outline_padding = 20

    #total required dimensions
    # print(border_padding*2 + distance_between_clocks * n_rows)
    # print(border_padding*2 + distance_between_clocks * n_cols)

    #background border
    x = (border_padding * 2 + distance_between_clocks * (n_cols))/2 
    y = (border_padding * 2 + distance_between_clocks * (n_rows))/2 
    w = (border_padding * 2 + distance_between_clocks * (n_cols)) - 2 * border_outline_padding
    h = (border_padding * 2 + distance_between_clocks * (n_rows)) - 2 * border_outline_padding

    glyph = Rect(x=x, y=y, width=w, height=h, fill_color="#dddddd")

    plot.add_glyph(glyph)
    
    for row in range(n_rows):
        for col in range(n_cols):
            center = (border_padding + (col + 0.5) * distance_between_clocks, border_padding + (row + 0.5) * distance_between_clocks)
            draw_single_clock(center, angles[n_rows - row -1 ,col]) #plotting is bottom up


if __name__ == "__main__":

    plot = Plot(
        title=None, width=2500, height=1000,
        min_border=0, toolbar_location=None,
        x_range=Range1d(0, 2500), y_range=Range1d(0, 1000))

    #time = 20:49
    angles = np.pi * np.array([
                [(0,0),     (1, 1.5),   (0, 1.5, ),     (1, 1.5),       (1.5, 1.5),     (1.5, 1.5),     (0, 1.5),   (1, 1.5)    ],
                [(0,1.5),   (1, 0.5),   (0.5, 1.5,),    (0.5, 1.5),     (0, 0.5),       (0.5, 1.5),     (0, 0.5),   (0.5, 1.5)  ],
                [(0,0.5),   (1, 1),     (0, 0.5, ),     (0.5, 1),       (1.25, 1.25),   (0.5, 0.5),     (0, 0),     (0.5, 1)    ],
            ])

    draw_full_clock(angles)
    show(plot)