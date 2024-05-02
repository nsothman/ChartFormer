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

def parse_vega_scene_graph(file_path):
    with open(file_path, 'r') as file:
        vega_spec = json.load(file)

        # Extracting data from the Vega scene graph
        data_values = []
        x_values = []
        y_values_list = []
        title = None
        x_axis_title = None
        y_axis_title = None
        x_labels = []
        y_labels = []
        def extract_data(item):
            nonlocal data_values, x_values, y_values_list, title, x_axis_title, y_axis_title
            if 'items' in item:
                for sub_item in item['items']:
                    if sub_item.get("marktype") == "line":
                        for mark_item in sub_item.get("items", []):
                            if "x" in mark_item and "y" in mark_item:
                                data_values.append(mark_item)
                                x_values.append(mark_item['x'])
                                y_values_list.append(mark_item['y'])
                    elif sub_item.get("marktype") == "rect":
                        for mark_item in sub_item.get("items", []):
                            if "description" in mark_item and "y" in mark_item:
                                # print(mark_item['description'].split(";")[0].split(": ")[1])
                                data_values.append(mark_item['description'].split(";")[0].split(": ")[1])
                                x_values.append(mark_item['description'].split(";")[0].split(": ")[1])
                                y_values_list.append(mark_item['y'])
                    elif sub_item.get("role") == "title":
                        title_item = sub_item.get("items", [])[0]
                        title_item = title_item.get("items", [])[0]
                        if title_item.get("role") == "title-text":
                            title_item = title_item.get("items")[0]
                            title = title_item.get("text")[0]
                    elif sub_item.get("role") == "axis":
                        axis_items = sub_item.get("items")
                        axis_items = axis_items[0].get("items", [])
                        for axis_item in axis_items:
                            if axis_item.get("role") == "axis-title":
                                if axis_item.get("items")[0]:
                                    if axis_item.get("items")[0].get("baseline") == "bottom":
                                        y_axis_title = axis_item.get("items")[0].get("text")
                                    elif axis_item.get("items")[0].get("baseline") == "top":
                                        x_axis_title = axis_item.get("items")[0].get("text")
                            elif axis_item.get("role") == "axis-label":
                                for item in axis_item.get("items", []):
                                    if item.get("x") < 0:
                                        y_labels.append(item.get("text"))
                                    else:
                                        x_labels.append(item.get("text"))
                                    


                    extract_data(sub_item)

        if extract_data(vega_spec) == 0:
            return 0, 0, 0, 0, 0, 0, 0
        y_labels_int = [int(y) for y in y_labels]
        y_max = max(y_values_list)
        y_min = min(y_values_list)
        actual_min = ((200 - y_max) / 200) * max(y_labels_int)
        y_labels = []
        for i in range(4):
            y_labels.append(str(round(actual_min + i * ((max(y_labels_int) - actual_min) / 4))))
        return x_values, y_values_list, title, x_labels, y_labels, x_axis_title, y_axis_title

