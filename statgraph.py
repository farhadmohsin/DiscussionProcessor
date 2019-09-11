import plotly.graph_objects as go
from glob import glob

# Plotly API support

# process entity sentiment data in to the following format
# {userid:{alternative:([sentiment], [order]), alternative:([sentiment], [order])}, userid:...}
def process_entity_data(entity_file_path):
    data_dict = {}
    data_file = open(entity_file_path, mode="r")
    for line in data_file:
        datum = line.rstrip().lstrip().split("|")
        alternative = datum[0]
        sentiment = datum[1]
        order = datum[3]
        userid = datum[4]
        if userid in data_dict:
            alternative_data = data_dict[userid]
            if alternative in alternative_data:
                alternative_data[alternative][0].append(float(sentiment))
                alternative_data[alternative][1].append(int(order))
            else:
                alternative_data[alternative] = ([float(sentiment)], [int(order)])
        else:
            data_dict[userid] = dict()
            data_dict[userid][alternative] = ([float(sentiment)], [int(order)])

    return data_dict

# generate scatter graph for entity sentiment data (all user)
def gen_scatter_graph_entity_sentiment_data(data_filepath, filename):

    data_dict = process_entity_data(data_filepath)



    for userid, alternative_data in data_dict.items():
        colors = [(255, 0, 102), (153, 0, 0),
                  (102, 255, 204), (102, 102, 255),
                  (204, 0, 204), (255, 135, 0),
                  (51, 136, 103), (176, 125, 0),
                  (208, 0, 129), (186, 0, 28)]
        color_index = 0
        fig = go.Figure()

        for alternative, alter_data in alternative_data.items():
            sentiments_y = alter_data[0]
            orders_x = alter_data[1]

            fig.add_trace(go.Scatter(
                x=orders_x, y=sentiments_y,
                name=alternative,
                mode='markers',
                marker_color='rgba({}, {}, {}, .8)'.format(colors[color_index][0],
                                                          colors[color_index][1], colors[color_index][2])
            ))

            color_index += 1


        # Set options common to all traces with fig.update_traces
        fig.update_traces(mode='markers', marker_line_width=2, marker_size=8)
        fig.update_layout(title='Styled Scatter',
                          yaxis_zeroline=False, xaxis_zeroline=False)

        filename = filename.replace(".txt", "")
        fig.write_image("statgraph/{}_{}.png".format(userid, filename))


def main():
    # go through every txt file in the target data folder
    discussion_folder_path = "individ_entity_sentiment\*.txt"
    for file_path in glob(discussion_folder_path):

        # get file name and alternative name from data
        file_name = file_path.split("\\")[1]

        # do the entity job and save result
        gen_scatter_graph_entity_sentiment_data(file_path, file_name)


if __name__ == '__main__':
    file_path = "whole_entity_sentiment\\restaurant_preferance.txt"
    gen_scatter_graph_entity_sentiment_data(file_path, "restaurant_preference")

