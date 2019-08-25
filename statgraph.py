import plotly.graph_objects as go
from glob import glob

# Plotly API support

# process entity sentiment data in to the following format
# {alternative:([sentiment], [order]), alternative:([sentiment], [order])}
def process_entity_data(entity_file_path):
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

# generate scatter graph for entity sentiment data (anomalous)
def gen_scatter_graph_entity_sentiment_data(data_filepath, filename):

    whole_data_dict = process_entity_data(data_filepath)

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

    filename = filename.replace("txt", "png")
    fig.write_image("statgraph/individ_entity_sentiment/{}".format(filename))


def main():
    # go through every txt file in the target data folder
    discussion_folder_path = "individ_entity_sentiment\*.txt"
    for file_path in glob(discussion_folder_path):

        # get file name and alternative name from data
        file_name = file_path.split("\\")[1]

        # do the entity job and save result
        gen_scatter_graph_entity_sentiment_data(file_path, file_name)


if __name__ == '__main__':
    main()

