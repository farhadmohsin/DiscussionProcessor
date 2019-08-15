from DiscussionChuck import DiscussionChuck, DiscussionChuckContainer
import re

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




