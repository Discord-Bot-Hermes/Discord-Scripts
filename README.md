# Discord Bot and REST API for Educational Purposes

This project provides a versatile Discord bot designed to support tutors and instructors, particularly for an Introductory Programming course. It includes a range of commands for server management, student interaction, and feedback collection. Accompanying the bot is a REST API that allows for programmatic control and interaction with the bot's functionalities.

## Features

### Discord Bot
- **Basic Server Utilities**:
    - `ping`: Check bot latency.
    - `hello <member> [message]`: Greet a server member.
    - `clear [channel] [limit]`: Delete a specified number of messages from a channel.
- **Role Management**:
    - `give_member_role <member> <role>`: Assign a role to a member.
- **Attendance Tracking**:
    - `attendance <status> <group_id>`: Start or stop attendance for a tutor group. Students DM the bot to mark attendance.
- **Feedback & Surveys**:
    - `tutor_session_feedback <group_id> <channel> <duration>`: Initiate a feedback session for a tutor group.
    - `create_complex_survey <message> <main_topic> <channel> [questions_json] [button_types_json] [duration]`: Create multi-question surveys with various response types (Difficulty, Score). Can be configured via JSON or an interactive flow.
    - `create_simple_survey <message> <button_type> <main_topic> <channel> <duration>`: Create single-question surveys.
- **DM Interaction**: Handles DMs for attendance and survey participation.

### REST API
- **Bot Control**:
    - Start and stop the Discord bot.
- **Exposed Bot Functionality**:
    - Most of the Discord bot's slash commands are available via API endpoints.
- **Authentication**:
    - API key based authentication for all endpoints.
- **Logging & Auditing**:
    - Session-based logging for the bot.
    - Detailed API call auditing.

## Project Structure

```
.
├── REST/                     # Flask REST API application
│   ├── bot_manager/          # Blueprints for bot control, data, etc.
│   ├── api/                  # API specific logic (validation, etc.)
│   ├── utils/                # Utility functions for the API
│   ├── app.py                # Main Flask application setup
│   └── run.py                # Script to run the Flask server
├── bot/                      # Discord bot (py-cord)
│   ├── ui/                   # UI elements for bot interactions (views, buttons)
│   ├── discord_bot.py        # Main bot logic, event handling, command registration
│   ├── discord_bot_functions.py # Core functions used by the bot
│   ├── discord_bot_slash_commands.py # Definition of slash commands
│   └── discord_bot_events.py # Event handlers (on_ready, on_message etc.)
├── data/                     # Data storage (logs, audit, feedback - gitignored)
│   ├── logs/
│   ├── audit/
│   ├── attendance/
│   └── survey_feedback/
├── shared/                   # Shared data models or constants
├── utility/                  # General utility functions
├── .secrets.json             # Configuration file (gitignored)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    -   Copy the example configuration file (if one is provided, otherwise create `.secrets.json` manually).
        A typical `.secrets.json` structure would be:
        ```json
        {
         // Required values
          "bot": {
            "token": "YOUR_DISCORD_BOT_TOKEN",
            "dev_token": "YOUR_DISCORD_BOT_DEVELOPMENT_TOKEN",
            "development_mode": false,
          },
          "api_keys": {
            "YOUR_API_KEY_1": "user_1_description",
          },
          // Placeholders
          "groups": ["g1", "Group 2", "Thur01", "Thu02"], // Example groups for attendance
          "аccess_roles": [ ], // This will be automatically fetched from the server once bot is started
          "allowed_roles": [ ] // This you can fill in after the roles are fetched from the server. It gives permission for CLI execution of the commands
        }
        ```
    -   **Discord Bot Token**: Obtain this from the [Discord Developer Portal](https://discord.com/developers/applications).
    -   **API Keys**: Generate secure API keys for accessing the REST API. `025002` is often used as a default/dev key in this project.
    -   **Allowed Roles**: Configure Discord role IDs that are permitted to use restricted bot commands.
    -   **Guild ID**: Specify the Discord server ID where the bot will primarily operate.

## Usage

### Running the Discord Bot
The bot can be started via the REST API or directly if a startup script is implemented (e.g., `python bot/discord_bot.py`). Ensure the `.secrets.json` is configured with the correct bot token.

### Running the REST API
The Flask development server can be started by running:
```bash
python REST/run.py
```
This will typically start the server on `http://127.0.0.1:5000` if no port specified.

### API Endpoints

All API endpoints require an `api_key` query parameter for authentication (e.g., `?api_key=YOUR_API_KEY`).

**Bot Management:**
*   `POST /api/start-bot`: Starts the Discord bot.
*   `POST /api/stop-bot`: Stops the Discord bot.

**Data Retrieval (Bot must be running):**
*   `GET /api/data/guild-info`: Get basic info of the connected guild.
*   `GET /api/data/channels`: Get list of channels in the guild.
*   `GET /api/data/roles`: Get list of roles in the guild.
*   `GET /api/data/members`: Get list of members in the guild.
*   `GET /api/data/member-counts`: Get online, offline, and total member counts.
*   `GET /api/data/settings`: Retrieves the current bot settings.
*   `GET /api/data/attendance-data`: Get current attendance data.
*   `GET /api/data/survey-data`: Get current survey data.

**Bot Interaction (Bot must be running for commands to execute on Discord):**
*   `POST /api/bot/assign-role`: Assigns a role to a member.
    *   Body: `{"member_id": "MEMBER_ID", "role_id": "ROLE_ID", "guild_id": "GUILD_ID"}`
*   _Other bot commands like `clear`, `hello`, `attendance`, `create_survey` etc. are expected to be exposed via respective API endpoints. Refer to `REST/bot_manager/` blueprints for details. The existing README had GET requests for these, which might need to be updated to POST if they modify state, or if they trigger complex bot actions._

**Example API Call (using cURL):**
```bash
curl -X POST "http://127.0.0.1:5000/api/start-bot?api_key=025002"
curl -X GET "http://127.0.0.1:5000/api/data/guild-info?api_key=025002"
curl -X POST "http://127.0.0.1:5000/api/bot/assign-role?api_key=025002" -H "Content-Type: application/json" -d '{"member_id": "123456789012345678", "role_id": "987654321098765432", "guild_id": "YOUR_GUILD_ID"}'
```

## Logging and Auditing

-   **Bot Session Logs**: Stored in `data/logs/`. Each bot session creates a new timestamped log file.
-   **API Audit Logs**: Stored in `data/audit/`. Daily JSON files logging all API requests (timestamp, endpoint, IP, redacted API key, parameters).

## Dependencies
Key dependencies include:
-   `py-cord`: For the Discord bot.
-   `Flask`: For the REST API.
-   `python-dotenv`: For managing environment variables (though `.secrets.json` is used here).
-   (See `requirements.txt` for the full list)

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
