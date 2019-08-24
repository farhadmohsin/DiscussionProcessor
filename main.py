from DiscussionChuck import DiscussionChuck, DiscussionChuckContainer
from Output import *

from progressbar import progressbar
import re
from glob import glob


# Discussion TXT File Processor for the format of <<<user id>>> and message
# return a DiscussionChuckContainer geenrated from the discussion
def discussionFileProcessor(file_path):
    discussion_file = open(file_path, "r")
    user_id_pattern = re.compile(r'<<<(.*?)>>>')

    # contains all chucks from the discussion
    chuck_container = DiscussionChuckContainer()

    # processing the file
    order = 0
    message = ""
    user_id = ""
    for line in discussion_file:
        match_result = re.findall(user_id_pattern, line)
        # new begin, new message
        if len(match_result) != 0:
            # save the previous conversation if exist
            if message != "":
                # clean up redundant space and \n
                message = message.lstrip().rstrip()
                new_chuck = DiscussionChuck(user_id, message, order)
                chuck_container.append(new_chuck)

            # reset variable
            message = ""
            user_id = match_result[0]
            order += 1

        else:
            # increment message
            message += line

    return chuck_container

# return True if this entity include target word
def similar_entity_recognition(entity, target_word):
    similar_pattern = re.compile(r'.*?{}.*?'.format(target_word), re.IGNORECASE)
    if re.match(similar_pattern, entity):
        return True
    else:
        return False


# generate individual Entity Sentiment Output of the most-chucks user
def generate_most_chuck_entity_sentiment(alternatives, filename, chuck_container):

    user_most_chucks = chuck_container.getUserMostChucks()

    alternative_one = alternatives[0]
    alternative_two = alternatives[1]

    sentiment_contain_one = []
    sentiment_contain_two = []

    # tide up all entity sentiments
    # collect sentiment in all message of one user in a discussion
    for chuck in user_most_chucks:

        order_sentiment_one = list()
        order_sentiment_two = list()
        for entity, sentiment in chuck.entity_sentiment_list:
            if similar_entity_recognition(alternative_one, entity):
                order_sentiment_one.append(sentiment)
            elif similar_entity_recognition(alternative_two, entity):
                order_sentiment_two.append(sentiment)

        # collect sentiment in one message
        sentiment_contain_one.append(order_sentiment_one)
        sentiment_contain_two.append(order_sentiment_two)

    sentiment_data = [(alternative_one, sentiment_contain_one), (alternative_two, sentiment_contain_two)]
    output_individual_entity_sentiment("ind_entity_sentiment/{}".format(filename), sentiment_data)

# generate individual Entity Sentiment Output of the most-chucks user
def generate_whole_entity_sentiment(alternatives, filename, chuck_container):

    alternative_one = alternatives[0]
    alternative_two = alternatives[1]

    whole_alter_data = list()

    for chuck in chuck_container:
        # go through all entity sentiment in one discussion chuck
        for entity, sentiment in chuck.entity_sentiment_list:
            # identify the entity text as alternative and save the sentiment and its order
            if similar_entity_recognition(alternative_one, entity):
                alter_datum = (alternative_one, sentiment, chuck.order)
                whole_alter_data.append(alter_datum)
            elif similar_entity_recognition(alternative_two, entity):
                alter_datum = (alternative_two, sentiment, chuck.order)
                whole_alter_data.append(alter_datum)

    output_whole_entity_sentiment("whole_entity_sentiment/{}".format(filename), whole_alter_data)


def main():
    # go through every txt file in the target data folder
    discussion_folder_path = "data\CollegeConfidential\*.txt"
    for file_path in glob(discussion_folder_path):
        # generate chuck container for data
        chuck_container = discussionFileProcessor(file_path)

        # set up entity sentiment for each chuck
        for i in progressbar(range(len(chuck_container))):
            chuck = chuck_container[i]
            chuck.gen_entity_sentiment()

        # get file name and alternative name from data
        file_name = file_path.split("\\")[2]
        datum = file_name.split("-")
        alternatives = (datum[1], datum[3])

        # do the entity job and save result
        generate_whole_entity_sentiment(alternatives, file_name, chuck_container)





if __name__ == '__main__':
    main()


