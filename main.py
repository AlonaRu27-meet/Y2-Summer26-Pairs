import app1
import app2

while True:
    pick = input("Which agent do you want to use? (Smart Chef/NutriGuide or type exit) ").strip().lower()
    
    if pick == 'smart chef' or pick == '1':
        recipe_to_analyze = app1.run_chat()
        
        if recipe_to_analyze:
            profile = app2.get_profile()
            print("\n--- Sending recipe to NutriGuide automatically... ---")
            nutrition_analysis = app2.run_agent(recipe_to_analyze, profile)
            print("\nNutriGuide Analysis:")
            print(nutrition_analysis)

    elif pick == 'nutriguide' or pick == '2':
        app2.start_nutritionist_chat()

        
    else:
        print("Invalid input, please try again.")
