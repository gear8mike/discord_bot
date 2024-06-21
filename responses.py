from random import choice, randint

def get_response(user_input):
    # raise NotImplementedError('Code is missing')
    lowered = user_input.lower()
    if lowered == '':
        return "You are silent ....zzzzz"
    elif 'hello' in lowered:
        return 'Hello Buddy!'
    elif 'roll dice' in lowered:
        return f"You rolled dice: {randint(1, 6)}"
    
    else:
        return choice("Roll dice", "Say hello", "Good bye!")