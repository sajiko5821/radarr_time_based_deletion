import requests
import json
from datetime import datetime, timedelta
import re
import os

# Radarr configuration
RADARR_API_KEY = "YOUR_API_KEY"
RADARR_URL = "http://localhost:7879"
DAYS_TO_CHECK = 14

def get_movie_title(path):
    """Extracts movie title from path."""
    try:
        filename = os.path.basename(path)
        match = re.search(r"^(.+?)\s*\((\d{4})\)", filename)
        return match.group(1) if match else filename.split(".")[0]
    except (AttributeError, IndexError):
        return "Unknown Title"

def get_movie_age(date_str):
    """Calculates movie age in days."""
    try:
        return (datetime.now() - datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")).days
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

def get_radarr_history():
    """Retrieves Radarr history with pagination."""
    headers = {"X-Api-Key": RADARR_API_KEY}
    page = 1
    page_size = 1000
    all_records = []

    while True:
        params = {"page": page, "pageSize": page_size}
        try:
            response = requests.get(f"{RADARR_URL}/api/v3/history", headers=headers, params=params)
            response.raise_for_status()
            records = response.json().get("records", [])
            if not records:
                break
            all_records.extend(records)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Radarr API Error: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Response: {getattr(response, 'text', 'N/A')}")
            break

    movies = {record["data"]["importedPath"]: {
        "title": get_movie_title(record["data"]["importedPath"]),
        "added_date": datetime.fromisoformat(record["date"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S"),
        "movie_id": record.get("movieId")
    } for record in all_records if record.get("data") and record["data"].get("importedPath")}
    return list(movies.values())

def set_movie_monitored_status(movie_id, monitored_status):
    """Sets monitored status of a movie."""
    try:
        # 1. Get the full movie data first
        get_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
        headers = {"X-Api-Key": RADARR_API_KEY}
        get_response = requests.get(get_url, headers=headers)
        get_response.raise_for_status()
        movie_data = get_response.json()

        # 2. Modify the monitored status in the retrieved data
        movie_data["monitored"] = monitored_status

        # 3. Send the updated movie data with PUT
        put_url = f"{RADARR_URL}/api/v3/movie/{movie_id}"
        put_headers = {"X-Api-Key": RADARR_API_KEY, "Content-Type": "application/json"}
        put_response = requests.put(put_url, headers=put_headers, json=movie_data)
        put_response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        print(f"Radarr API Error (set_movie_monitored_status): {e}")
        if 'get_response' in locals() and hasattr(get_response, 'text'):
            try:
                error_json = get_response.json()
                print(f"Radarr API Error Details (GET): {json.dumps(error_json, indent=4)}")
            except json.JSONDecodeError:
                print(f"Response Text (GET - could not decode JSON): {get_response.text}")
        if 'put_response' in locals() and hasattr(put_response, 'text'):
            try:
                error_json = put_response.json()
                print(f"Radarr API Error Details (PUT): {json.dumps(error_json, indent=4)}")
            except json.JSONDecodeError:
                print(f"Response Text (PUT - could not decode JSON): {put_response.text}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def delete_movie_files_by_movie_id(radarr_url, radarr_api_key, movie_id):
    """Deletes movie files by movie ID."""
    try:
        movie_url = f"{radarr_url}/api/v3/movie/{movie_id}"
        headers = {"X-Api-Key": radarr_api_key}
        movie_response = requests.get(movie_url, headers=headers)
        movie_response.raise_for_status()
        movie_data = movie_response.json()

        moviefile_id = movie_data.get("movieFile", {}).get("id")

        if moviefile_id:
            delete_url = f"{radarr_url}/api/v3/moviefile/{moviefile_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            delete_response.raise_for_status()
            print(f"Movie file (ID: {moviefile_id}) for movie (ID: {movie_id}) deleted successfully.")
            return True
        else:
            print(f"No movie file found for movie ID: {movie_id}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Radarr API Error (delete_movie_files_by_movie_id): {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def check_and_update_movie(movie):
    """Checks movie age, updates monitored status, and deletes files if needed."""
    age = get_movie_age(movie["added_date"])
    movie_id = movie.get("movie_id")

    if age is not None:
        if age >= DAYS_TO_CHECK:
            print(f"ID: {movie_id}, Movie '{movie['title']}' is older than {DAYS_TO_CHECK} days ({age} days). Setting monitored to False and deleting file.")
            if set_movie_monitored_status(movie_id, False):
                if not delete_movie_files_by_movie_id(RADARR_URL, RADARR_API_KEY, movie_id):
                    print(f"Failed to delete movie file for ID: {movie_id}")
            else:
                print(f"Failed to set monitored status for ID: {movie_id}")
        else:
            print(f"ID: {movie_id}, Movie '{movie['title']}' is not yet {DAYS_TO_CHECK} days old ({age} days). Keeping monitored status.")
    else:
        print(f"ID: {movie_id}, Title: {movie['title']}, Added Date: {movie['added_date']}, Age: Calculation failed (Invalid date format)")

if __name__ == "__main__":
    movie_list = get_radarr_history()
    if movie_list:
        print(f"Checking for movies older than {DAYS_TO_CHECK} days:")
        for movie in movie_list:
            check_and_update_movie(movie)
    else:
        print("Could not retrieve movie history.")
