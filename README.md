# Radarr-Aged-Cleaner
A Python script designed to automatically clean up your Radarr library by unmonitoring and deleting movie files that have been imported and held for a specified number of days. This is useful for temporary libraries, "watch and delete" setups, or managing disk space.

## Features
- Aged-Based Cleanup: Targets movies older than a configurable number of days (DAYS_TO_CHECK).
- Full Automation: Retrieves history, unmonitors the movie in Radarr, and deletes the associated movie file.
- Pagination Support: Uses Radarr's history API pagination to handle large libraries.
- Robust Handling: Checks for and handles potential API request errors and JSON decoding issues gracefully.

## Prerequisites
- Python 3.x
- Radarr instance with API enabled.
- The requests library. You can install it using pip:
  ```
  pip install requests
  ```

## Installation and Configuration
1. Clone the Repo
Save this repository to your local drive

2. Configure Your Radarr Instance

⚠️ Security Warning: To prevent exposing your API key, you should set these values using environment variables rather than hardcoding them in the script.

The script is set up to read from these variables, but you can also edit the top of the file if you prefer.

| Variable       | Description                                                         | Example Value                    |
| -------------- | ------------------------------------------------------------------- | -------------------------------- |
| RADARR_API_KEY | Your secret Radarr API key.                                         | a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 |
| RADARR_URL     | The full URL to your Radarr instance.                               | http://localhost:7879            |
| DAYS_TO_CHECK  | The number of days after import to keep a file before it's deleted. | 14                               |

A safer way to run the script is to set these variables in your terminal before execution:
```
export RADARR_API_KEY="YOUR_KEY_HERE"
export RADARR_URL="http://radarr:7879"
export DAYS_TO_CHECK=7

python3 radarr_cleaner.py
```
**Example Output:**
The script will provide status updates as it processes your library:
```
Checking for movies older than 14 days:
ID: 105, Movie 'The Matrix' is not yet 14 days old (5 days). Keeping monitored status.
ID: 250, Movie 'Blade Runner 2049' is older than 14 days (18 days). Setting monitored to False and deleting file.
Movie file (ID: 1234) for movie (ID: 250) deleted successfully.
ID: 312, Movie 'Inception' is older than 14 days (20 days). Setting monitored to False and deleting file.
Movie file (ID: 5678) for movie (ID: 312) deleted successfully.
```
