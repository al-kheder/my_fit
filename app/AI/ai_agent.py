import logging
from pyexpat.errors import messages
from typing import Dict, Any
import json
import requests
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
logger = logging.getLogger(__name__)

def extract_fitness_goal(response_str: str) -> dict:
    """
    Extract structured fitness goal data from the AI response string.

    Args:
        response_str (str): The raw response string from the AI (expected to be a JSON object)

    Returns:
        dict: Parsed data with keys for goal_name, workout_type, etc.
    """
    try:
        # Parse the string response to a dictionary
        data = json.loads(response_str)

        # Validate required fields
        required_keys = [
            "goal_name", "workout_type", "calories_to_burn",
            "duration_days", "daily_target_calories", "daily_time_minutes"
        ]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing key in response: {key}")

        return data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON response: {response_str}")
        raise ValueError("Response is not valid JSON")
    except Exception as e:
        logger.error(f"Error extracting fitness goal: {str(e)}")
        raise



def create_custom_agent(instruction_prompt: str,goal_description: str):
    API_URL = os.environ.get("RAPIDAPI_URL")
    if API_URL is None:
        raise ValueError("RAPIDAPI_URL not found in environment variables")
    API_KEY = os.environ.get("RAPIDAPI_KEY")
    if API_KEY is None:
        raise ValueError("RAPIDAPI_KEY not found in environment variables")

    payload = {
        "messages": [
            {
                "role": "user",
                "content":f"{instruction_prompt} \n{goal_description} "
            }
        ],
        "model": "gpt-4o-mini"
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Extract message content based on the API response structure
        if 'choices' in data and len(data['choices']) > 0:
            print(data['choices'][0]['message']['content'])
            return data['choices'][0]['message']['content']
        elif 'messages' in data and len(data['messages']) > 0:
            return data['messages'][0]['content']
        else:
            logger.error(f"Unexpected API response format: {data}")
            raise ValueError("Unable to extract content from API response")

    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to communicate with AI service")
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        raise



create_custom_agent(instruction_prompt=f"""
You are a fitness goal planner assistant. 
Based on the user's goal description below, return a JSON object with a detailed breakdown of their workout target. 
Use this format:
  "goal_name": "string",
  "workout_type": "string",
  "calories_to_burn": integer,
  "duration_days": integer,
  "daily_target_calories": integer,
  "daily_time_minutes": integer,

Use these rules:
- 1 kg of fat = 7700 kcal
- Estimate calorie burn rate based on the activity (e.g., Running ≈ 10 kcal/min, Walking ≈ 4 kcal/min, Cycling ≈ 8 kcal/min)
- Assume 5 workout days per week unless specified otherwise
- Only return the JSON object, no explanation
   """,goal_description="lose 5 kg in 3 months"
)
