
import application
import random

character = "0123456789abcdefghijklmnopqrstuvwxyz"
character_list = list(character)
List = {}
username = []
guess = ""
for names in application.db.execute("""SELECT * FROM users"""):
    List[names["username"]] = names["password"]
    username.append(names["username"])
print(List)

Crackuser = username[4]
Crackpass = List.get(Crackuser)
print(Crackuser)
print(Crackpass)

while guess != Crackuser.lower():
    guess = ""
    for y in range(len(Crackuser)):
        guess += random.choice(character_list)
    guess="".join(guess)
print("The username is " + guess)
while guess != Crackpass.lower():
    guess = ""
    for y in range(len(Crackpass)):
        guess += random.choice(character_list)
    guess="".join(guess)
print("The password is " + guess)





