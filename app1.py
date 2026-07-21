import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
print("hello")

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

user_goal = input("What we are going to make today? ")
print(f"Goal locked in: {user_goal}\n")

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
def run_chat():
    print('You: (type exit to quit)')
    history = []

    total_con_tokens = 0

    scores_list = []  
    while True:

        turn_number = int(len(history) / 2) + 1
        print(f"[Turn {turn_number}] ", end="")

        user_input = input('>> ')

        if user_input.lower() == 'exit':
            
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

