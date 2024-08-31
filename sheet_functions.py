"""
This module contains functions for interacting with Google Sheets.
"""

import time
from googleapiclient.errors import HttpError


def add_header(values, columns):
    """
    Adds a header to the values list.

    Parameters:
        values (list): The values list to add the header to.
        columns (list): The list of column names.

    Returns:
        list: The values list with the header added.
    """
    columns.append("Updated " + time.strftime("%m-%d-%Y %I:%M %p"))
    return [columns] + values


def create_range(values, sheet_name):
    """
    Creates a range string for a Google Sheets API batch update.

    Args:
        values (list): A list of lists representing the values in the sheet.
        sheet_name (str): The name of the sheet.

    Returns:
        str: A string representing the range of cells to be updated in the format
        sheet_name!A1:column_widthrow_count.
    """

    column_width = len(values[0])
    return sheet_name + "!A1:" + str(column_width) + str(len(values))


def get_ss_name(service, spreadsheet_id, count=0):
    """
    Retrieves the title of a Google Sheets spreadsheet using the provided service and
    spreadsheet ID.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Sheets
        API service object.
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.

    Returns:
        str: The title of the spreadsheet if successful, or an error message if an
        exception occurred.
    """
    try:
        if count >= 3:
            print("Hit max retries for get_ss_name, returning None")
            return None
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return result.get("properties").get("title")
    except HttpError as error:
        print(f"An error occurred: {error}")
        get_ss_name(service, spreadsheet_id, count + 1)


def update_values(
    service, spreadsheet_id, range_name, value_input_option, _values, count=0
):
    """
    Updates the values in a specified range of a Google Sheets spreadsheet.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Sheets
        API service object.
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.
        range_name (str): The range of cells to update.
        value_input_option (str): How the input data should be interpreted.
        _values (List[List[Any]]): The new values to be written into the specified range.

    Returns:
        dict: A dictionary containing the result of the update operation if successful,
        or an error message if an exception occurred.
    """
    if count >= 3:
        print("Hit max retries for update_values, returning None")
        return None
    try:
        body = {
            "values": _values,
        }
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updatedRows')-1} rows updated.")
        return result
    except HttpError as error:
        print(f"An error occurred in update_values: {error}")
        update_values(
            service, spreadsheet_id, range_name, value_input_option, _values, count + 1
        )


def read_sheet(spreadsheet_id, range_name, sheets_service, count=0):
    """
    Reads the values from a specific range of a Google Sheets spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.
        range_name (str): The range of cells to read.
        sheets_service (googleapiclient.discovery.Resource): An authenticated Google
        Sheets API service object.

    Returns:
        list: A list of lists containing the values in the specified range. If an error
        occurs, it returns the error message.
    """
    if count >= 3:
        print("Hit max retries for read_sheet, returning None")
        return None
    try:
        sheet = sheets_service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        )
        values = result.get("values", [])
        return values
    except HttpError as error:
        print(f"An error occurred in read_sheet: {error}")
        read_sheet(spreadsheet_id, range_name, sheets_service, count + 1)


def get_sheets(service, spreadsheet_id, count=0):
    """
    Retrieves the sheets of a Google Sheets spreadsheet using the provided service and
    spreadsheet ID.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Sheets API
        service object.
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.

    Returns:
        dict: A dictionary containing the sheets of the spreadsheet if successful, or an
        error message if an exception occurred.
    """
    if count >= 3:
        print("Hit max retries for get_sheets, returning None")
        return None
    try:
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return result
    except HttpError as error:
        print(f"An error occurred in get_sheets: {error}")
        get_sheets(service, spreadsheet_id, count + 1)


def copy_spreadsheet(
    source_spreadsheet_id, new_spreadsheet_title, service, dest_shared_drive_id, count=0
):
    """Copies an existing spreadsheet to a new one with the specified title.

    Args:
        source_spreadsheet_id: The ID of the spreadsheet to copy.
        new_spreadsheet_title: The title for the new copy.
        service: The authenticated Google Drive API service object.

    Returns:
        The ID of the newly created spreadsheet if successful, None otherwise.
    """
    if count >= 3:
        print("Hit max retries for copy_spreadsheet, returning None")
        return None
    try:
        copied_file = {"name": new_spreadsheet_title}

        # Add the destination shared drive ID (if provided)
        if dest_shared_drive_id:
            copied_file["parents"] = [dest_shared_drive_id]

        # Copy the spreadsheet
        new_sheet = (
            service.files()
            .copy(
                fileId=source_spreadsheet_id,
                body=copied_file,
                supportsAllDrives=True,  # Important for shared drive support
            )
            .execute()
        )
        return new_sheet["id"]

    except HttpError as error:
        print(f"An error occurred in copy_spreadsheet: {error}")
        copy_spreadsheet(
            source_spreadsheet_id,
            new_spreadsheet_title,
            service,
            dest_shared_drive_id,
            count + 1,
        )


def clear_sheet(service, spreadsheet_id, sheet_name, count=0):
    """
    Clears the cells of a specified sheet in a Google Sheets spreadsheet.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Sheets API
        service object.
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.
        sheet_name (str): The name of the sheet within the spreadsheet.

    Returns:
        dict: A dictionary containing the result of the clear operation if successful, or
        an error message if an exception occurred.
    """
    if count >= 3:
        print("Hit max retries for clear_sheet, returning None")
        return None
    try:
        result = (
            service.spreadsheets()
            .values()
            .clear(spreadsheetId=spreadsheet_id, range=sheet_name)
            .execute()
        )
        print(f"{sheet_name} cells cleared.")
        return result
    except HttpError as error:
        print(f"An error occurred in clear_sheet: {error}")
        clear_sheet(service, spreadsheet_id, sheet_name, count + 1)


def ensure_sheet_exists(spreadsheet_id, sheet_name, service, count=0):
    """Checks if a sheet exists and creates it if not found.

    Args:
        spreadsheet_id: The ID of the Google Sheets spreadsheet.
        sheet_name: The name of the sheet to check/create.
        service: The authenticated Google Sheets API service object.

    Returns:
        The sheet ID if the sheet exists or was created, None otherwise.
    """
    if count >= 3:
        print("Hit max retries for ensure_sheet_exists, returning None")
        return None
    sheets = get_sheets(service, spreadsheet_id).get("sheets", [])
    existing_sheet_names = [sheet["properties"]["title"] for sheet in sheets]

    if sheet_name in existing_sheet_names:
        sheet_id = next(
            (
                sheet["properties"]["sheetId"]
                for sheet in sheets
                if sheet["properties"]["title"] == sheet_name
            ),
            None,
        )
        return sheet_id

    try:
        request_body = {
            "requests": [{"addSheet": {"properties": {"title": sheet_name}}}]
        }
        response = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )

        sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
        return sheet_id

    except HttpError as error:
        print(f"An error occurred in ensure_sheet_exists: {error}")
        ensure_sheet_exists(spreadsheet_id, sheet_name, service, count + 1)


def update_sheet(service, sheet_id, sheet_name, values, columns, has_header):
    """
    Updates the specified Google Sheets with the provided values and columns.

    Args:
        sheet_id (str): The ID of the Google Sheet to update.
        sheet_name (str): The name of the sheet within the Google Sheet.
        values (list): The values to update in the sheet.
        columns (list): The columns corresponding to the values.

    Returns:
        None
    """
    ensure_sheet_exists(sheet_id, sheet_name, service)
    clear_sheet(service, sheet_id, sheet_name)
    if not has_header:
        tvalues = add_header(values, columns)
    else:
        tvalues = values
    update_values(
        service, sheet_id, create_range(values, sheet_name), "USER_ENTERED", tvalues
    )

def append_sheet(
    service, spreadsheet_id, range_name, value_input_option, _values, count=0
):
    """
    Appends values to a specific range of a Google Sheets spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet.
        range_name (str): The range of cells to append to.
        value_input_option (str): The input format of the values.
        _values (list): The values to append.
        sheets_service (googleapiclient.discovery.Resource): An authenticated Google
        Sheets API service object.
    """
    if count >= 3:
        print("Hit max retries for append_sheet, returning None")
        return None
    try:
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body={"values": _values},
            )
            .execute()
        )
        return result
    except HttpError as error:
        print(f"An error occurred in append_sheet: {error}")
        append_sheet(
            service, spreadsheet_id, range_name, value_input_option, _values, count + 1
        )