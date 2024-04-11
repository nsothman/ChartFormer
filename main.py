import svgwrite
import math
import numpy as np
import random
from vega_datasets import data
from vega_datasets import local_data
from utils.vega_parser import parse_vega_lite_json, parse_vega_scene_graph

import os
import json
from tqdm import tqdm
from PIL import Image
# import utils_gen

def min_max_scaling(data, new_min, new_max):
    old_min = min(data)
    old_max = max(data)
    scaled_data = []
    for value in data:
        scaled_value = ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
        scaled_data.append(scaled_value)
    return scaled_data

def add_axis(dwg, start_x, start_y, end_x, end_y, axis_type='x', label_values=None, label_positions=None, axis_title=None, title_height=50, tick_length=7):
    # Add main axis line
    dwg.add(svgwrite.shapes.Line(start=(start_x, start_y), end=(end_x, end_y), stroke='black', stroke_width=3))

    if label_values is not None and label_positions is not None:
        font_size_factor = 7
        for label, pos in zip(label_values, label_positions):
            text = None
            rect_x, rect_y, rect_width = None, None, None

            if axis_type == 'x':
                text = svgwrite.text.Text(label, insert=(pos, start_y + 25), text_anchor="middle", font_size=14)
                rect_x = pos - (len(str(label)) * font_size_factor + 10) / 2
                rect_y = start_y + 10
            else:  # For y-axis
                text = svgwrite.text.Text(label, insert=(start_x - 27.5, pos + 7.5), text_anchor="end", font_size=14)
                rect_x = start_x - len(label) * font_size_factor - 32.5
                rect_y = pos - 7.5

            dwg.add(text)
            rect_width = len(str(label)) * font_size_factor + 10

            if axis_title is not None:
                # Add axis title
                if axis_type == 'x':
                    dwg.add(svgwrite.text.Text(axis_title, insert=(end_x / 2 + (len(axis_title) * 5), end_y + 5 + title_height), text_anchor="end", font_size=16))
                    x_axis_box = svgwrite.shapes.Rect(insert=(end_x / 2 - len(axis_title) * 5 + 10, end_y - 15 + title_height), size=(len(axis_title) * 10, 30), stroke='black', fill='none')
                    dwg.add(x_axis_box)
                else:  # For y-axis
                    dwg.add(svgwrite.text.Text(axis_title, insert=(start_x - 40, 35 + title_height), text_anchor="start", font_size=16))
                    y_axis_box = svgwrite.shapes.Rect(insert=(start_x - 65, 15 + title_height), size=(len(axis_title) * 10, 30), stroke='black', fill='none')
                    dwg.add(y_axis_box)

            dwg.add(svgwrite.shapes.Rect(insert=(rect_x, rect_y), size=(rect_width, 20), stroke='black', fill='none'))

    for pos in label_positions:
        if axis_type == 'x':
            dwg.add(svgwrite.shapes.Line(start=(pos, start_y), end=(pos, start_y + tick_length), stroke='black', stroke_width=3))
        else:  # For y-axis
            dwg.add(svgwrite.shapes.Line(start=(start_x, pos), end=(start_x - tick_length, pos), stroke='black', stroke_width=3))


def create_line_graph(x_values, y_values_list, title, index, x_labels, y_labels, labels, x_axis_title='X-axis', y_axis_title='Y-axis', width=400, height=300):
    # Define graph parameters
    legend_width = 120
    title_height = 50
    dwg = svgwrite.Drawing(filename=title + '.svg', size=(f'{width + legend_width}px', f'{height + title_height}px'))

    x_min, x_max = min(x_values), max(x_values)
    y_min = min(min(y) for y in y_values_list)
    y_max = max(max(y) for y in y_values_list)

    padding_left = 70
    padding_bottom = 50
    axis_start_x, axis_end_x = padding_left, width - 10
    axis_start_y, axis_end_y = height - padding_bottom - 30 + title_height, padding_bottom + title_height
    height -= 30

    num_labels_x = len(x_labels)
    x_label_positions = [axis_start_x + i * (width - padding_left - 10) // (num_labels_x + 1) for i in range(1, num_labels_x + 1)]
    x_label_values = [str(round(float(x_min + i * (x_max - x_min) / (num_labels_x + 1)))) for i in range(1, num_labels_x + 1)]

    num_labels_y = len(y_labels)
    y_label_positions = [axis_start_y - i * (height - padding_bottom - 10) // (num_labels_y + 2) for i in range(1, num_labels_y + 1)]
    y_label_values = [str(round(float(y_min + i * (y_max - y_min) / (num_labels_y + 2)), 1)) for i in range(1, num_labels_y + 1)]

    add_axis(dwg, axis_start_x, axis_start_y, axis_end_x, axis_start_y, 'x', x_labels, x_label_positions, x_axis_title, title_height)
    add_axis(dwg, axis_start_x, axis_start_y, axis_start_x, axis_end_y, 'y', y_labels, y_label_positions, y_axis_title, title_height)

    dwg.add(svgwrite.text.Text(title, insert=(width / 2, title_height), text_anchor="middle", font_size=15))
    title_box = svgwrite.shapes.Rect(insert=(width / 2 - len(title) * 4, 30), size=(len(title) * 8, 30), stroke='black', fill='none')
    dwg.add(title_box)

    # Plot lines
    line_styles = ['solid', 'dash', 'dot']
    colors = ['#555555', '#555555', '#555555']

    for i, y_values in enumerate(y_values_list):
        scaled_x = [padding_left + (width - padding_left - 10) * (x - x_min) / (x_max - x_min) for x in x_values]
        scaled_y = min_max_scaling(y_values, y_label_positions[-1], y_label_positions[0])
        points = [(float(x), float(y)) for x, y in zip(scaled_x, scaled_y)]
        polyline = dwg.polyline(points=points, fill='none', stroke=colors[i], stroke_width=2)

        if line_styles[i] == 'dash':
            polyline.dasharray([8, 4])
        elif line_styles[i] == 'dot':
            polyline.dasharray([2, 4])

        dwg.add(polyline)

        # Legend entries with different line styles
        if (len(y_values_list) > 1):
            legend_start_x = axis_end_x + 30
            legend_start_y = axis_end_y + 30 * i
            legend_line_start_x = legend_start_x - 10

            if line_styles[i] == 'dash':
                dwg.add(svgwrite.shapes.Line(start=(legend_line_start_x, legend_start_y + 5), end=(legend_line_start_x + 40, legend_start_y + 5),
                                            stroke=colors[i], stroke_width=2, stroke_dasharray="8,4"))
            elif line_styles[i] == 'dot':
                dwg.add(svgwrite.shapes.Line(start=(legend_line_start_x, legend_start_y + 5), end=(legend_line_start_x + 40, legend_start_y + 5),
                                            stroke=colors[i], stroke_width=2, stroke_dasharray="2,4"))
            else:
                dwg.add(svgwrite.shapes.Line(start=(legend_line_start_x, legend_start_y + 5), end=(legend_line_start_x + 40, legend_start_y + 5),
                                            stroke=colors[i], stroke_width=2))

            dwg.add(svgwrite.text.Text(labels[i], insert=(legend_start_x + 20, legend_start_y), text_anchor="start", font_size=14))

    # Save SVG file
    dwg.saveas("svg_charts\\" + str(index) + ".svg")



def create_bar_chart(x_values, y_values_list, title, labels, x_axis_title='X-axis', y_axis_title='Y-axis', width=400, height=300):
    legend_width = 120
    title_height = 50
    dwg = svgwrite.Drawing(filename=title + '.svg', size=(f'{width + legend_width}px', f'{height + title_height}px'))

    # Define graph parameters
    x_values_numeric = list(range(len(x_values)))
    x_min, x_max = min(x_values_numeric), max(x_values_numeric)
    y_min = 0  # Set minimum y-value for bar charts
    y_max = max(max(y) for y in y_values_list)

    padding_left = 70
    padding_bottom = 50
    axis_start_x = padding_left
    axis_end_x = width - 10

    axis_start_y = height - padding_bottom - 30 + title_height
    height -= 30

    axis_end_y = padding_bottom + title_height

    num_labels_x = len(x_values)
    x_label_positions = [axis_start_x + i * (width - padding_left - 10) // (num_labels_x + 1) for i in range(1, num_labels_x + 1)]
    x_label_values = x_values

    num_labels_y = 3
    y_label_positions = [axis_start_y - i * (height - padding_bottom - 10) / (num_labels_y + 1) for i in range(1, num_labels_y + 1)]
    y_label_values = [str(round(float(y_min + i * (y_max - y_min) / (num_labels_y)))) for i in range(1, num_labels_y + 1)]

    add_axis(dwg, axis_start_x, axis_start_y, axis_end_x, axis_start_y, 'x', x_label_values, x_label_positions, x_axis_title, title_height)
    add_axis(dwg, axis_start_x, axis_start_y, axis_start_x, axis_end_y, 'y', y_label_values, y_label_positions, y_axis_title, title_height)

    dwg.add(svgwrite.text.Text(title, insert=(width / 2, title_height), text_anchor="middle", font_size=20))
    title_box = svgwrite.shapes.Rect(insert=(width / 2 - len(title) * 5, 30), size=(len(title) * 10, 30), stroke='black', fill='none')
    dwg.add(title_box)

    # Plot bar charts
    bar_width = (width - padding_left - 10) / len(x_values) * 0.8  # Adjusted width for bars
    line_styles = ['solid', 'dash', 'dot']
    for i, y_values in enumerate(y_values_list):
        for j, x in enumerate(x_values):
            bar_height = height - ((height - padding_bottom - title_height) * (y_values[j] - y_min)) / (y_max - y_min) + title_height - padding_bottom
            line_start_x = x_label_positions[j] - bar_width / 2 + i * bar_width
            line_end_x = x_label_positions[j] + bar_width / 2 + i * bar_width
            mid_point = (line_start_x + line_end_x) / 2  # Midpoint between line_start_x and line_end_x
            if line_styles[i] == 'dash':
                line = svgwrite.shapes.Line(start=(mid_point, height - padding_bottom + title_height), end=(mid_point, bar_height), stroke='#444444', stroke_width=4, stroke_dasharray="8,4")
            elif line_styles[i] == 'dot':
                line = svgwrite.shapes.Line(start=(mid_point, height - padding_bottom + title_height), end=(mid_point, bar_height), stroke='#444444', stroke_width=4, stroke_dasharray="2,4")
            else:  # For solid lines
                line = svgwrite.shapes.Line(start=(mid_point, height - padding_bottom + title_height), end=(mid_point, bar_height), stroke='#444444', stroke_width=4)
            dwg.add(line)

        # Legend entry for bar charts
        legend_start_x = axis_end_x + 30  # Adjusted x-coordinate for legend
        legend_start_y = axis_end_y + 30 * i  # Y-coordinate for the legend items
        legend_line_start_x = legend_start_x - 10  # X-coordinate for the legend lines

        dwg.add(svgwrite.shapes.Line(start=(legend_line_start_x, legend_start_y + 5), end=(legend_line_start_x + 40, legend_start_y + 5),
                                    stroke='#555555', stroke_width=4))

        dwg.add(svgwrite.text.Text(labels[i], insert=(legend_start_x + 20, legend_start_y), text_anchor="start", font_size=14))

    # Save SVG file
    dwg.save()


def create_scatter_plot(x_values_list, y_values_list, title, titles, symbols, x_axis_title='X-axis', y_axis_title='Y-axis', width=400, height=300):
    title_height = 50
    legend_width = 120
    dwg = svgwrite.Drawing(size=(f'{width + legend_width}px', f'{height + title_height}px'))

    # Define graph parameters
    x_min = min(min(x) for x in x_values_list)
    x_max = max(max(x) for x in x_values_list)
    y_min = min(min(y) for y in y_values_list)
    y_max = max(max(y) for y in y_values_list)

    padding_left = 70
    padding_bottom = 50
    axis_start_x, axis_end_x = padding_left, width - 10
    axis_start_y, axis_end_y = height - padding_bottom - 30 + title_height, padding_bottom + title_height
    height -= 30

    num_labels_x = 4
    x_label_positions = [axis_start_x + i * (width - padding_left - 10) // (num_labels_x + 1) for i in range(1, num_labels_x + 1)]
    x_label_values = [str(round(float(x_min + i * (x_max - x_min) / (num_labels_x + 1)))) for i in range(1, num_labels_x + 1)]

    num_labels_y = 3
    y_label_positions = [axis_start_y - i * (height - padding_bottom - 10) // (num_labels_y + 2) for i in range(1, num_labels_y + 1)]
    y_label_values = [str(round(float(y_min + i * (y_max - y_min) / (num_labels_y + 2)))) for i in range(1, num_labels_y + 1)]

    # Add axes
    add_axis(dwg, axis_start_x, axis_start_y, axis_end_x, axis_start_y, 'x', x_label_values, x_label_positions, x_axis_title, title_height)
    add_axis(dwg, axis_start_x, axis_start_y, axis_start_x, axis_end_y, 'y', y_label_values, y_label_positions, y_axis_title, title_height)

    dwg.add(svgwrite.text.Text(title, insert=(width / 2, title_height), text_anchor="middle", font_size=20))
    title_box = svgwrite.shapes.Rect(insert=(width / 2 - len(title) * 5 - 5, 30), size=(len(title) * 10, 30), stroke='black', fill='none')
    dwg.add(title_box)

    symbols_mapping = {
        'circle': 'circle',
        'star': 'polygon',
        'triangle': 'polygon'
    }

    # Plot scatter points for each dataset
    for i, (x_values, y_values) in enumerate(zip(x_values_list, y_values_list)):
        symbol = symbols[i]
        symbol_type = symbols_mapping.get(symbol)
        if symbol_type:
            for x, y in zip(x_values, y_values):
                scaled_x = padding_left + (width - padding_left - 10) * (x - x_min) / (x_max - x_min)
                scaled_y = height - ((height - padding_bottom - title_height) * (y - y_min)) / (y_max - y_min) + title_height - padding_bottom

                if symbol == 'circle':
                    circle_radius = 7
                    dwg.add(svgwrite.shapes.Circle(center=(scaled_x, scaled_y), r=circle_radius, fill='#555555'))
                elif symbol == 'star':
                    star_points = []
                    outer_radius = 12
                    inner_radius = 5
                    for j in range(5):
                        angle_outer = (4 * math.pi * j) / 5 - math.pi / 2
                        x_outer = scaled_x + outer_radius * math.cos(angle_outer)
                        y_outer = scaled_y + outer_radius * math.sin(angle_outer)
                        star_points.append((x_outer, y_outer))

                        angle_inner = (4 * math.pi * (j + 0.5)) / 5 - math.pi / 2
                        x_inner = scaled_x + inner_radius * math.cos(angle_inner)
                        y_inner = scaled_y + inner_radius * math.sin(angle_inner)
                        star_points.append((x_inner, y_inner))

                    dwg.add(svgwrite.shapes.Polygon(points=star_points, fill='#555555'))
                elif symbol == 'triangle':
                    triangle_size = 9
                    triangle_points = [
                        (scaled_x, scaled_y - triangle_size),
                        (scaled_x + triangle_size, scaled_y + triangle_size),
                        (scaled_x - triangle_size, scaled_y + triangle_size)
                    ]
                    dwg.add(svgwrite.shapes.Polygon(points=triangle_points, fill='#555555'))

    # Add legend
    legend_x = axis_end_x + 30
    legend_y = axis_end_y + 30
    legend_spacing = 20

    for i, (title, symbol) in enumerate(zip(titles, symbols)):
        legend_symbol = None

        if symbol == 'circle':
            circle_radius = 7
            legend_symbol = svgwrite.shapes.Circle(center=(legend_x, legend_y + i * legend_spacing), r=circle_radius, fill='#555555')
        elif symbol == 'star':
            star_points = []
            outer_radius = 12
            inner_radius = 5
            for j in range(5):
                angle_outer = (4 * math.pi * j) / 5 - math.pi / 2
                x_outer = legend_x + outer_radius * math.cos(angle_outer)
                y_outer = legend_y + i * legend_spacing + outer_radius * math.sin(angle_outer)
                star_points.append((x_outer, y_outer))

                angle_inner = (4 * math.pi * (j + 0.5)) / 5 - math.pi / 2
                x_inner = legend_x + inner_radius * math.cos(angle_inner)
                y_inner = legend_y + i * legend_spacing + inner_radius * math.sin(angle_inner)
                star_points.append((x_inner, y_inner))

            legend_symbol = svgwrite.shapes.Polygon(points=star_points, fill='#555555')
        elif symbol == 'triangle':
            triangle_size = 9
            triangle_points = [
                (legend_x, legend_y + i * legend_spacing - triangle_size),
                (legend_x + triangle_size, legend_y + i * legend_spacing + triangle_size),
                (legend_x - triangle_size, legend_y + i * legend_spacing + triangle_size)
            ]
            legend_symbol = svgwrite.shapes.Polygon(points=triangle_points, fill='#555555')

        dwg.add(legend_symbol)
        legend_text = svgwrite.text.Text(title, insert=(legend_x + 15, legend_y + i * legend_spacing + 3), text_anchor="start", font_size=14)
        dwg.add(legend_text)

    # Save SVG file
    dwg.save()

success = []

for i in range(1, 8823):
    try:
        x_values, y_values, title, x_labels, y_labels, x_axis_title, y_axis_title = parse_vega_scene_graph("scenegraphs/" + str(i) + ".json")
        create_line_graph(x_values, [y_values], title, i, x_labels, y_labels, labels=[1, 2, 3], x_axis_title=x_axis_title, y_axis_title=y_axis_title)
        success.append(i)
    except:
        print("Index", i, "failed")
print(success)
