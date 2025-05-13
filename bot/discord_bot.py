"""
Discord Bot
~~~~~~~~

A basic bot created for the tutors and instructors of the Introductory Programming course.

:copyright: (c) 2023-present Ivan Parmacli
:license: MIT, see LICENSE for more details.
"""

import asyncio
import discord
import sys
import logging
from pathlib import Path

# Add the project root to Python path to make imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings manager
from REST import settings_manager
from discord.ext import commands

# Get the logger configured in app.py
logger = logging.getLogger('discord_bot')

##################################
#              INIT              #
##################################

# Get settings from the central manager
SETTINGS = settings_manager.SETTINGS
if not SETTINGS:
    raise RuntimeError("Settings could not be loaded. Cannot start the bot.")

bot = commands.Bot(
    intents=discord.Intents.all(),
    status=discord.Status.streaming,
    activity=discord.Streaming(
        name="Coding with Jimbo", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ),
)

###########################################
#              BOT FUNCTIONS              #
###########################################


def start(token_key=None) -> None:
    """
    Startup function.

    Args:
        token_key: Optional key to specify which token to use.
               If None, uses token based on development_mode setting.
    """
    # Update global keyword so it can be accessed.
    global bot
    global _guilds, _channels, _members, _roles, _member_counts

    # Clear any existing data
    _guilds = {}
    _channels = {}
    _members = {}
    _roles = {}
    _member_counts = {"online": 0, "offline": 0, "total": 0}

    # Determine which token to use based on development mode
    if token_key is None:
        # Simply use the appropriate token based on development mode
        # without checking if it's None
        if SETTINGS["bot"]["development_mode"]:
            token = SETTINGS["bot"]["dev_token"]
        else:
            token = SETTINGS["bot"]["token"]
    else:
        # If a specific token key is provided, use that token
        token = SETTINGS["bot"][token_key]

    # Create a new event loop and set it as the current loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create a new bot instance if needed
    global bot
    recreated = False
    if hasattr(bot, 'is_closed') and bot.is_closed():
        bot = commands.Bot(
            intents=discord.Intents.all(),
            status=discord.Status.streaming,
            activity=discord.Streaming(
                name="Coding with Jimbo", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ),
        )
        recreated = True
        # Update the bot reference in the top-level bot package so other modules see the new client
        pkg = sys.modules.get('bot')
        if pkg is not None:
            setattr(pkg, 'bot', bot)

    # Reload dependent modules only if the bot instance was recreated.
    if recreated:
        import importlib, sys as _sys
        for mod in ['bot.discord_bot_functions', 'bot.discord_bot_slash_commands', 'bot.discord_bot_events']:
            if mod in _sys.modules:
                importlib.reload(_sys.modules[mod])

    # Run the bot with the selected token
    bot.run(token)



def _verify_author_roles(user: discord.User | discord.Member) -> bool:
    """
    Ensure that the user has the required role to use the command.

    Args:
        user :class:`User` | :class:`Member`: The user whose roles are to be verified.
    """
    # Get access roles from settings
    access_roles = SETTINGS["allowed_roles"]
    
    # Extract role IDs from the access_roles list
    allowed_role_ids = []
    for role_data in access_roles:
        try:
            # Each role_data is a dictionary with complete role information
            role_id = int(role_data["id"])
            allowed_role_ids.append(role_id)
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Warning: Invalid role data in settings: {e}")
    
    # Print all role IDs that the user has for debugging
    # print(f"User roles: {[(role.name, role.id) for role in user.roles]}")
    for role in user.roles:
        if role.id in allowed_role_ids:
            return True
    return False

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    try:
        # Load role data from settings
        if 'roles' in SETTINGS:
            for role_data in SETTINGS['roles']:
                try:
                    role_id = int(role_data['id'])
                    role_name = role_data['name']
                    bot_data.ROLES[role_id] = role_name
                except (ValueError, KeyError) as e:
                    logger.warning(f"Warning: Invalid role data in settings: {e}")
    except Exception as e:
        logger.error(f"Error loading role data: {e}")

    logger.info(f"Bot is ready! Logged in as {bot.user.name}")