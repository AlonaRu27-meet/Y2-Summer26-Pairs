import app1
import app2
while True:
    pick = input ("Which agent do you want to use? (1/2)")
    if pick == '1':
        app1.run_chat()
    elif pick == '2':
        app2.run_agent()
    else:
        print ("Invalid input, please try again")