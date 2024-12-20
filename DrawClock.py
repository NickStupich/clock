import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot, Rect, Circle
from bokeh.models import Range1d

import datetime

# clock_positions_base = np.pi * np.array([
#                 [(0,0),     (1, 1.5),   (0, 1.5, ),     (1, 1.5),       (1.5, 1.5),     (1.5, 1.5),     (0, 1.5),   (1, 1.5)    ],
#                 [(0,1.5),   (1, 0.5),   (0.5, 1.5,),    (0.5, 1.5),     (0, 0.5),       (0.5, 1.5),     (0, 0.5),   (0.5, 1.5)  ],
#                 [(0,0.5),   (1, 1),     (0, 0.5, ),     (0.5, 1),       (1.25, 1.25),   (0.5, 0.5),     (0, 0),     (0.5, 1)    ],
#             ])


clock_positions_base = np.array([
                [(0,0),     (180, 270),   (0, 270 ),     (180, 270),       (270, 270),     (270, 270),     (0, 270),   (180, 270)    ],
                [(0,270),   (180, 90),   (90, 270),    (90, 270),     (0, 90),       (90, 270),     (0, 90),   (90, 270)  ],
                [(0,90),   (180, 180),     (0, 90 ),     (90, 180),       (225, 225),   (90, 90),     (0, 0),     (90, 180)    ],
            ])

n_rows = 3
n_cols = 8

if 1:
    border_padding = 50
    distance_between_clocks = 300
    border_outline_padding = 20

    hand_length = 130
    hand_width = 20
    clock_radius = 140

    plot_width = 2500
    plot_height = 1000 #dimensions
else:
    border_padding = 25
    distance_between_clocks = 150
    border_outline_padding = 10

    hand_length = 65
    hand_width = 10
    clock_radius = 70

    plot_width = 1250
    plot_height = 500

def draw_single_clock(plot, center, angles):

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
    

def draw_full_clock(plot, angles):
    start = datetime.datetime.now()

    plot.renderers = []

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
            draw_single_clock(plot, center, angles[n_rows - row -1 ,col]) #plotting is bottom up

    print('full draw time: ', (datetime.datetime.now() - start))


def draw_full_clock_by_source(plot, source):
    start = datetime.datetime.now()

    hand_color = "#cab2d6"
    plot.renderers = []


    #background border
    x = (border_padding * 2 + distance_between_clocks * (n_cols))/2 
    y = (border_padding * 2 + distance_between_clocks * (n_rows))/2 
    w = (border_padding * 2 + distance_between_clocks * (n_cols)) - 2 * border_outline_padding
    h = (border_padding * 2 + distance_between_clocks * (n_rows)) - 2 * border_outline_padding

    glyph = Rect(x=x, y=y, width=w, height=h, fill_color="#dddddd")
    plot.add_glyph(glyph)


    glyph = Circle(x='centers_x', y='centers_y', radius=clock_radius, line_color="#3288bd", fill_color="#eeeeee", line_width=1)
    plot.add_glyph(source, glyph)

    glyph = Rect(x='hour_rect_centers_x', y='hour_rect_centers_y', width=hand_length, height=hand_width, angle='hour_angles', fill_color=hand_color)
    plot.add_glyph(source, glyph)

    glyph = Rect(x='minute_rect_centers_x', y='minute_rect_centers_y', width=hand_length, height=hand_width, angle='minute_angles', fill_color=hand_color)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='centers_x', y='centers_y', radius=hand_width, fill_color=hand_color, line_width=1)
    plot.add_glyph(source, glyph)

    print('full draw time: ', (datetime.datetime.now() - start))


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

    # print(flat_angles)

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

    #time = 20:49
    angles = clock_positions_base

    # draw_full_clock(plot2, angles)
    draw_full_clock_by_source(plot2, ColumnDataSource(angles_to_source_dict(angles)))
    show(plot2)