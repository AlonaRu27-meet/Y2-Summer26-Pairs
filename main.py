import app1
import app2
while True:
    pick = input ("Which agent do you want to use? (Smart Chef/NutriGuide)")
    if pick.lower() == 'smart chef' or pick == '1':
        recipe_to_analyze = app1.run_chat()
        
        if recipe_to_analyze:
            print("\n--- Sending recipe to NutriGuide automatically... ---")
            nutrition_analysis = app2.run_agent(recipe_to_analyze)
            print("\nNutriGuide Analysis:")
            print(nutrition_analysis)

    elif pick.lower() == 'nutriguide' or pick == '2':
        app2.start_agent()
    else:
        print ("Invalid input, please try again")