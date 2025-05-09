"""
Function Utils
~~~~~~~~

Contains various functions required for the different elements of the bot.

:copyright: (c) 2023-present Ivan Parmacli
:license: MIT, see LICENSE for more details.
"""

import discord
import csv
import os
import logging
from datetime import datetime
from pathlib import Path

from bot import bot_data
from shared import SurveyEntry

# Get the logger configured in app.py
logger = logging.getLogger('discord_bot')

# Add live bot accessor
import REST.utils.bot_context as bc

def _bot():
    return bc.get_live_bot()

################################################################
#               TUTOR SESSION FEEDBACK FUNCTIONS               #
################################################################

DEFAULT_CASE_WARNING = "Incorrect group id."


async def add_student_to_attendance_list(
    message: discord.Message, group: list, status: bool, id: str
) -> None:
    """
    Adds a student to the specified group, only works if the student is in the INFUN server.

    Args:
        message :class:`discord.Message`: The message sent by the user.
        group :class:`list`: List of participants of the tutor group.
        status :class:`bool`: Indicates whether attendance verification has started.
        id :class:`str`: The ID of the tutor group.
    """
    print(f"Adding student to attendance. Status: {status}, ID: {id}, Message content: {message.content}")
    
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        print(f"Processing DM from {message.author.name}")
        current_guild = _bot().guilds[0]
        member = current_guild.get_member(message.author.id)
        
        if member:
            # Format: "DisplayName (username)"
            student_info = f"{member.display_name} ({message.author.name})"
            
            if status and message.content.lower() == id.lower() and student_info not in group:
                print(f"Adding {student_info} to {id} attendance list")
                group.append(student_info)
                try:
                    await message.channel.send("You are added to the attendance list.")
                except Exception as e:
                    print(f"Error sending confirmation: {e}")
            else:
                print(f"Not adding student. Status: {status}, Content match: {message.content.lower() == id.lower()}, Already in list: {student_info in group}")
        else:
            print(f"Could not find member in guild: {message.author.name} ({message.author.id})")
    else:
        # Regular channel message
        current_guild = _bot().guilds[0]
        member = current_guild.get_member(message.author.id)
        
        if member:
            # Format: "DisplayName (username)"
            student_info = f"{member.display_name} ({message.author.name})"
            
            if status and message.content.lower() == id.lower() and student_info not in group:
                group.append(student_info)
                await message.channel.send("You are added to the attendance list.")
        else:
            print(f"Could not find member in guild: {message.author.name} ({message.author.id})")


def save_attendance_to_csv(group_id: str, attendance_list: list) -> None:
    """
    Save the attendance list to a CSV file.
    
    Args:
        group_id :class:`str`: The ID of the tutor group.
        attendance_list :class:`list`: List of students who attended.
    """
    # Create attendance directory if it doesn't exist
    attendance_dir = Path('../data/attendance')
    attendance_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate filename with current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{group_id}_{current_time}.csv"
    file_path = attendance_dir / filename
    
    # Write attendance list to CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Attendance'])  # Header
        for student in attendance_list:
            writer.writerow([student])


def attendance_cleanup(group_id: str) -> None:
    """
    Reset the specified group status and clear the students group list.

    Args:
        group_id :class:`str`: The ID of the tutor group.
    """
    # Convert to lowercase for case-insensitive comparison
    group_id_lower = group_id.lower()
    
    # Find the original case version of the group ID
    original_group_id = None
    for group in bot_data.SETTINGS["groups"]:
        if group.lower() == group_id_lower:
            original_group_id = group
            break
    
    if original_group_id:
        # Use the original case for variable access
        var_name = f"group_{original_group_id}"
        
        # Get the group list using getattr
        group_list = getattr(bot_data, var_name)
        
        # Save attendance list before clearing
        save_attendance_to_csv(original_group_id, group_list)
        
        # Clear the list
        group_list.clear()
        
        # Reset the status
        setattr(bot_data, f"{var_name}_status", False)
    else:
        raise RuntimeWarning(DEFAULT_CASE_WARNING)


def prepare_group_list_for_embed(id: str) -> str:
    """
    Adds a new line character for each student name, so that it will be displayed correctly in the embed.

    Args:
        id :class:`str`: The ID of the tutor group.

    Raises:
        :class:`RuntimeWarning`: Occurs when the tutor's group ID does not exist.

    Returns:
        :class:`str`: A list of students.
    """
    # Convert to lowercase for case-insensitive comparison
    id_lower = id.lower()
    
    # Find the original case version of the group ID
    original_id = None
    for group in bot_data.SETTINGS["groups"]:
        if group.lower() == id_lower:
            original_id = group
            break
    
    text = ""
    if original_id:
        var_name = f"group_{original_id}"
        group_list = getattr(bot_data, var_name)
        
        for entry in group_list:
            text += entry + "\n"
        return text
    else:
        raise RuntimeWarning(DEFAULT_CASE_WARNING)


def update_dm_accept_status(id: str) -> None:
    """
    Set the specified group status to True, so the messages from the students will be accepted by the bot.

    Args:
        id :class:`str`: The ID of the tutor group.

    Raises:
        :class:`RuntimeWarning`: Occurs when the tutor's group ID does not exist.
    """
    # Convert to lowercase for case-insensitive comparison
    id_lower = id.lower()
    
    # Find the original case version of the group ID
    original_id = None
    for group in bot_data.SETTINGS["groups"]:
        if group.lower() == id_lower:
            original_id = group
            break
    
    if original_id:
        var_name = f"group_{original_id}"
        setattr(bot_data, f"{var_name}_status", True)
    else:
        raise RuntimeWarning(DEFAULT_CASE_WARNING)


####################################################################
#               Saving the SurveyEntry to a CSV File               #
####################################################################


def save_survey_entry_to_csv(path: str, entry: SurveyEntry) -> None:
    """
    Adds the student's answers to the csv file.

    Args:
        path :class:`str`: The path to the file.
        entry :class:`SurveryEntry`: The survey entry that contains the student's answers.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Check if file exists to determine if we need to write a header
    file_exists = os.path.isfile(path) and os.path.getsize(path) > 0
    
    # Prepare header from entry keys
    header = list(entry.selected_options.keys())
    header.insert(0, "Name")
    
    # Write the data to a file.
    with open(file=path, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=header,
        )
        
        # Write header only if file is new or empty
        if not file_exists:
            writer.writeheader()

        # Create a row from the dictionary.
        row = {"Name": entry.student_name}
        for key in entry.selected_options.keys():
            row.update({key: entry.selected_options.get(key)})

        # Check if this student already submitted an entry
        if verify_entry_not_in_csv(path=path, entry=entry.student_name):
            writer.writerow(rowdict=row)


def verify_entry_not_in_csv(path: str, entry: str) -> bool:
    """
    Verify whether an entry already exists in the csv file.

    Args:
        path :class:`str`: The path to the file.
        entry :class:`str`: String to check.

    Returns:
        :class:`bool`: Whether an entry already exists in the csv file.
    """

    with open(file=path, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            if entry in row:
                return False
        return True
