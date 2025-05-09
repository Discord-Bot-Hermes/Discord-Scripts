# DiscordBot

A basic bot created for the tutors and instructors of the Introductory Programming course.

Related paper: https://arxiv.org/abs/2407.19266

## Discord Bot and REST API

This repository contains a Discord bot for educational purposes and a REST API to interact with it.

### Discord Bot Commands

The Discord bot supports the following slash commands:

1. `/ping` - A simple ping command to check if the bot is responsive.
2. `/hello <member> <message>` - Greet a member with a custom message.
3. `/clear <channel> <number of messages>` - Delete a specified number of messages from a channel.
4. `/give-member-role <member> <role>` - Assign a specific role to a member.
5. `/attendance <status> <group_id>` - Start or stop attendance tracking for a specific group.
6. `/tutor-session-feedback <group_id>` - Collect feedback for a tutor session from a specific group.
7. `/create-complex-survey <message> <main_topic> <channel>` - Create a multi-question survey.
8. `/create-simple-survey <message> <button_type> <main_topic> <channel>` - Create a single-question survey.

### REST API Endpoints

The REST API provides endpoints to interact with the Discord bot. All endpoints require an API key as a query parameter.

#### Authentication

All API requests require an API key passed as a query parameter: `?api_key=YOUR_API_KEY`

For development purposes, use the "Master-M" API key: `?api_key=025002`

#### Available Endpoints

1. **Start Bot**
   - URL: `/api/start-bot`
   - Method: `GET`
   - Required Parameters: `api_key`
   - Description: Starts the Discord bot if it's not already running.

2. **Stop Bot**
   - URL: `/api/stop-bot`
   - Method: `GET`
   - Required Parameters: `api_key`
   - Description: Stops the Discord bot if it's running.

3. **Ping**
   - URL: `/api/ping`
   - Method: `GET`
   - Required Parameters: `api_key`
   - Description: Simple endpoint to check if the bot is responsive.

4. **Hello**
   - URL: `/api/hello`
   - Method: `GET`
   - Required Parameters: `api_key`, `member`
   - Optional Parameters: `message` (default: "Hello there!")
   - Description: Greet a member with a custom message.

5. **Clear**
   - URL: `/api/clear`
   - Method: `GET`
   - Required Parameters: `api_key`, `channel`
   - Optional Parameters: `limit` (default: 10, must be between 1 and 100)
   - Description: Delete a specified number of messages from a channel.

6. **Give Member Role**
   - URL: `/api/give-member-role`
   - Method: `GET`
   - Required Parameters: `api_key`, `member`, `role`
   - Description: Assign a specific role to a member.

7. **Attendance**
   - URL: `/api/attendance`
   - Method: `GET`
   - Required Parameters: `api_key`, `status` (must be "start" or "stop"), `group_id`
   - Description: Start or stop attendance tracking for a specific group.

8. **Tutor Session Feedback**
   - URL: `/api/tutor-session-feedback`
   - Method: `GET`
   - Required Parameters: `api_key`, `group_id`
   - Description: Collect feedback for a tutor session from a specific group.

9. **Create Complex Survey**
   - URL: `/api/create-complex-survey`
   - Method: `GET`
   - Required Parameters: `api_key`, `message`, `main_topic`, `channel`
   - Description: Create a multi-question survey.

10. **Create Simple Survey**
    - URL: `/api/create-simple-survey`
    - Method: `GET`
    - Required Parameters: `api_key`, `message`, `button_type` (must be "Difficulty" or "Score"), `main_topic`, `channel`
    - Description: Create a single-question survey.

### Error Handling

All API endpoints use a consistent error response structure:

```json
{
  "status": "error",
  "error": "Error type",
  "message": "Detailed error message"
}
```

Common error types:
- `Bad request` (400): Missing or invalid parameters
- `Unauthorized` (401): Invalid or missing API key
- `Not found` (404): Endpoint not found
- `Internal server error` (500): Server-side error

### Logging and Auditing

The system implements comprehensive logging and auditing:

1. **Session Logs**
   - Each bot session has its own log file in the `data/logs` directory
   - Log files are named with the timestamp when the session started (e.g., `2025-03-05_14-30.log`)

2. **API Audit Logs**
   - All API calls are logged in daily audit files in the `data/audit` directory
   - Audit logs include timestamp, endpoint, API key, parameters, and client IP
   - API keys are redacted in the logs for security

### Data Storage

The system stores data in the `data` directory, with subdirectories for different data types:
- `logs`: Session logs
- `audit`: API audit logs
- `exercise_feedback`: Feedback data from exercises
- `tutor_session_feedback`: Feedback data from tutor sessions

A future version will migrate data storage to a proper database system.

### Examples

1. Start the bot:
   ```
   GET /api/start-bot?api_key=025002
   ```

2. Send a greeting to a member:
   ```
   GET /api/hello?api_key=025002&member=username&message=Welcome%20aboard!
   ```

3. Clear 50 messages from a channel:
   ```
   GET /api/clear?api_key=025002&channel=general&limit=50
   ```

4. Stop the bot:
   ```
   GET /api/stop-bot?api_key=025002
   ```
