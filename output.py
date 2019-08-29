
# Output the indivdual entity sentiment data in certain format to output_path
# in the format of
#   Yale     Berkeley
# 1. 0.3     0.5
# 2. 0.1     0.4
# 3. /       0.0
#
# @param data a list of entity sentiment data
# [(alternative_one, sentiment_contain_one), (alternative_two, sentiment_contain_two)]
# alternative_xxx: Yale
# sentiment_contain_xxx: [[0.1, 0.2], [0.0], [], [0.1]]
def output_individual_entity_sentiment(output_path, ind_alter_data):
    output_file = open(output_path, "w")

    alternatives = [datum[0] for datum in ind_alter_data]

    # print alternative row
    alter_row = " \t"
    for alter in alternatives:
        alter_row += "{:<10s}".format(alter)
    output_file.write(alter_row+"\n")

    # preprocess the data
    output_data = []
    for i in range(len(ind_alter_data[0][1])):
        output_data.append([])

    for alter, each_sentiment_container in ind_alter_data:
        for i in range(len(each_sentiment_container)):
            output_data[i].append(each_sentiment_container[i])


    for i in range(len(output_data)):
        output_file.write(str(i)+"\t")
        # get largest length of sentiments
        # TODO: DEBUG
        all_length = [len(data) for data in output_data[i]]
        output_length = max(all_length) if len(all_length) != 0 else 1
        for j in range(output_length):
            if j != 0:
                output_file.write(" \t")
            for data in output_data[i]:
                if j < len(data):
                    output_file.write("{:<10.3f}".format(data[j]))
                else:
                    output_file.write("{:<10s}".format("/"))
            output_file.write("\n")

    output_file.close()

# output whole or individual entity sentiment data in one discussion
# in the format of (alternative entity sentiment discussion order)
# Yale 0.512 1
# Berkeley -0.1 1
# Berkeley -0.5 2
# Yale 0.00 2
# @params whole_alter_data:
# [(alternative, sentiment, order), (alternative, sentiment, order) by order]
# alternative: Yale or Berkeley
# sentiment: 0.1
def output_general_entity_sentiment(output_path, whole_alter_data):
    output_file = open(output_path, "w")

    # go through all data and save in output_file
    for alter, sentiment, order, user_id in whole_alter_data:
        output_file.write("{} {:.3f} {} {}\n".format(alter, sentiment, order, user_id))

    output_file.close()
