import os
clear = lambda: os.system('cls')

def credit_counter():
    user_input = ''    
    credits = 0
    while user_input.lower() != 'q':
        
        user_input = input('Enter Credits:')
        
        try:
            if user_input.lower() != 'q':
                credits += int(user_input)
            
        except:
            print('Try Again.')
    
    print(f'\nTotal Credits: {credits}')

    if credits < 120:
        print(f'You are short {120 - credits} credits.')
    elif credits == 120:
        pass
    else:
        print(f'You are {credits - 120} credits over.')

while True:
    print()
    credit_counter()
    
    closing_prompt = input('')
    closing_prompt = input('')
    clear()
    print()

