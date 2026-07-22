import os
import base64
import mimetypes
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_MESSAGE = """
You are NutriGuide, a Nutrition Coach for a Smart Kitchen Assistant.

Your job is to analyze a recipe, meal description, or food image that the user
provides. Give approximate nutrition information and realistic healthier
alternatives.

You provide:
- Estimated calories per serving
- Estimated protein, carbohydrates, and fat
- A brief nutrition summary
- Healthier substitutions or improvements
- A reminder that all nutrition values are estimates, not medical advice

For photos:
- Identify only food you can reasonably see.
- Do not claim to know exact ingredients, portion sizes, calories, or cooking
  methods from an image alone.
- Explain when more information is needed for a better estimate.

You do not diagnose health conditions, prescribe diets, or create complete
recipes from scratch.

Every response must use exactly this format:

[Summary]: One sentence repeating what the user asked.
[Response]: Nutrition estimate, healthier alternatives, and a short disclaimer.
[Next Step]: One concrete action the user can take.
"""


def get_age():
    """Asks for a valid age."""

    while True:
        try:
            age = int(input("How old are you? "))

            if 2 <= age <= 120:
                return age

            print("Please enter an age between 2 and 120.")

        except ValueError:
            print("Please enter a whole number.")


def get_profile():
    """Creates a temporary profile for this session only."""

    name = input("What is your name? ").strip()

    if not name:
        name = "Chef"

    age = get_age()

    return {
        "name": name,
        "age": age
    }


def get_system_message(profile):
    """Adds the temporary profile to the agent instructions."""

    return f"""
{SYSTEM_MESSAGE}

The user's name is {profile["name"]}.
The user is {profile["age"]} years old.

Give general, age-appropriate nutrition guidance. Do not claim to calculate
exact personal nutrition needs from age alone. Explain that exact needs also
depend on activity level, body size, health needs, and personal goals.
"""


def run_agent(user_input, profile, history=None):
    """Analyzes meals or recipes written by the user."""

    if history is None:
        history = []

    history.append({
        "role": "user",
        "content": user_input
    })

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0,
        system=get_system_message(profile),
        messages=history
    )

    reply = response.content[0].text

    history.append({
        "role": "assistant",
        "content": reply
    })

    return reply


def analyze_food_image(image_path, profile, user_note=""):
    """Analyzes a food image saved on the computer."""

    image_file = Path(image_path)

    if not image_file.is_file():
        return (
            "[Summary]: You asked to analyze a food photo.\n"
            "[Response]: I could not find that image file.\n"
            "[Next Step]: Check the image filename and try again."
        )

    media_type, _ = mimetypes.guess_type(image_file.name)

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif"
    }

    if media_type not in allowed_types:
        return (
            "[Summary]: You asked to analyze a food photo.\n"
            "[Response]: Please use a JPG, PNG, WEBP, or GIF image.\n"
            "[Next Step]: Choose a supported image file."
        )

    image_data = base64.b64encode(
        image_file.read_bytes()
    ).decode("utf-8")

    image_prompt = f"""
Analyze this food image.

The user is {profile["name"]}, age {profile["age"]}.

Additional information from the user:
{user_note if user_note else "No extra information was given."}

Identify only food that is clearly visible. Estimate calories, protein,
carbohydrates, and fat per serving only when reasonable. Explain that a photo
cannot reveal exact portions, ingredients, oils, sauces, or cooking methods.

Every response must use exactly this format:

[Summary]: One sentence repeating what the user asked.
[Response]: Visible foods, estimated nutrition, healthier alternatives, and a short disclaimer.
[Next Step]: One concrete action the user can take.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0,
        system=get_system_message(profile),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": image_prompt
                    }
                ]
            }
        ]
    )

    return response.content[0].text


def analyze_recent_meals(profile):
    """Asks about recent meals and estimates a healthy-eating streak."""

    recent_meals = input(
        "\nTell me what you ate over the last few days.\n"
        "Example: Monday: chicken, rice, and salad. "
        "Tuesday: pizza and soda. Wednesday: eggs, toast, and fruit.\n\n"
        "Your meals: "
    ).strip()

    if not recent_meals:
        return (
            "[Summary]: You asked to check your recent healthy-eating streak.\n"
            "[Response]: I need a description of your meals before I can estimate a streak.\n"
            "[Next Step]: List what you ate on at least one recent day."
        )

    streak_prompt = f"""
The user is {profile["name"]}, age {profile["age"]}.

The user described recent meals as:

{recent_meals}

Analyze this as a general healthy-eating consistency challenge.

Rules:
- Review each day the user clearly described.
- Mark each day as: reasonably balanced, needs improvement, or not enough detail.
- Count a day toward an estimated healthy-eating streak only if the description
  reasonably includes a balance of foods, such as protein, carbohydrates,
  fruits, vegetables, or healthy fats.
- Do not invent meals, nutrition values, or dates.
- Clearly say this is only an estimate based on the user's description.

Use these levels:
- 0 days: Getting Started
- 1–2 days: Fresh Starter
- 3–6 days: Nutrition Builder
- 7–13 days: Healthy Habit Hero
- 14+ days: Kitchen Champion

Every response must use exactly this format:

[Summary]: One sentence repeating what the user asked.
[Response]: Show the estimated streak, level, feedback for each described day,
what they did well, and one thing to improve.
[Next Step]: One concrete action the user can take tomorrow.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=650,
        temperature=0,
        system=get_system_message(profile),
        messages=[
            {
                "role": "user",
                "content": streak_prompt
            }
        ]
    )

    return response.content[0].text


def start_nutritionist_chat():
    print("Welcome to NutriGuide — Nutrition Coach")

    profile = get_profile()

    print(f"\nWelcome, {profile['name']}!")
    print("Type a meal or recipe for nutrition analysis.")
    print("Type 'streak' to describe recent meals and get an estimated streak.")
    print("Type 'photo' to analyze a food image.")
    print("Type 'reset' to clear chat history.")
    print("Type 'exit' to quit.")

    history = []
    last_reply = None

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            if last_reply is not None:
                switch = input("\nDo you want to get a healthier alternative from the recipe maker? (yes/no): ")
                if switch.lower() == 'yes':
                    return last_reply
            break

        if user_input.lower() == "reset":
            history = []
            print("Chat history cleared.")
            continue

        if user_input.lower() == "streak":
            print("\nNutriGuide:")
            print(analyze_recent_meals(profile))
            continue

        if user_input.lower() == "photo":
            image_path = input("Enter the image file path: ").strip()
            user_note = input("Optional: describe the meal or serving size: ").strip()
            print("\nNutriGuide:")
            print(analyze_food_image(image_path, profile, user_note))
            continue

        if not user_input:
            print("Please type a meal, recipe, 'streak', or 'photo'.")
            continue

        print("\nNutriGuide:")
        last_reply = run_agent(user_input, profile, history)
        print(last_reply)

if __name__ == "__main__":
    start_nutritionist_chat()
