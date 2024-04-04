import json

def parse_vega_lite_json(file_path):
    with open(file_path, 'r') as file:
        vega_lite_spec = json.load(file)

        # Extracting data from the Vega-Lite specification
        x_field = vega_lite_spec["encoding"]['x']["field"]
        y_field = vega_lite_spec["encoding"]['y']["field"]
        title = vega_lite_spec["description"]

        # Extract data points and labels
        data_values = vega_lite_spec["data"]["values"]
        if vega_lite_spec["mark"] ==  "line":
            y_values1 = []
            y_values2 = []
            y_values3 = []
            x_values = []
            colour = vega_lite_spec["encoding"]["color"]["field"]
            # x_values = [float(data_point[x_field]) for data_point in data_values]
            for data_point in data_values:
                if data_point[colour] == 1:
                    x_values.append(float(data_point[x_field]))
                    y_values1.append(float(data_point[y_field]))
                elif data_point[colour] == 2:
                    y_values2.append(float(data_point[y_field]))
                else:
                    y_values3.append(float(data_point[y_field]))
            y_values = [y_values1, y_values2, y_values3]
        elif vega_lite_spec["mark"]["type"] ==  "bar":
            x_values = [str(data_point[x_field]) for data_point in data_values]
            y_values = [float(data_point[y_field]) for data_point in data_values]
        elif vega_lite_spec["mark"]["type"] ==  "point":
            x_values1 = []
            x_values2 = []
            x_values3 = []
            y_values1 = []
            y_values2 = []
            y_values3 = []
            colour = vega_lite_spec["encoding"]["color"]["field"]
            for data_point in data_values:
                if data_point[x_field] is None or data_point[y_field] is None or data_point[colour] is None:
                    continue
                if data_point[colour] == "Europe":
                    x_values1.append(float(data_point[x_field]))
                    y_values1.append(float(data_point[y_field]))
                elif data_point[colour] == "Japan":
                    x_values2.append(float(data_point[x_field]))
                    y_values2.append(float(data_point[y_field]))
                else:
                    x_values3.append(float(data_point[x_field]))
                    y_values3.append(float(data_point[y_field]))
            x_values = [x_values1, x_values2, x_values3]
            y_values = [y_values1, y_values2, y_values3]

        # Assuming x-axis and y-axis titles are specified in the Vega-Lite specification
        x_axis_title = vega_lite_spec["encoding"]['x']["field"]
        y_axis_title = vega_lite_spec["encoding"]['y']["field"]

        # Call create_line_graph function with extracted data
        return(x_values, y_values, title, y_field, x_axis_title, y_axis_title)

