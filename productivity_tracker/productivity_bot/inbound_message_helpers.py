
from productivity_bot.models import User, ActiveLoops

COMMAND_ERROR = 'Sorry, that was an invalid command.'
SESSION_BEGIN = 'Working session has begun! To end the session, say "stop"'
SESSION_END = 'Working session has ended! See a summary of your work here: %s'

################################################################################
# used to parse user responses and redirect to react
#
# called by productivity_bot.ChatbotEvent.post
################################################################################
def handle_inbound_message(mssg_text, user_name, space_name):
    """Handles inbound messages sent to the bot.

    Will react according to the user's input:
        'start <X> hours' -> Start a working session and ping me every X hours
        'stop' -> stop the existing working session and send me a summary of my
            working session
        '<XYZ>' -> log that I completed <XYZ>

    Args:
        mssg_text: The raw string sent to this bot from the user via hangouts chat
        user_name: The user's name field (via 
            https://developers.google.com/hangouts/chat/reference/rest/v1/User)
        space_name: The space's name field (via 
            https://developers.google.com/hangouts/chat/reference/rest/v1/spaces)

    Returns:
        The text that the bot should send back to the user via the hangouts chat DM

    Raises:
        No errors should be raised. An error would be unexpected behavior.
    """
    mssg = mssg_text.split()
    user = User.objects.get_or_create(
        space_name=space_name, 
        user_name=user_name
    )[0]
    # User wants to start working session
    if mssg[0] == 'start':
        if (len(mssg) != 3 or not (mssg[1].isdigit() or mssg[2] != 'hours')): 
            return COMMAND_ERROR

        mssg_freq = mssg[1]
        response = start_active_loop(user, mssg_freq, space_name)
        return response
    # User wants to stop working session
    elif mssg[0] == 'stop':
        if len(mssg) != 1 and not in_active_loop(user): 
            return COMMAND_ERROR

        response = end_active_loop(user)
        return response
    # User wants to log work
    else:
        if not in_active_loop(user): 
            return COMMAND_ERROR

        response = log_user_response(user, mssg)
        return response


def start_active_loop(user, mssg_freq, space_name):
    """Starts a working session/active loop for the user

    This function will create an ActiveLoop object for the user indicating that
    the user is in a working session and should be pinged every mssg_freq
    minutes. If the user is already in a working session, this function will
    delete the existing object and create a new one, allowing users to change
    their frequencies on-the-fly.

    Args:
        user: The User object referring to the user who's requested the active loop
        mssg_freq: The frequency at which the user should be pinged
        space_name: The space's name field (via 
            https://developers.google.com/hangouts/chat/reference/rest/v1/spaces)

    Returns:
        The text that the bot should send back to the user via the hangouts chat DM

    Raises:
        No errors should be raised. An error would be unexpected behavior.
    """

    # Check if this user is in an active loop
    # If they are, delete that active loop to create a new one.
    active_loop = in_active_loop(user)
    if active_loop: active_loop.delete()

    active_loop = ActiveLoops(
        user=user, 
        mssg_freq=int(mssg_freq),
        mins_to_mssg = -1*int(mssg_freq))
    active_loop.save()

    return SESSION_BEGIN% mssg_freq


def end_active_loop(user):
    """Ends a working session/active loop for the user

    This function will delete an ActiveLoop object for the user. If no object
    exists, it will return gracefully.
    This function will also 'wrap up' the working session by copying the user's
    data into a google sheet, drawing necessary conclusions for the user, and
    displaying it back in the DM.

    Args:
        user: The User object referring to the user who's requested the active loop
    
    Returns:
        The text that the bot should send back to the user via the hangouts chat DM

    Raises:
        No errors should be raised. An error would be unexpected behavior.
    """

    active_loop = in_active_loop(user)
    if not active_loop: return "I can't believe you've done this"
    
    # TODO(ahez): copy SQL data to google sheet
    # TODO(ahez): use GCP NLP API to categorize the data
    # TODO(ahez): Visualize the data with sheets Charts (& maybe data studio)

    active_loop.delete()
    summary_link = "google.com"
    return SESSION_END% summary_link


def in_active_loop(user):
    """Checks if there exists an ActiveLoop object for specified User object

    This function determines if the specified user is in an active loop. If it
    is, the function will return the object. Otherwise, it will return False.

    Args:
        user: The User object referring to the user who's requested the active loop
    
    Returns:
        ActiveLoop object: if one exists for this user
        False:             otherwise

    Raises:
        No errors should be raised. An error would be unexpected behavior.
    """

    active_loop = ActiveLoops.objects.filter(user=user)
    if active_loop.exists(): return active_loop[0]
    else: return False


def log_user_response(user, text):
    """Logs a user's response as a completed task

    When the user reports completed work, this function is called to log the
    data. It will be stored in the UserResponse table and then copied over to a 
    google sheet in end_active_loop()

    Args:
        user: The User object referring to the user who's requested the active loop
        text: The raw text sent by the user. To be stored now and analyzed later.
    
    Returns:
        The text that the bot should send back to the user via the hangouts chat DM

    Raises:
        No errors should be raised. An error would be unexpected behavior.
    """

    # TODO(ahez): Implement this function
    # TODO(ahez): Decide whether to analyze data (using NLP API) here or when
    #    copying to Sheets in end_active_loop(user)


    return "Response has been logged!"
