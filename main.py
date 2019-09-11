from DiscussionChuck import DiscussionChuck, DiscussionChuckContainer
from output import *

from progressbar import progressbar
import re
from glob import glob
import json


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
            # save the previous conversation if existf
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
# allow multiple keywords for target_words
# such as Sunhee: target_words can be: "Sunhee's Farm|Korean"
# Keywords will be split by |
def similar_entity_recognition(entity, target_words):
    keywords = target_words.split("|")
    for keyword in keywords:
        if keyword.rstrip().lstrip() != "":
            try:
                similar_pattern = re.compile(r'.*?{}.*?'.format(keyword), re.IGNORECASE)
                if re.match(similar_pattern, entity):
                    return True
            except:
                if keyword == entity:
                    return True


    return False


# generate individual Entity Sentiment Output of the most-chucks user
def generate_most_chuck_entity_sentiment(alternatives, filename, chuck_container):

    user_most_chucks = chuck_container.getUserMostChucks()

    individ_alter_data = list()

    # set up entity sentiment for most-chucks user
    for i in progressbar(range(len(user_most_chucks))):
        chuck = user_most_chucks[i]
        chuck.gen_google_entity_sentiment()

    # tide up all entity sentiments
    # collect sentiment in all message of one user in a discussion
    for chuck in user_most_chucks:

        for entity, sentiment_data in chuck.entity_sentiment_list:
            # format the potential sentiment data in the sentiment list
            sentiment = ""
            for sentiment_datum in sentiment_data:
                sentiment += "{:.3f} ".format(sentiment_datum)

            for alternative in alternatives:
                if similar_entity_recognition(entity, alternative):
                    alter_datum = (alternative, sentiment, chuck.order, chuck.user_id)
                    individ_alter_data.append(alter_datum)

    userid = user_most_chucks[0].user_id
    output_general_entity_sentiment("individ_entity_sentiment/{}-{}".format(userid, filename), individ_alter_data)


# generate individual Entity Sentiment Output of the most-chucks user
def generate_whole_entity_sentiment(alternatives, filename, chuck_container):

    # set up entity sentiment for each chuck
    for i in progressbar(range(len(chuck_container))):
        chuck = chuck_container[i]
        chuck.gen_google_entity_sentiment()


    whole_alter_data = list()

    for chuck in chuck_container:
        # go through all entity sentiment in one discussion chuck
        for entity, sentiment_data in chuck.entity_sentiment_list:

            # format the potential sentiment data in the sentiment list
            sentiment = ""
            for sentiment_datum in sentiment_data:
                sentiment += "{:.3f} ".format(sentiment_datum)

            # identify the entity text as alternative and save the sentiment and its order
            # also includes the name of discussion chuck
            for alternative in alternatives:
                if similar_entity_recognition(entity, alternative):
                    alter_datum = (alternative, sentiment, chuck.order, chuck.user_id)
                    whole_alter_data.append(alter_datum)
                    break

    output_general_entity_sentiment("whole_entity_sentiment/{}".format(filename), whole_alter_data)


# generate all sentiment data in a json output
# {"1": chuck data, "2": chuck data, .....}
# "1", "2" represents message index in one discussion
def generate_all_sentiment(output_filename, chuck_container):
    data = dict()
    # set up all sentiment for each chuck
    for i in progressbar(range(len(chuck_container))):
        chuck = chuck_container[i]
        chuck.gen_google_all_data()

    data["length"] = len(chuck_container)
    for i in range(len(chuck_container)):
        data[str(i+1)] = chuck_container[i].whole_sentiment_data

    output_filename = "all_sentiment_data/{}".format(output_filename)
    with open(output_filename, "w") as output_file:
        json.dump(data, output_file)


def main():
    # go through every txt file in the target data folder
    discussion_folder_path = "SlackDiscussion\*.txt"
    for file_path in glob(discussion_folder_path):
        # generate chuck container for data
        chuck_container = discussionFileProcessor(file_path)

        # get file name and alternative name from data
        file_name = file_path.split("\\")[1]

        # assumed alternatives are given
        alternatives = ["Forrest Gump|FG",
                        "Avengers|AVE",
                        "The Matrix|MAT",
                        "Star Wars|SW",
                        "Interstellar|INT",
                        "Despicable Me|DM",
                        "Avatar|TAR",
                        "Titanic|TTN",
                        "Inception|INC",
                        "La La Land|LLL"]


        # do the entity job and save result
        generate_whole_entity_sentiment(alternatives, file_name, chuck_container)


def main_all_sentiment_data():
    # go through every txt file in the target data folder
    discussion_folder_path = "data\CollegeConfidential\*.txt"
    for file_path in glob(discussion_folder_path):
        # generate chuck container for data
        chuck_container = discussionFileProcessor(file_path)

        # json file output
        output_file_name = file_path.split("\\")[2].replace(".txt", ".json")

        generate_all_sentiment(output_file_name, chuck_container)


if __name__ == '__main__':
    main()


