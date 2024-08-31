# Need to change all of this to use Gmail




# A function to send the that gets the email and password and send login information to the parent
def login_email(email, password):
    """
	Sends an email notification to the user regarding the creation of their Powerschool
	parent account.
	
	Parameters:
	    email (str): The email address of the user.
	    password (str): The password for the user's Powerschool account.
	
	Returns:
	    [str, str]: The subject of the email and the email body.
	"""
    subject = "Powerschool Account Creation Notification"

    body = (
        """<p>Good day,</p>

    <p>Your PowerSchool parent account has been created. You may access your child(ren)’s grades and school information by going to the following website:</p>

    <p><a href='https://min201.powerschool.com'>https://min201.powerschool.com</a></p>

    <p>Your Powerschool ID (or username) is: """
        + email
        + """<br>Your password (until you change it) is: """
        + password
        + """</p>

    <p>You can also install the PowerSchool smartphone app to quickly see your child(ren)’s grades (although the website has more features), using the above username / password and a district code of DDMK.</p>

    <p>Here is a link to a PDF regarding checking your student’s fees or lunch balances and paying it: <a href='https://www.min201.org/parents/powerschool#fs-panel-6858'>https://www.min201.org/parents/powerschool#fs-panel-6858</a></p>

    <p>If you have any other questions, feel free to email <a href='mailto:pshelp@min201.org'>pshelp@min201.org</a> and someone from the tech team will respond to you.</p>

    <p>Have a great day,</p>

    <p>David Plaskett</p>"""
    )
    return [subject, body]


# Function for email to send for no custodial email.
def no_email(last_first, number):
    """
    Sends an email notification to the specified email address indicating that the
    student does not have a custodial email.

    Parameters:
        last_first (str): The last name and first name of the student.
        number (str): The student's number.

    Returns:
        None
    """
    subject = "No custodial email for student"
    body = (
        "The student, "
        + last_first
        + " ("
        + number
        + ")"
        + ", does not have a custodial email. No data access account can be created."
    )
    return [subject, body]


# Function for email to send for no custodial email.
def no_access(last_first, number):
    """
    Sends an email notification indicating that the student was not set up for data access.

    Parameters:
        last_first (str): The last name and first name of the student.
        number (str): The student's number.

    Returns:
        None
    """
    subject = "No access created for student"
    body = (
        "The student, "
        + last_first
        + " ("
        + number
        + ")"
        + ", was not set up for data access. No data access account can be created."
    )
    return [subject, body]


# Function for email to send for no custody is sent.
def no_custody(last_first, number):
    """
    Sends an email notification indicating that the student does not have a contact with custody.

    Parameters:
        last_first (str): The last name and first name of the student.
        number (str): The student's number.

    Returns:
        None
    """
    subject = "No custody for student"
    body = (
        "The student, "
        + last_first
        + " ("
        + number
        + ")"
        + ", does not have a contact with custody. No data access account can be created."
    )
    return [subject, body]
    