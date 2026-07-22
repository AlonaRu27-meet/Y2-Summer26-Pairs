import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

try:
    with open("feedback.txt", "r") as changes_file:
        saved_changes = changes_file.read()
except FileNotFoundError:
    saved_changes = ""



system_message = """
    You are Remi, a smart chef, that experts in culinary and meal planning. your aim is to create a delicious, step-by-step recepies, based on the ingrediants the user already has at home, while trictly adhering to dietary restrictions and prefereneces (alergies, diets, health, etc.)
    Your job is to To guide the user step-by ptep how to make the meal you craeted.

    Always:
    - Always be nice and pleasant.
    - Suggest complete recipes using the user's available ingredients.
    - Adapt recipes perfectly to requested dietary constraints (e.g., Gluten-Free, Kosher, Vegan, Keto, etc).
    - Provide clear ingredients lists and step-by-step cooking instructions.

    Never:
    - DO NOT suggest recipes that require core ingredients the user explicitly said they do not have.
    - DO NOT provide medical or clinical nutritional advice (leave nutritional analysis to the second Agent).
    - DO NOT engage in general chitchat unrelated to food, cooking, or recipes.
    - Never judge the user prefereneces.

    Response format:
    You must ALWAYS respond using this exact format.
    - [Summary]: One sentence repeating what the user asked for.
    - [Response]: The detailed recipe, including name, ingredients list, and instructions.
    - [Next Step]: One concrete action the user can take (e.g., asking to pass this recipe to the Nutritionist Agent for analysis, or asking for a replacement ingredient).
    """
system_message = system_message + f"\nHere are past improvements you must remember:\n{saved_changes}"


def run_chat():
    user_goal = input("What we are going to make today? ")
    print(f"Goal locked in: {user_goal}\n")
    print('You: (type exit to quit)')
    history = []
    favorits = {}
    total_con_tokens = 0
    reply = ""
    while True:

        turn_number = int(len(history) / 2) + 1
        print(f"[Turn {turn_number}] ", end="")

        user_input = input('>> ')

        if user_input.startswith('/get '):
            recipe_name = user_input.replace('/get ', '')
            if recipe_name in favorits:
                print(favorits[recipe_name])
            else:
                print(f"Sorry, you don't have a recipe named '{recipe_name}' in your favorites.")
            continue

        if user_input.lower() == 'exit':
            while True:
                user_rating = input("\nHow would you rate this meal? (1-5): ").strip()
                if user_rating in ['1', '2', '3', '4', '5']:
                    print(f"Thank you for your feedback! You rated us: {user_rating}/5")
                    if int(user_rating) < 4:
                        changes = input("Can you tell us what was wrong? ")
                        with open("feedback.txt", "a") as changes_file:
                            changes_file.write(changes + "\n")
                        print("Thank you! we will try to improve next time")

                    break
                else:
                    print("Invalid input. Please enter a number between 1 and 5.")
            
            if 'reply' in locals() or 'reply' in globals():
                comment = input("\nWould you like to add this final recipe to 'favorites'? (yes/no): ").strip().lower()
                if comment == "yes":
                    name = input("How would you like to call this recipe? ").strip()
                    favorits[name] = reply

                    with open("favorites.txt", "a") as fav_file:
                        fav_file.write(f"=== Recipe Name: {name} ===\n")
                        fav_file.write(reply)
                        fav_file.write("\n\n---------------------------------------\n\n")
                    print(f"Recipe '{name}' saved to favorites successfully!")

            if 'reply' in locals() or 'reply' in globals():
                switch = input("\nDo you want to analyze that meal with the Nutritionist? (yes/no): ").strip().lower()
                if switch == 'yes':
                    return reply 

            break



        if user_input.lower() == 'reset':
            history = []
            print("Conversation history cleared. Starting fresh!")
            continue

        if user_input.lower() == '/summary':
            print("\n--- Remi is reviewing your chat history... ---")
            
            summary_response = client.messages.create(
                model='claude-3-haiku-20240307',
                max_tokens=300,
                temperature=0.9,
                system="You are a helpful tutor. Summarize the user's progress based on the history.",
                messages=history + [{'role': 'user', 'content': 'Please give a quick, structured summary of what we discussed so far and what I learned.'}]
            )
            
            reply_text = summary_response.content[0].text
            print(f"\n[Summary]: {reply_text}\n")
            continue

        history.append({'role': 'user', 'content': user_input})
        #print('History:', history)

        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=3000, #number of chars
            temperature=1.0, #creativity level
            system=system_message,
            messages=history
        )

        reply = response.content[0].text
        print(f'Claude: {reply}')
        history.append({'role': 'assistant', 'content': reply})

        
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens

        total_tokens = in_tokens + out_tokens

        print(f"[Tokens used — In: {in_tokens} | Out: {out_tokens} | Total: {total_tokens}]")

        total_con_tokens += total_tokens
        print (f"[Running Total: {total_con_tokens} tokens]")

        input_cost = (in_tokens / 1000000) * 0.25
        output_cost = (out_tokens / 1000000) * 1.25
        cost_in_cents = (input_cost + output_cost) * 100
        print(f"[Estimated Cost: {cost_in_cents:.5f}¢]")

if __name__ == "__main__":
    run_chat()

