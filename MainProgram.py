"""
Moothy 14
"""

import argon2, secrets
import os, time, urllib
import sqlite3
import SendingEmails 
ph = argon2.PasswordHasher(3, 524288, 100, type=argon2.Type.I)
connection = sqlite3.connect("accounts.db")
cursor = connection.cursor()

#~~~~~~~~~~~~~~~~~Functions~~~~~~~~~~~~~~~~~~~~~~
def PrintTitle(ScreenTitle):
    #Requires the title of the screen you are on to display
    os.system("cls")
    print("\t"* 2 + """Tea and Biscuits:
            A Place to Make Friends""")
    
    print("\n"+ " " * int((47 - len(ScreenTitle))/2) + f"{ScreenTitle}\n")

class LogInScreen:
    def __init__(self):
        self.valid = False
        self.index = None
        self.computingID = None
        self.password = None

    def LogIn(self):
        MoreThanOnce = False
        while self.valid != "Valid":

            PrintTitle("Log in")
            print ("""(Type "cancel" in the Computing ID to return to home screen)""")
            
            if MoreThanOnce == True:
                print("*Your Computing ID or Password is incorrect")
            
            self.computingID = input("SFU Computing ID: ").lower()

            if self.computingID == "cancel":
                break

            self.password = input("Password: ")


            
            MoreThanOnce = True
            self.index = cursor.execute("SELECT counter FROM accounts WHERE id = ?", (self.computingID,)).fetchone()

            if self.index is not None:
                sStoredPassword = cursor.execute("SELECT password FROM accounts WHERE counter = ?", (self.index)).fetchone()[0]
                try:
                    ph.verify(sStoredPassword, self.password)
                    #Rehashes password on Successful login
                    cursor.execute("""UPDATE accounts
                                   SET password = ? WHERE counter = ?""",
                                   (ph.hash(self.password), self.index[0])) 
                    connection.commit()
                    self.valid = "Valid"
                
                except:
                    pass

            else:
                #If there is no account found, it defaults to result in it being incorrect
                #but still runs the verify so that you can't tell if the account exists or not by the speed it runs the "verify"
                #Otherwise, it would just instantly tell you it's incorrect if there was no account registered
                sStoredPassword = "$argon2i$v=19$m=524288,t=3,p=100$Fc3qDcq9TDE35tpCXmqgNw$9k7KurifCOCyuIZcBNI0e6mSADAbjouA1kkjEX6Ex50"
                
                try:
                    ph.verify(sStoredPassword, "Not the correct password")

                except:
                    pass

class SignUpScreen:
    def __init__(self):
        self.valid = False
        self.computingID = None
        self.password = None
        self.SentTime = None

    def SignTitle(self, message = ""):
        PrintTitle("Sign Up")
        print(message)

    def GenerateCode(self):
        VerificationCode = ""
        for number in range(6):
            VerificationCode += str(secrets.randbelow(10))
        return VerificationCode

    def SignUp(self):
        MoreThanOnce = False

        #-----------Sign in screen-----------
        while self.valid == False:
            self.SignTitle("""(Type "cancel" in the email to return to home screen)""")
            print("(You may also reset you password from here)")

            self.computingID = input("SFU Computing ID: ").lower()

            if self.computingID == "cancel":
                break

            try:
                SecretCode = self.GenerateCode()
                SendingEmails.send_mail("teaandbiscuitsdonotreply@gmail.com", self.computingID + "@sfu.ca",
                "Tea and Biscuits Verification Code",
                "Your code is " + SecretCode + "<br />" + "This code expires in 2 minutes")
                self.SentTime = time.time()
                self.valid = True
                MoreThanOnce = False   

            except urllib.error.HTTPError:
                print("520 Method Failure")   
                print("An account is unable to be created at this time. Please contact support to let them know of the issue.")  
                input("Press enter to return to the home screen")
                self.valid = "Invalid"
            except:
                print("500 Internal Server Error")
                print("An unknown error has occured. Please contact support to let them know of the issue.")
                input("Press enter to return to the home screen")
                self.valid = "Invalid"

    #------------verification screen-------------
        while self.valid == True:
            self.SignTitle()

            #Prints if you've seen this screen more than once 
            if MoreThanOnce == True:
                print("*That is not correct")

            MoreThanOnce = True

            
            if input("Enter the verification code you received: ") == SecretCode:

                if (time.time() - self.SentTime) > 120:
                    print("Sorry, this code has expired. We have sent you new code")
                    time.sleep(4)
                    SecretCode = self.GenerateCode()
                    self.SentTime = time.time()
                    MoreThanOnce = False
                    SendingEmails.send_mail("teaandbiscuitsdonotreply@gmail.com", self.computingID + "@sfu.ca",
                    "Tea and Biscuits Verification Code",
                    "Your code is " + SecretCode + "<br />" + "This code expires in 2 minutes") 
                
                else:
                    self.valid = "Valid"
                    MoreThanOnce = False
        
        while self.valid == "Valid":
            self.SignTitle()
            if MoreThanOnce == True:
                print("*The passwords you entered do not match")
            
            self.password = input("Create a new password: ")
            if self.password == input("Retype password: "):
                cursor.execute("""INSERT OR REPLACE INTO accounts(id, password)
                VALUES (?, ?)""", (self.computingID, ph.hash(self.password)))
                connection.commit()
                open("messages/" + str(self.computingID) + ".txt", "a")
                print("Account Successfully Created!")
                time.sleep(3)
                break
                
            MoreThanOnce = True
    
#~~~~~~~~~~~~~~~~~~~~Code~~~~~~~~~~~~~~~~~~~~
LogIn = LogInScreen()
exit = False

while exit == False:
    while LogIn.valid == False:
        PrintTitle("Welcome!")
        print("""     To create an account, type 'Sign Up'
    Already have an account? Type 'Log in'
             Type "Exit" to exit""")
        SignOrLog = input("What would you like to do? ").lower()

        if SignOrLog in {"sign up", "signup", "sing up", "singup"}:
            SignUp = SignUpScreen()
            SignUp.SignUp()

        elif SignOrLog in {"log in", "login"}:
            LogIn.LogIn()
            if LogIn.valid == "Valid":
                PrintTitle("Successfully Signed in!")

        elif SignOrLog == "exit":
            exit = True
            break

        else:
            print("I'm not sure I understand you")
            time.sleep (2)

    while LogIn.valid == "Valid":
        PrintTitle("Welcome!")
        print("""    To read your new messages, type "Read"
        To send a message, type "Send
          To log out, type "Log out\"""")
        SendOrReceive = input("What would you like to do? ").lower()

        if SendOrReceive == "read":
            UserTextFile = open("messages/" + str(LogIn.computingID) + ".txt", "r")
            messages = UserTextFile.readlines()
            messagesReversed = messages[::-1]

            if messages == []:
                print("You currently have no messages")
            
            else:
                print("".join(messages))
            
            input("Press enter to return ")

                        #Reduces the file to the last 50 messages
            if len(messages) > 50:
                UserTextFile = open("messages/" + str(LogIn.com) + ".txt", "w")

                #Runs a for-loop on the last 50 messages in the list
                for line in messages[len(messages)-50:]:
                    UserTextFile.write(line)
                UserTextFile.close()

        elif SendOrReceive == "send":
            Sent = False
            while Sent == False:
                PrintTitle("Send a message")
                print("Who would you like to send a message to?")
                print("(Type their computing id)")
                print("Press enter to cancel")
                SendName = input("Name: ").lower()
                if SendName == "":
                    break            
                SendName += ".txt"
                

                if os.path.isfile("messages/" + SendName) == False:
                    print("Sorry, that account does not exist")
                    time.sleep(2)

                else:
                    SendToTxtFile = open("messages/" + SendName, "a")
                    SendMessage = input("Message: ")
                    SendToTxtFile.write("From " + LogIn.computingID + """: \"""" + SendMessage + """\" Sent on """ + time.strftime("%Y %B %d at %I:%M %p %Z\n"))
                    SendToTxtFile.close()
                    print("Sent Successfully!")
                    Sent = True
                    time.sleep(2)
        
        elif SendOrReceive in {"log out","logout"}:
            LogIn.valid = False

        else:
            print("I'm not sure I understand you")
            time.sleep (2)