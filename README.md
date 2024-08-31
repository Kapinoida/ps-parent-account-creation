# ps-parent-account-creation

## Introduction

This projects used a bunch of different tools to loop through and create PowerSchool parent accounts for students where one isn't tied to the student. Once it is created, it will email the parent and relevant techs with the login information and notate the change to a Google Sheet.

The main script is `ps_parent.py` with supporting scripts of `constants.py`, `create_service.py`, `emails.py`, `gmail_functions.py`, and `sheet_functions.py`.

## Requirements

- Keyring - a module that lets you set up variables for getting passwords or other sensitive information without directly adding it to the script. [min201 Keyring Documentation](https://github.com/Minooka-CCSD-201/min201-documentation/blob/main/keyring.md)
- Google Cloud Credentials - Need to have a project ready and the credentials JSON downloaded. [min201 Google Cloud Console](https://github.com/Minooka-CCSD-201/min201-documentation/blob/main/google-cloud-console.md)
- Selenium - Opens a web browser and runs the account creation. [min201 Selenium Documentation](https://github.com/Minooka-CCSD-201/min201-documentation/blob/main/selenium.md)

## Explanation

1. Logs into PowerSchool Admin (should use 201apps account along with Keyring)
2. Finds the stored query for students with no PS web access
3. Loops through the list of students:
   1. Checks for parent data access to be enabled and sets it up if not.
   2. Loops through contacts and finds custodial with email address.
      1. If so:
         1. Runs through account creation process.
         2. Notates and emails parent with login info
      2. If not
         1. Writes to sheet
         2. (Currently emails Dave, could change to make a pshelp ticket.)

## ps_parent.py

This is where all the magic happens. Basically, the bulk of the script is the Selenium directions to drive the web browser. The script should be able to handle auto-updating of the Chrome Driver (you used to have to update it manually if Chrome on the device updated).

The inner works can probably be figured out, but there is a lot of different methods used to navigate around. Webpages are weird, and stacking PowerSchool on top of that just makes things even stranger. Also, this script can be volatile as webpages can change over time, so something might not be named the same down the road.

## Helper Scripts

### constants.py

This just hold a few constants we would use across the project. Helps with finding them later as they aren't buried in some script.

### create_service.py

This just creates a Google API service, depending on parameters you feed it. This is used across multiple projects, but we are not using this script for Gmail, more on that later.

### emails.py

These are emails we can feed in variables to. Really just use it to clean up the main script and save a bunch of space.

### gmail_functions.py

This helper module handles all things Gmail. We are using a service account in Google with domain level delegation to send out an email using pshelp@min201.org. We are connecting to the Gmail service with that service account, then sending all the emails using the pshelp@min201.org email.

### sheet_functions.py

Helper module used in other projects. Added an append to sheet for this project and that's all it's used for.

## Implementation

To be determined. In the past, Dave ran it locally on his machine a few times a week, but the recent enhancements were intended to automate the process.
