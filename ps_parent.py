"""
This module contains the ps_parent.py script.
Its purpose is to create a script that will run through and create parent accounts.
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from constants import (
    BUILDING_TECH,
    SHEET_ID,
    PS_ADMIN_URL,
    PS_ADMIN_USERNAME,
    PS_ADMIN_PASSWORD,
    DEFAULT_PASSWORD,
    PS_PARENT_URL,
)
from emails import login_email, no_access, no_custody, no_email
from gmail_functions import send_email
from sheet_functions import append_sheet
from create_service import create_service

sheet_service = create_service("sheets", "v4")
# Options for regular window
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--window-size=1920,1080")
options.add_argument("--window-position=3840,0")

# Options for incog window
incogOptions = webdriver.ChromeOptions()
incogOptions.add_argument("--incognito")
incogOptions.add_experimental_option("detach", True)
incogOptions.add_argument("--window-size=1920,1080")
incogOptions.add_argument("--window-position=3840,0")


def set_data_access():
    """
    Sets the data access for a student by clicking on the Data Access tab,
    checking the "Can Access" box, and clicking the "Submit" button.

    This function does not take any parameters.

    This function does not return anything.
    """
    # Open Data Access Tab
    browser.find_element(
        By.XPATH, '//*[@id="edit-demographics-form"]/ul/li[3]/a'
    ).click()
    # Click on Can Access Box
    browser.execute_script(
        "arguments[0].click()",
        browser.find_element(By.ID, "allow-access-to-student-data-drawer-input"),
    )
    time.sleep(5)
    # Click on Submit
    browser.execute_script(
        "arguments[0].click()",
        browser.find_element(By.ID, "demographics-panel-save-button"),
    )


# Opens the browser, gos to admin login and logs in
browser = webdriver.Chrome(options=options)
browser.get(PS_ADMIN_URL)
browser.find_element(By.ID, "fieldUsername").send_keys(PS_ADMIN_USERNAME)
browser.find_element(By.ID, "fieldPassword").send_keys(PS_ADMIN_PASSWORD)
browser.find_element(By.ID, "fieldPassword").send_keys(Keys.ENTER)

# Sets a default wait timer
browser.implicitly_wait(10)

# Go to the stored search
browser.get(
    "https://min201.powerschool.com/admin/studentlist/functions.html?ac=dbquery&stored_query=2087"
)

# Get the student count for later iteration
studentCount = browser.find_element(
    By.XPATH, '//*[@id="content-main"]/p/a'
).get_property("text")

# Create a list for tossing to a csv output with a report of what happened for each student
output = []
sheetOutput = []

# Head back to the main page
browser.get(PS_ADMIN_URL)

browser.execute_script(
    "arguments[0].scrollIntoView();",
    browser.find_element(
        By.XPATH,
        '//*[@id="studentsSelectionTable"]/table/tbody/tr[1]/td[contains(concat(" ", @class, " "), " left ")]/a',
    ),
)
browser.find_element(
    By.XPATH,
    '//*[@id="studentsSelectionTable"]/table/tbody/tr[1]/td[contains(concat(" ", @class, " "), " left ")]/a',
).click()

# This is where the for loop will go for each student
for index in range(int(studentCount)):

    # Check for the Access is turned on the the student
    if index == 0:
        accessURL = browser.current_url.replace("quicklookup", "accessaccounts")
        browser.get(accessURL)
        time.sleep(5)
    else:
        accessURL = browser.current_url.replace("contacts", "accessaccounts")
        browser.get(accessURL)
        time.sleep(5)

    # If the Access ID is blank, push the button
    if browser.find_element(By.ID, "guardianwebid").get_property("value") == "":
        browser.execute_script(
            "arguments[0].click()", browser.find_element(By.ID, "autoLink")
        )
        time.sleep(5)

    # If the Enable Parent Access is off, turn it on
    if (
        browser.execute_script(
            "return document.getElementById('allowGuardianWebAccess').checked"
        )
        is False
    ):
        browser.execute_script(
            "arguments[0].click()",
            browser.find_element(By.ID, "allowGuardianWebAccess"),
        )
        browser.execute_script(
            "arguments[0].click()", browser.find_element(By.ID, "btnSubmit")
        )

    # Head to the Contacts page
    contactsURL = browser.current_url.replace("accessaccounts", "contacts")
    browser.get(contactsURL)
    time.sleep(5)

    # Saving student name and number
    STU_NAME = browser.find_element(By.ID, "Student_Name_Type_Ahead").get_property(
        "innerText"
    )
    STU_NUM = (
        browser.find_element(By.XPATH, '//*[@id="student_details_information"]/span[2]')
        .get_property("innerText")
        .rsplit(" ")[2]
    )
    STU_SCHOOL = (
        browser.find_element(
            By.CSS_SELECTOR, "#student_details_information > span.homeSchool"
        )
        .get_property("innerText")
        .rsplit(" ")[1]
    )

    # Finds the contact table to look for custody
    contactTableRows = browser.find_elements(
        By.XPATH,
        '//*[@id="studentContactsTable"]/tbody/tr[contains(concat(" ", @class, " "), " center ")]',
    )

    # Set up two flags for decisions later
    HAS_CUSTODY = False
    CUSTODY_EMAIL = False
    ACCESS_GRANTED = False
    EMAIL_SENT = False

    # for each item in the custody table (also gets the index to add for element searching)
    for indexC, row in enumerate(contactTableRows):

        # if the current row has a custody checkmark
        if (
            browser.find_element(
                By.ID, "contact-custody-" + str(indexC)
            ).value_of_css_property("background-image")
            != "none"
        ):
            HAS_CUSTODY = True
            PARENT_NAME = browser.find_element(
                By.XPATH,
                '//*[@id="studentContactsTable"]/tbody/tr['
                + str(indexC + 2)
                + "]/td/a",
            ).text

            # If the data access checkmark is not there
            # Make condition if there is a checkmark (just proceed to the next part of the loop)
            # Check if there is an email (usually within the span for the name) Can circumvent
            # opening tab and looking there.
            if (
                len(
                    browser.find_elements(
                        By.XPATH,
                        '//*[@id="studentContactsTable"]/tbody/tr['
                        + str(indexC + 2)
                        + "]/td/div/a",
                    )
                )
                > 0
            ):
                CUSTODY_EMAIL = True
                if (
                    browser.find_element(
                        By.ID, "contact-data-access-" + str(indexC)
                    ).value_of_css_property("background-image")
                    == "none"
                ):
                    browser.find_element(
                        By.ID, "edit-details-button-" + str(indexC)
                    ).click()
                    time.sleep(2)

                    # If the tab is there, enable the account. If the tab is hidden,
                    # then proceed into the account creation process
                    if (
                        browser.find_element(
                            By.XPATH, '//*[@id="edit-demographics-form"]/ul/li[3]'
                        ).get_property("ariaHidden")
                        == "false"
                    ):
                        time.sleep(2)
                        set_data_access()
                        ACCESS_GRANTED = True

                        append_sheet(
                            sheet_service,
                            SHEET_ID,
                            "Created Accounts",
                            "USER_ENTERED",
                            [
                                [
                                    str(time.strftime("%m/%d/%Y - %I:%M %p")),
                                    STU_NAME,
                                    STU_NUM,
                                    PARENT_NAME,
                                    "Data account exists - access granted",
                                ]
                            ],
                        )
                        time.sleep(5)
                    else:
                        time.sleep(2)

                        # Open contact page and switch to that browser tab
                        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        browser.find_element(
                            By.ID, "contact-first-name-" + str(indexC)
                        ).click()
                        time.sleep(7)
                        browser.switch_to.window(browser.window_handles[1])

                        # Find the email of the contact ( gets the one marked current)
                        PARENT_EMAIL = ""
                        emailTable = browser.find_elements(
                            By.XPATH,
                            '//*[@id="email-address-table"]/tbody/tr[contains(concat(" ", @class, " "), " center ")]',
                        )
                        for indexE, row in enumerate(emailTable):
                            if (
                                browser.find_element(
                                    By.ID, "email-type-display-" + str(indexE)
                                ).get_property("innerHTML")
                                == "Current"
                            ):
                                PARENT_EMAIL = browser.find_element(
                                    By.ID, "email-address-display-" + str(indexE)
                                ).get_property("innerHTML")

                        # Opens the add account page and runs through the adding tot the fields
                        browser.execute_script(
                            "arguments[0].click()",
                            browser.find_element(By.ID, "add-account-button"),
                        )
                        browser.execute_script(
                            "arguments[0].click()",
                            browser.find_element(By.ID, "web-account-disabled-input"),
                        )
                        browser.find_element(
                            By.ID, "web-account-username-input"
                        ).send_keys(PARENT_EMAIL)
                        browser.find_element(
                            By.ID, "web-account-new-password-input"
                        ).send_keys(DEFAULT_PASSWORD)
                        browser.find_element(
                            By.ID, "web-account-confirm-password-input"
                        ).send_keys(DEFAULT_PASSWORD)

                        # Function to create four random digits
                        def random_four_digits():
                            """
                            Generates a random four-digit number.

                            Returns:
                                str: A string representation of a random four-digit number,
                                padded with leading zeros if necessary.
                            """
                            return format(random.randint(0000, 9999), "04")

                        # Make the parent password to be used later
                        PARENT_PASSWORD = "parent" + str(random_four_digits())

                        browser.find_element(
                            By.ID, "web-account-recovery-email-input"
                        ).send_keys(PARENT_EMAIL)
                        time.sleep(2)

                        # Commented out the clicking of save button form now.
                        browser.execute_script(
                            "arguments[0].click()",
                            browser.find_element(By.ID, "email-panel-save-button"),
                        )
                        time.sleep(5)

                        #  Create condition if the email already exists.
                        if len(browser.find_elements(By.ID, "contact-error")) > 0:
                            # print('error')
                            append_sheet(
                                sheet_service,
                                SHEET_ID,
                                "Running Log",
                                "USER_ENTERED",
                                [
                                    str(time.strftime("%m/%d/%Y - %I:%M %p")),
                                    STU_NAME,
                                    STU_NUM,
                                    PARENT_NAME,
                                    "Email exists - account not created",
                                ],
                            )
                            browser.close()
                            browser.switch_to.window(browser.window_handles[0])
                            time.sleep(2)
                        else:

                            # Scrolls to the relationship table
                            browser.execute_script(
                                "arguments[0].scrollIntoView();",
                                browser.find_element(By.ID, "web-account-table"),
                            )

                            # Add instuctions for attaching the account to the kid(s)
                            # (might have to add a scroll down?)
                            # Should be basically like the other edit account
                            relationshipTable = browser.find_elements(
                                By.XPATH,
                                '//*[@id="relationship-table"]/tbody/tr[contains(concat(" ", @class, " "), " center ")]',
                            )
                            schools_for_students = []
                            for indexR, row in enumerate(relationshipTable):
                                if (
                                    browser.find_element(
                                        By.ID,
                                        "relationship-custody-display-" + str(indexR),
                                    ).value_of_css_property("background-image")
                                    != "none"
                                ):
                                    schools_for_students.append(
                                        browser.find_element(
                                            By.ID,
                                            "relationship-schoolabbr-display-"
                                            + str(indexR),
                                        ).get_property("innerHTML")
                                    )
                                    browser.find_element(
                                        By.ID, "edit-details-button-" + str(indexR)
                                    ).click()

                                    time.sleep(2)
                                    set_data_access()
                                    ACCESS_GRANTED = True
                                    time.sleep(2)

                            # Incognito window and setup
                            incog = webdriver.Chrome(
                                options=incogOptions,
                            )
                            incog.get(PS_PARENT_URL)

                            # Enter in the login information
                            incog.find_element(By.ID, "fieldAccount").send_keys(
                                PARENT_EMAIL
                            )
                            incog.find_element(By.ID, "fieldPassword").send_keys(
                                DEFAULT_PASSWORD
                            )
                            incog.execute_script(
                                "arguments[0].click()",
                                incog.find_element(By.ID, "btn-enter-sign-in"),
                            )
                            time.sleep(2)

                            # Enter in the old and new passwords
                            incog.find_element(By.NAME, "currentCredential").send_keys(
                                DEFAULT_PASSWORD
                            )
                            incog.find_element(By.NAME, "newCredential").send_keys(
                                PARENT_PASSWORD
                            )
                            incog.find_element(By.NAME, "newCredential1").send_keys(
                                PARENT_PASSWORD
                            )
                            incog.execute_script(
                                "arguments[0].click()",
                                incog.find_element(By.ID, "btn-enter"),
                            )
                            time.sleep(5)
                            incog.close()

                            techs = []
                            # for each school, loop and add techs to cc
                            for school in schools_for_students:
                                for row in BUILDING_TECH:
                                    if row["school"] == school:
                                        techs.append(row["email"])
                            to = PARENT_EMAIL
                            email_items = login_email(PARENT_EMAIL, PARENT_PASSWORD)
                            send_email(techs, to, email_items[0], email_items[1])

                            append_sheet(
                                sheet_service,
                                SHEET_ID,
                                "Running Log",
                                "USER_ENTERED",
                                [
                                    [
                                        str(time.strftime("%m/%d/%Y - %I:%M %p")),
                                        STU_NAME,
                                        STU_NUM,
                                        PARENT_NAME,
                                        "Account created",
                                        PARENT_EMAIL,
                                        PARENT_PASSWORD,
                                    ]
                                ],
                            )

                            append_sheet(
                                sheet_service,
                                SHEET_ID,
                                "Created Accounts",
                                "USER_ENTERED",
                                [
                                    [
                                        str(time.strftime("%m/%d/%Y - %I:%M %p")),
                                        STU_NAME,
                                        STU_NUM,
                                        PARENT_NAME,
                                        PARENT_EMAIL,
                                        PARENT_PASSWORD,
                                    ]
                                ],
                            )

                            # Close the parent tab and switch back to the student
                            browser.close()
                            browser.switch_to.window(browser.window_handles[0])
                            time.sleep(2)
                else:
                    ACCESS_GRANTED = True

                    append_sheet(
                        sheet_service,
                        SHEET_ID,
                        "Running Log",
                        "USER_ENTERED",
                        [
                            [
                                str(time.strftime("%m/%d/%Y - %I:%M %p")),
                                STU_NAME,
                                STU_NUM,
                                PARENT_NAME,
                                "Access exists",
                            ]
                        ],
                    )
            else:
                append_sheet(
                    sheet_service,
                    SHEET_ID,
                    "Running Log",
                    "USER_ENTERED",
                    [
                        [
                            str(time.strftime("%m/%d/%Y - %I:%M %p")),
                            STU_NAME,
                            STU_NUM,
                            PARENT_NAME,
                            "No email",
                        ]
                    ],
                )

    if HAS_CUSTODY is False:
        append_sheet(
            sheet_service,
            SHEET_ID,
            "Running Log",
            "USER_ENTERED",
            [
                [
                    str(time.strftime("%m/%d/%Y - %I:%M %p")),
                    STU_NAME,
                    STU_NUM,
                    "",
                    "No custody set for student",
                ]
            ],
        )

        # Sends out an email to me if there is no email on custodial
        # Blocking sending the email for 323000040
        if int(STU_NUM) not in (323000040, 2637084):
            email_items = no_custody(STU_NAME, STU_NUM)
            send_email(
                "dplaskett@min201.org",
                "dplaskett@min201.org",
                email_items[0],
                email_items[1],
            )
            # no_custody(STU_NAME, STU_NUM)
            EMAIL_SENT = True

    if CUSTODY_EMAIL is False:
        # Sends out an email to me if there is no email on custodial
        # Blocking sending the email for 323000040
        if int(STU_NUM) not in (323000040, 2637084) and EMAIL_SENT is False:
            email_items = no_email(STU_NAME, STU_NUM)
            send_email(
                "dplaskett@min201.org",
                "dplaskett@min201.org",
                email_items[0],
                email_items[1],
            )
            # no_email(STU_NAME, STU_NUM)
            EMAIL_SENT = True

    if ACCESS_GRANTED is False:
        # Sends out an email to me if there is no email on custodial
        # Blocking sending the email for 323000040
        if int(STU_NUM) not in (323000040, 2637084) and EMAIL_SENT is False:
            email_items = no_access(STU_NAME, STU_NUM)
            send_email(
                "dplaskett@min201.org",
                "dplaskett@min201.org",
                email_items[0],
                email_items[1],
            )
            # no_access(STU_NAME, STU_NUM)

    # Switch to the next student
    browser.switch_to.window(browser.window_handles[0])
    browser.execute_script(
        "arguments[0].click()",
        browser.find_element(By.ID, "navNext"),
    )

# Closes browser
browser.close()
