import numpy as np

from bokeh.plotting import figure, show
from bokeh.models import AnnularWedge, ColumnDataSource, Grid, LinearAxis, Plot, Rect, Circle, Range1d


n_rows = 3
n_cols = 8
clock_positions_base = np.ones((n_rows, n_cols, 2)) * 270

if 0:
    #dimensions
    horizontal_border_padding = 50 + 250
    vertical_border_padding = 50 + 250
    distance_between_clocks = 300
    border_outline_padding = 20

    hand_length = 130
    hand_width = 25
    clock_radius = 140

    # plot_width = 2500 + 500 # 50*2+300*
    # plot_height = 1000 + 500

    plot_width = n_cols * distance_between_clocks + 2 * horizontal_border_padding
    plot_height = n_rows * distance_between_clocks + 2 * vertical_border_padding


else:
    frame_width = 900
    frame_height = 400

    distance_between_clocks = 100
    border_outline_padding = 0

    hand_length = 40
    hand_width = 10
    clock_radius = 44.5

    horizontal_border_padding = (frame_width - n_cols * distance_between_clocks) // 2
    vertical_border_padding = (frame_height - n_rows * distance_between_clocks) // 2

    plot_width = n_cols * distance_between_clocks + 2 * horizontal_border_padding
    plot_height = n_rows * distance_between_clocks + 2 * vertical_border_padding

    #print(horizontal_border_padding, vertical_border_padding)
    #print(plot_height, plot_width, frame_height, frame_width)

    if 0: #for drawing template
        scale = 10
        horizontal_border_padding *= scale
        vertical_border_padding *= scale
        distance_between_clocks *= scale
        border_outline_padding *= scale
        hand_length *= scale
        hand_width *= scale
        clock_radius *= scale
        plot_width *= scale
        plot_height *= scale


def create_pdf():
    from bokeh.io import export_png
    import svglib.svglib as svglib
    from reportlab.graphics import renderPDF
    from selenium import webdriver
    driver = webdriver.Firefox()
    plot = create_plot()

    centers = np.array([
                (horizontal_border_padding + (col + 0.5) * distance_between_clocks, vertical_border_padding + (row + 0.5) * distance_between_clocks) 
            for row in range(n_rows)[::-1] #drawn bottom to top
            for col in range(n_cols)
            ])


    centers_x = centers[:, 0]
    centers_y = centers[:, 1]

    source = ColumnDataSource({
        'centers_x': centers_x,
        'centers_y': centers_y,
        'support1_x' : centers_x + 9 * scale,
        'support1_y' : centers_y + 15.5 * scale,
        'support2_x' : centers_x + 9 * scale,
        'support2_y' : centers_y - 34.5 * scale,
        'support3_x' : centers_x - 12 * scale,
        'support3_y' : centers_y - 9.5 * scale,
        'outline_center_x' : centers_x,
        'outline_center_y' : centers_y - 9.5 * scale,
    })

    #main dial post
    main_radius = 2.75 * scale
    glyph = Circle(x='centers_x', y='centers_y', radius= main_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0.2)
    plot.add_glyph(source, glyph)

    main_radius = 1 * scale
    glyph = Circle(x='centers_x', y='centers_y', radius= main_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0.)
    plot.add_glyph(source, glyph)


    #support posts    
    support_radius = 1.5 * scale
    glyph = Circle(x='support1_x', y='support1_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='support2_x', y='support2_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='support3_x', y='support3_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)


    support_radius = 1. * scale
    glyph = Circle(x='support1_x', y='support1_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='support2_x', y='support2_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)

    glyph = Circle(x='support3_x', y='support3_y', radius=support_radius, line_color=individual_recess_line_color, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)


    #rough outline

    glyph = Rect(x='outline_center_x', y='outline_center_y', width=31.5*scale, height=59.5*scale, line_width=1, fill_alpha=0)
    plot.add_glyph(source, glyph)


    plot.output_backend = 'svg'
    export_svgs(plot, filename = 'template.svg', webdriver=driver)
    export_png(plot, filename='template.png', webdriver=driver)


#colors - black and rose gold
hand_color = "#d08050"
background_color = "#111111"
individual_recess_line_color = "#333333"
individual_recess_fill_color = "#222222"


def draw_full_clock_by_source(plot, source):
    plot.renderers = []

    #background border
    x = (horizontal_border_padding * 2 + distance_between_clocks * (n_cols))/2 
    y = (vertical_border_padding * 2 + distance_between_clocks * (n_rows))/2 
    w = (horizontal_border_padding * 2 + distance_between_clocks * (n_cols)) - 2 * border_outline_padding
    h = (vertical_border_padding * 2 + distance_between_clocks * (n_rows)) - 2 * border_outline_padding

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
            (horizontal_border_padding + (col + 0.5) * distance_between_clocks, vertical_border_padding + (row + 0.5) * distance_between_clocks) 
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

    # plot2 = create_plot()
    # angles = clock_positions_base

    # draw_full_clock_by_source(plot2, ColumnDataSource(angles_to_source_dict(angles)))
    # show(plot2)

    create_pdf()
