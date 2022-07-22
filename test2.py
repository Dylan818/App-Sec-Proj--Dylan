import re

def validate_username(user_input):
    pattern = r"\d|[a-z]|[A-Z][!@#$]"
    if re.search(pattern, user_input):
        x = re.findall(pattern, user_input)
        print(x)
        if len(x) == len(user_input):
            print("h1")
            return True
        else:
            return False

    else:
        print("Not found")
        return False

validate_username("123'")
validate_username("hello123")
