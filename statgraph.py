import plotly.graph_objects as go

# Plotly API support

# process whole entity sentiment data in to the following format
# {alternative:([sentiment], [order]), alternative:([sentiment], [order])}
def process_whole_entity_data(entity_file_path):
    data_dict = {}
    data_file = open(entity_file_path, mode="r")
    for line in data_file:
        datum = line.rstrip().lstrip().split(" ")
        alternative = datum[0]
        sentiment = datum[1]
        order = datum[2]
        if alternative in data_dict:
            data_dict[alternative][0].append(float(sentiment))
            data_dict[alternative][1].append(int(order))
        else:
            data_dict[alternative] = ([float(sentiment)], [int(order)])

    return data_dict


if __name__ == '__main__':

    whole_data_dict = process_whole_entity_data("whole_entity_sentiment/1086301-berkeley-vs-yale.txt")

    fig = go.Figure()

    color_diff = 50

    for alternative, alter_data in whole_data_dict.items():
        sentiments_y = alter_data[0]
        orders_x = alter_data[1]

        fig.add_trace(go.Scatter(
            x=orders_x, y=sentiments_y,
            name=alternative,
            mode='markers',
            marker_color='rgba({}, {}, 0, .8)'.format(color_diff, color_diff, color_diff)
        ))

        color_diff += 200

    # Set options common to all traces with fig.update_traces
    fig.update_traces(mode='markers', marker_line_width=2, marker_size=10)
    fig.update_layout(title='Styled Scatter',
                      yaxis_zeroline=False, xaxis_zeroline=False)

    fig.write_image("statgraph/whole_entity_sentiment/1086301-berkeley-vs-yale.png")