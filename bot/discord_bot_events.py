import discord
import sys
import asyncio
import time
from pathlib import Path

import utility
from bot import bot_data, bot
from bot.discord_bot_functions import get_roles

# Add the project root to Python path to make imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))
from REST import settings_manager


########################################
#              BOT EVENTS              #
########################################


@bot.event
async def on_ready() -> None:
    # Views creation is deprecated, don't use this code.
    # Create views for the background process.
    # quiz_view_for_thread = get_view("quiz", bot)
    # lecture_view_for_thread = get_view("lecture", bot)
    # # Uncomment when the lecture_loop function is ready or is being tested.
    # background_thread = Thread(
    #     target=_lectures_loop,
    #     args=(
    #         quiz_view_for_thread,
    #         lecture_view_for_thread,
    #     ),
    #     daemon=True,
    # )
    # background_thread.start()

    # Sync commands with Discord. Uncomment when done and pre-demo
    await update_roles_in_settings()

    print("Syncing commands...")
    try:
        # To sync to all guilds (global commands - can take up to an hour to register)
        await bot.sync_commands()

        # To sync to specific guilds for immediate testing (faster than global commands)
        # If your bot is only in one guild, sync commands to just that guild for faster updates
        print("Synced commands...", bot.all_commands)
        if len(bot.guilds) > 0:
            print(f"Syncing commands to guild: {bot.guilds[0].name}")
            await bot.sync_commands(guild_ids=[bot.guilds[0].id])
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    print(f'-----\nLogged in as {bot.user.name}.\nWith the bot id="{bot.user.id}"\n-----')


async def update_roles_in_settings():
    """
    Fetch roles from the Discord server and update settings.json
    This is run after the bot is fully initialized
    """
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f"Fetching roles and updating settings.json (attempt {retry_count + 1}/{max_retries})...")
            
            # Make sure the bot is connected to at least one guild
            if not bot.guilds:
                print("Bot not connected to any guilds yet, waiting...")
                await asyncio.sleep(2)
                retry_count += 1
                continue
                
            # Use the get_roles function to fetch role data
            roles_data = get_roles()
            
            if not roles_data:
                print("No role data returned, waiting...")
                await asyncio.sleep(2)
                retry_count += 1
                continue
                
            guild_id = str(bot.guilds[0].id)
            if guild_id not in roles_data:
                print(f"No roles found for guild {guild_id}, waiting...")
                await asyncio.sleep(2)
                retry_count += 1
                continue
                
            guild_roles = roles_data[guild_id]
            
            # Get current settings
            settings = settings_manager.get_settings()
            
            # Store the complete role data in access_roles
            settings["access_roles"] = guild_roles
            settings_manager.update_settings(settings)
            
            print(f"Successfully updated settings.json with {len(guild_roles)} roles from server")
            return
            
        except Exception as e:
            print(f"Error updating roles in settings.json: {e}")
            await asyncio.sleep(2)
            retry_count += 1
    
    print("Failed to update roles in settings.json after multiple attempts")


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    This event is triggered when a message is sent in a channel.

    Args:
        message :class:`discord.Message`: The message that was sent.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Process commands first
    await bot.process_commands(message)

    # Get the message content
    message_content = message.content.lower()

    # Check for attendance messages
    # Only check for attendance if the message is in a valid group format
    if len(message_content) <= 10:  # Reasonable limit for group names
        # Dynamically check all groups from settings
        for group_id in bot_data.SETTINGS["groups"]:
            # Check if this message matches the group ID
            if message_content.lower() == group_id.lower():
                # Get the group list and status from bot_data using original case
                group_list = getattr(bot_data, f"group_{group_id}")
                group_status = getattr(bot_data, f"group_{group_id}_status")
                
                # For debugging purposes
                print(f"Message received: {message_content}, Group: {group_id}")
                print(f"Group Status: {group_status}, Channel: {message.channel}")
                
                # Check this group
                await utility.add_student_to_attendance_list(
                    message=message,
                    group=group_list,
                    status=group_status,
                    id=group_id,
                )