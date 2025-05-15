import logging
from pyexpat.errors import messages
from typing import Dict, Any
import re
import json
import requests
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
logger = logging.getLogger(__name__)




logger = logging.getLogger(__name__)

AI_EXAMPLE_RESPONSE :{
  "goal_name": "lose 5 kg",
  "workout_type": "mixed",
  "calories_to_burn": 38500,
  "duration_days": 50,
  "daily_target_calories": 770,
  "daily_time_minutes": 77
}

def extract_fitness_goal(raw_response: str) -> dict:
    """
    Extract a structured fitness goal from the AI response.

    Args:
        raw_response: Raw string response from the AI

    Returns:
        Dictionary containing the structured goal data

    Raises:
        ValueError: If the response cannot be parsed as JSON
    """
    logger.debug(f"Attempting to extract JSON from raw response: {raw_response[:100]}...")

    # First try direct JSON parsing
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed, attempting to extract JSON from text")

    # Try to extract JSON objects from the text response - common pattern with AI responses
    json_pattern = r'(\{[\s\S]*?\})'
    json_matches = re.findall(json_pattern, raw_response)

    for potential_json in json_matches:
        try:
            goal_data = json.loads(potential_json)

            # Validate required fields
            required_fields = [
                "goal_name", "workout_type", "calories_to_burn",
                "duration_days", "daily_target_calories", "daily_time_minutes"
            ]

            if all(field in goal_data for field in required_fields):
                logger.debug(f"Successfully extracted JSON: {goal_data}")
                return goal_data
        except json.JSONDecodeError:
            continue

    # If we get here, we couldn't extract valid JSON
    logger.error(f"Failed to extract valid JSON from response: {raw_response}")
    raise ValueError("Response is not valid JSON")


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
#TODO
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



