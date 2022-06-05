import time
import pyautogui
import application
import random
'''
def Automatic():
    time.sleep(50)

    text = open('user.txt')
    for lines in text:
        pyautogui.typewrite(lines)
        pyautogui.press('enter')



db = application.db.connect("localhost", "root", "", "GEEK")

# get cursor object
cursor = db.cursor()

# execute your query
cursor.execute("SELECT * FROM geeksdemo")

# fetch all the matching rows
result = cursor.fetchall()

# loop through the rows
for row in result:
    print(row)
    print("\n")
'''
character = "0123456789abcdefghijklmnopqrstuvwxyz"
character_list = list(character)
List = []

guess = ""
for names in application.db.execute("""SELECT * FROM users"""):
    List.append([names["username"],names["password"]])
print(List)

Crackuser = List[4][0]
Crackpass = List[4][1]
while guess != Crackpass.lower():
    guess = ""
    for y in range(len(Crackpass)):
        guess += random.choice(character_list)
    guess="".join(guess)
print("The password is " + guess)

while guess != Crackuser.lower():
    guess = ""
    for y in range(len(Crackuser)):
        guess += random.choice(character_list)
    guess="".join(guess)
print("The username is " + guess)

print(Crackpass)
print(Crackuser)
