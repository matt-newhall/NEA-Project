#!/usr/bin/env python3

# Import Modules, Functions and Classes
# -----------------------------------------------------------------------------------------------------------------------------------------------------

import pymysql, getpass, sys, os
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from cursorCreate import *
from treeFunctionsClasses import *
from passSaltAndHash import *
from mergeSort import *



# Start Flask Application
# -----------------------------------------------------------------------------------------------------------------------------------------------------

print("Welcome to the Bracket Creation System.")

intSelection = 0
while intSelection != 9:
    intSelection = int(input("\nPlease type 1 to Start the Flask Web Server\n          > 2 to Create a new Account\n          > 5 to Reset the Database\n         or 9 to Quit:\n > "))

    if intSelection == 1:
        break

    elif intSelection == 2:
        database, cursor = cursorCreate()

        strUsername = input("Username: ")
        sql = "SELECT UserID FROM User_mst WHERE Username=\"" + strUsername + "\";"
        cursor.execute(sql)
        if cursor.fetchall() != ():
            print("Warning: account found with same name. Account was not created.")
            continue

        strEmail = input("Email: ")

        strAccountType = input("Account Type (A, C, R or U): ")
        if strAccountType != "A" and strAccountType != "C" and strAccountType != "R" and strAccountType != "U":
            print("Invalid account type entered - please try again")
            continue

        strPassword = getpass.getpass("Password: ")
        strPassCheck = getpass.getpass("Confirm Password: ")
        if strPassword != strPassCheck:
            print("Passwords do not match - please start again")
            continue
        elif len(strPassword) < 8 or strPassword == strPassword.lower():
            print("Password validation failed. Please make the password at least 8 characters in length and contain at least one capital letter.")
            continue

        strSaltedPass, strRandSalt = passSalt(strPassword)
        strPassHash = passHash(strSaltedPass)

        sql = "INSERT INTO User_mst (Username, PasswordHash, PasswordSalt, AccountType, EmailAddress) VALUES (\"" + strUsername + "\",\"" + strPassHash + "\",\"" + strRandSalt + "\",\"" + strAccountType + "\",\"" + strEmail + "\");"
        cursor.execute(sql)
        database.commit()

        cursor.close()
        database.close()

        print("Account created succesfully.")

    elif intSelection == 5:
        database = pymysql.connect(host="localhost", user="root", passwd="..n1tT.fa.gm", autocommit=True)
        cursor = database.cursor(pymysql.cursors.DictCursor)

        objDatabaseSQL = open("/var/www/html/resetDatabaseSQL.txt", "r")
        for strLine in objDatabaseSQL.readlines():
            try:
                cursor.execute(strLine)
                database.commit()
            except:
                if strLine == objDatabaseSQL.readlines()[0]:
                    print("Warning: No existing database found")
                else:
                    print("Error thrown on line " + objDatabaseSQL.readlines().index(strLine) + 1)
                continue

        objDatabaseSQL.close()

        cursor.close()
        database.close()

        print("Reset successful. We now recommend creating an administrator account.")

    elif intSelection == 9:
        continue

    else:
        print("Selection invalid - please enter an option")



# HTTP Rerouting
# -----------------------------------------------------------------------------------------------------------------------------------------------------

if intSelection != 9:
    app = Flask(__name__)



    # Login/Logout
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    
    @app.route('/', methods = ['GET', 'POST'])
    @app.route('/home', methods = ['GET', 'POST'])
    def home():
        if session.get('userLoggedIn'):
            return render_template("account.html")
        else:
            return render_template("login.html")

            
    @app.route('/loginUser', methods = ['GET', 'POST'])
    def loginUser():
        if request.method == "POST":
            database, cursor = cursorCreate()

            strUsername = request.form['txtUsername']
            strPassword = request.form['txtPassword']

            sql = "SELECT UserID FROM User_mst WHERE Username=\"" + strUsername + "\";"
            cursor.execute(sql)

            if cursor.fetchall() == ():
                print("Warning: no account found with the same name. Returning client to home page.")
                flash("No account in this name found")
                cursor.close()
                database.close()
                return render_template("login.html")

            sql = "SELECT PasswordHash, PasswordSalt FROM User_mst WHERE Username=\"" + strUsername + "\";"
            cursor.execute(sql)
            dictPassword = cursor.fetchone()

            strPassSalt = dictPassword["PasswordSalt"]
            strSaltedPass = strPassword + strPassSalt

            strPassHash = passHash(strSaltedPass)
            strRealHash = dictPassword["PasswordHash"]

            sql = "SELECT AccountType FROM User_mst WHERE Username=\"" + strUsername + "\";"
            cursor.execute(sql)
            strAccountType = cursor.fetchone()["AccountType"]
            
            cursor.close()
            database.close()
            
            if strRealHash == strPassHash:
                print("Valid login for " + strUsername + ".")
                session['userLoggedIn'] = True
                session['strUsername'] = strUsername
                session['strAccountType'] = strAccountType
            else:
                print("Invalid password for " + strUsername + ".")
                flash('Wrong Password')
            return redirect(url_for('home'))
        return render_template("login.html")


    @app.route('/logout', methods = ['GET', 'POST'])
    def logoutUser():
        try:
            session.clear()
        except:
            print("error")
            pass

        return redirect(url_for('home'))


    @app.route('/createAccount', methods = ['GET', 'POST'])
    def createAccount():
        if request.method == 'POST':
            database, cursor = cursorCreate()

            strUsername = request.form['txtUsername']
            sql = "SELECT UserID FROM User_mst WHERE Username=\"" + strUsername + "\";"
            cursor.execute(sql)
            if cursor.fetchall() != ():
                print("Warning: account found with same name. Account was not created.")
                cursor.close()
                database.close()
                return render_template("createAccount.html")

            strEmail = request.form['emailAddress']

            charAccountType = request.form['txtAccount']
            if charAccountType != "U" and charAccountType != "C" and charAccountType != "R":
                print("Warning: attempted signup with non-standard user type detected. Returning client to home page.")
                cursor.close()
                database.close()
                return render_template("createAccount.html")

            strPassword = request.form['txtPassword']
            strPassCheck = request.form['txtPasswordCheck']
            if strPassword != strPassCheck:
                print("Warning: passwords do not match. Returning client to account create page.")
                cursor.close()
                database.close()
                return render_template("createAccount.html")
            elif len(strPassword) < 8 or strPassword == strPassword.lower():
                print("Warning: password validation failed. Returning client to account create page.")
                cursor.close()
                database.close()
                return render_template("createAccount.html")

            strSaltedPass, strRandSalt = passSalt(strPassword)
            strPassHash = passHash(strSaltedPass)

            #Encryption goes here

            sql = "INSERT INTO User_mst (Username, PasswordHash, PasswordSalt, AccountType, EmailAddress) VALUES (\"" + strUsername + "\",\"" + strPassHash + "\",\"" + strRandSalt + "\",\"" + charAccountType + "\",\"" + strEmail + "\");"
            cursor.execute(sql)
            database.commit()

            cursor.close()
            database.close()

            return "<html><head><meta http-equiv=\"refresh\" content=\"2;" + url_for('home') + "\" /></head><body>Success - you will now be redirected to the home page.</body></html>"

        return render_template("createAccount.html")



    # Account Management
    # -------------------------------------------------------------------------------------------------------------------------------------------------
            
    @app.route('/changePassword', methods = ['GET', 'POST'])
    def changePassword():
        if session.get('userLoggedIn'):
            if request.method == "POST":
                strOldPassword = request.form['txtOldPassword']
                strNewPassword = request.form['txtNewPassword']
                strPasswordCheck = request.form['txtPassCheck']

                database, cursor = cursorCreate()

                sql = "SELECT PasswordHash, PasswordSalt FROM User_mst WHERE Username=\"" + session['strUsername'] + "\";"
                cursor.execute(sql)
                dictPassword = cursor.fetchone()

                strPassSalt = dictPassword["PasswordSalt"]
                strSaltedPass = strOldPassword + strPassSalt

                strPassHash = passHash(strSaltedPass)
                strRealHash = dictPassword["PasswordHash"]

                if strPassHash == strRealHash:
                    if strNewPassword != strPasswordCheck:
                        print("Error: new passwords do not match. Returning client to change password page.")
                        cursor.close()
                        database.close()
                        return render_template("changePassword.html")
                    elif len(strNewPassword) < 8 or strNewPassword == strPasswordCheck.lower():
                        print("Error: password validation failed. Returning client to change password page.")
                        cursor.close()
                        database.close()
                        return render_template("createAccount.html")

                    strSaltedPass, strRandSalt = passSalt(strNewPassword)
                    strPassHash = passHash(strSaltedPass)
                    
                    sql = "UPDATE User_mst SET PasswordHash=\"" + strPassHash + "\", PasswordSalt=\"" + strRandSalt + "\" WHERE Username=\"" + session['strUsername'] + "\";"
                    cursor.execute(sql)
                    database.commit()
                    
                    cursor.close()
                    database.close()
                    
                    return "<html><head><meta http-equiv=\"refresh\" content=\"2;" + url_for('home') + "\" /></head><body>Success - you will now be redirected to the account page.</body></html>"

                else:
                    print("Error: invalid old password when attempting to change password - returning client to change password page.")
                    cursor.close()
                    database.close()
                    return render_template("changePassword.html")

            return render_template("changePassword.html")
        else:
            return redirect(url_for('home'))        



    # Team Management
    # -------------------------------------------------------------------------------------------------------------------------------------------------

    @app.route('/createTeam', methods = ['GET', 'POST'])
    def createTeam():
        if session.get('userLoggedIn'):
            if request.method == "POST":
                # The section below imports all necessary values from the form
                strTeamName = request.form['txtTeamName']
                print(strTeamName)
                if session['strAccountType'] == "A":
                    strCoachName = request.form['txtCoachName']
                else:
                    strCoachName = session['strUsername']

                database, cursor = cursorCreate()

                try:
                    sql = "SELECT UserID FROM User_mst WHERE Username=\"" + strCoachName + "\" AND AccountType=\"C\";"
                    cursor.execute(sql)
                    intCoachID = cursor.fetchone()["UserID"]
                except TypeError:
                    print("Error thrown: " + str(sys.exc_info()[0]) + ". Returning user to create team page.")
                    cursor.close()
                    database.close()
                    return render_template("createTeam.html")

                sql = "SELECT TeamID FROM Team_mst WHERE TeamName=\"" + strTeamName + "\";"
                cursor.execute(sql)
                if cursor.fetchall() != ():
                    print("Error: team with the same team name exists.")
                    cursor.close()
                    database.close()
                    return render_template("createTeam.html")

                sql = "INSERT INTO Team_mst (TeamName, CoachID) VALUES (\"" + strTeamName + "\",\""  + str(intCoachID) + "\");"
                cursor.execute(sql)
                database.commit()

                cursor.close()
                database.close()

                return "<html><head><meta http-equiv=\"refresh\" content=\"2;" + url_for('home') + "\" /></head><body>Success - you will now be redirected to the account page.</body></html>"

            return render_template("createTeam.html")
        else:
            return redirect(url_for('home'))


    @app.route('/leaveTeam', methods = ['GET', 'POST'])
    def leaveTeam():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "U":
                database, cursor = cursorCreate()

                strTeamName = request.form['txtTeamName']
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + strTeamName + "\";"
                cursor.execute(sql)
                intTeamID = cursor.fetchall()["TeamID"]

                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + session['strUsername'] + "\";"
                cursor.execute(sql)
                intUserID = cursor.fetchall()["UserID"]

                try:
                    sql = "DELETE FROM UserToTeam_xrf WHERE UserID = \"" + str(intUserID) + "\" AND TeamID = \"" + str(intTeamID) + "\";"
                    cursor.execute(sql)

                    return redirect(url_for('viewTeams'))
                except:
                    return redirect(url_for('viewTeams'))

            else:
                print("Error: client is not a user account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))

            
    @app.route('/manageTeams', methods = ['GET', 'POST'])
    def manageTeams():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "C":
                database, cursor = cursorCreate()
                
                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + session['strUsername'] + "\";"
                cursor.execute(sql)
                
                sql = "SELECT TeamID FROM Team_mst WHERE CoachID = \"" + str(cursor.fetchone()["UserID"]) + "\";"
                cursor.execute(sql)

                dictTeams = {}
                for dictTeamIDs in cursor.fetchall():
                    sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + str(dictTeamIDs["TeamID"]) + "\";"
                    cursor.execute(sql)
                    strTeamName = cursor.fetchone()["TeamName"]
                
                    sql = "SELECT UserID FROM UserToTeam_xrf WHERE TeamID = \"" + str(dictTeamIDs["TeamID"]) + "\";"
                    cursor.execute(sql)
                    
                    lstUsers = []
                    for dictUser in cursor.fetchall():
                        sql = "SELECT Username FROM User_mst WHERE UserID = \"" + str(dictUser["UserID"]) + "\";"
                        cursor.execute(sql)
                        lstUsers.append(cursor.fetchone()["Username"])
                        
                    dictTeams[strTeamName] = mergeSort(lstUsers)
                
                #dictTeams = mergeSort(dictTeams)       FIX
                
                return render_template("manageTeams.html", dictTeams = dictTeams)

            else:
                print("Error: client is not a user account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))


    @app.route('/viewTeams', methods = ['GET', 'POST'])
    def viewTeams():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "U" or session['strAccountType'] == "C":
                database, cursor = cursorCreate()

                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + session['strUsername'] + "\";"
                cursor.execute(sql)

                sql = "SELECT TeamID FROM UserToTeam_xrf WHERE UserID = \"" + str(cursor.fetchone()['UserID']) + "\";"
                cursor.execute(sql)

                lstTeams = []
                for dictID in cursor.fetchall():
                    sql = "SELECT TeamName, CoachID FROM Team_mst WHERE TeamID = \"" + str(dictID["TeamID"]) + "\";"
                    cursor.execute(sql)
                    dictFetch = cursor.fetchone()

                    if session['strAccountType'] == "U":
                        strTeamName, intCoachID = dictFetch["TeamName"], dictFetch["CoachID"]
                        
                        sql = "SELECT Username FROM User_mst WHERE UserID = \"" + str(intCoachID) + "\";"
                        cursor.execute(sql)
                        
                        lstTeams.append([strTeamName, cursor.fetchone()["Username"]])
                    else:
                        strTeamName = dictFetch["TeamName"]
                        lstTeams.append([strTeamName])

                return render_template("viewTeams.html", lstTeams = lstTeams)

            else:
                print("Error: client is not a user account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))


    @app.route('/teamAddUser', methods = ['GET', 'POST'])
    def teamAddUser():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "C":
                database, cursor = cursorCreate()
            
                strUsername = request.form['txtUserName']
                strTeamName = request.form['txtTeamName']

                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + strUsername + "\";"
                cursor.execute(sql)
                intUserID = cursor.fetchone()["UserID"]
                
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + strTeamName + "\";"
                cursor.execute(sql)
                intTeamID = cursor.fetchone()["TeamID"]

                try:
                    sql = "INSERT INTO UserToTeam_xrf (UserID, TeamID) VALUES (\"" + str(intUserID) + "\",\"" + str(intTeamID) + "\");"
                    print(sql)
                    cursor.execute(sql)
                    database.commit()
                except:
                    print("Error: user not in this team.")
                    
                return redirect(url_for('manageTeams'))

            else:
                print("Error: client is not a coach account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))


    @app.route('/teamDropUser', methods = ['GET', 'POST'])
    def teamDropUser():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "C":
                database, cursor = cursorCreate()
            
                strUsername = request.form['txtUserName']
                strTeamName = request.form['txtTeamName']
                
                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + strUsername + "\";"
                cursor.execute(sql)
                intUserID = cursor.fetchone()["UserID"]
                
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + strTeamName + "\";"
                cursor.execute(sql)
                intUserID = cursor.fetchone()["TeamID"]
                
                sql = "DELETE FROM UserToTeam_xrf WHERE UserID = \"" + str(intUserID) + "\" AND TeamID = \"" + str(intTeamID) + "\";"
                cursor.execute(sql)

                return redirect(url_for('manageTeams'))

            else:
                print("Error: client is not a coach account type. Returning client to manage teams page")
                return render_template("manageTeams")
        else:
            print("Error: client is not logged in. Returning client to manage teams page")
            return render_template("manageTeams")
    
    
    
    # League Management
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    
    @app.route('/createLeague', methods = ['GET', 'POST'])
    def createLeague():
        if session.get('userLoggedIn'):
            if request.method == 'POST':
                database, cursor = cursorCreate()

                # RULESET SETUP

                try:
                    intMatchLength = int(request.form['numMatchLength'])
                except:
                    print("Error: invalid match length entered. Returning client to create league page")
                    cursor.close()
                    database.close()
                    return render_template("createLeague.html")

                if request.form["ckbExtraTime"] == "ckbExtraTime":
                    intExtraTime = 1
                    intETLength = request.form["numExtraTime"]
                else:
                    intExtraTime = 0
                    intETLength = 0

                if request.form["ckbPenalties"] == "ckbPenalties":
                    intPenalties = 1
                else:
                    intPenalties = 0

                try:
                    intTeamPlayers = int(request.form['numPlayersTeam'])
                except:
                    print("Error: invalid match length entered. Returning client to create league page")
                    cursor.close()
                    database.close()
                    return render_template("createLeague.html")

                if intTeamPlayers == '' or intMatchLength == "" or intMatchLength == 0 or intTeamPlayers == 0:
                    print("Error: missing required field. Returning client to create league page.")
                    cursor.close()
                    database.close()
                    return render_template("createLeague.html")

                sql = "SELECT RulesetID FROM Rules_mst WHERE MatchLength=" + str(intMatchLength) + " AND ExtraTime=" + str(intExtraTime) + " AND ExtraTimeLength=" + str(intETLength) + " AND Penalties=" + str(intPenalties) + " AND NumPlayers=" + str(intTeamPlayers) + ";"
                cursor.execute(sql)
                dictRuleset = cursor.fetchone()

                if dictRuleset != None:
                    intRuleID = dictRuleset["RulesetID"]
                else:
                    sql = "INSERT INTO Rules_mst (MatchLength, ExtraTime, ExtraTimeLength, Penalties, NumPlayers) VALUES (\"" + str(intMatchLength) + "\",\"" + str(intExtraTime) + "\",\"" + str(intETLength) + "\",\"" + str(intPenalties) + "\",\"" + str(intTeamPlayers) + "\");"
                    cursor.execute(sql)
                    database.commit()

                    sql = "SELECT RulesetID FROM Rules_mst WHERE MatchLength=" + str(intMatchLength) + " AND ExtraTime=" + str(intExtraTime) + " AND ExtraTimeLength=" + str(intETLength) + " AND Penalties=" + str(intPenalties) + " AND NumPlayers=" + str(intTeamPlayers) + ";"
                    cursor.execute(sql)
                    intRuleID = cursor.fetchone()["RulesetID"]


                # LEAGUE SETUP

                strLeagueName = request.form['txtLeagueName']
                intTeamLimit = request.form['numTeamLimit']
                strFormat = request.form['txtFormat']

                sql = "SELECT LeagueID FROM League_mst WHERE LeagueName=\"" + strLeagueName + "\";"
                cursor.execute(sql)
                if cursor.fetchall() != ():
                    print("Warning: league found with same name. Returning client to create league page.")
                    cursor.close()
                    database.close()
                    return render_template("createLeague.html")

                intTeamsEntered = 0

                if strFormat != "R" and strFormat != "E":
                    print("Invalid league format entered - returning user to create league page.")
                    cursor.close()
                    database.close()
                    return render_template("createLeague.html")
                else:
                    if strFormat == "R":
                        intFormat = 0
                    else:
                        intFormat = 1

                sql = "INSERT INTO League_mst (LeagueName, RulesetID, TeamLimit, RegisteredTeams, Format) VALUES (\"" + strLeagueName + "\",\"" + str(intRuleID) + "\",\"" + str(intTeamLimit) + "\",\"" + str(intTeamsEntered) + "\",\"" + str(intFormat) + "\");"
                cursor.execute(sql)
                database.commit()

                cursor.close()
                database.close()

                return "<html><head><meta http-equiv=\"refresh\" content=\"2;" + url_for('home') + "\" /></head><body>Success - you will now be redirected to the home page.</body></html>"
                
            return render_template("createLeague.html")
        else:
            return redirect(url_for('home'))

            
    @app.route('/bracket/<strLeagueName>', methods = ['GET', 'POST'])
    def bracket(strLeagueName):
        if session.get('userLoggedIn'):
            database, cursor = cursorCreate()
            
            sql = "SELECT LeagueID, Format FROM League_mst WHERE LeagueName = \"" + strLeagueName + "\";"
            cursor.execute(sql)
            dictFetch = cursor.fetchone()

            intLeagueID, intFormat = dictFetch["LeagueID"], dictFetch["Format"]

            sql = "SELECT TeamID FROM TeamToLeague_xrf WHERE LeagueID = \"" + str(intLeagueID) + "\";"
            cursor.execute(sql)

            lstTeams = []
            for dictID in cursor.fetchall():
                sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + str(dictID["TeamID"]) + "\";"
                cursor.execute(sql)
                lstTeams.append(cursor.fetchone()["TeamName"])
            
            if intFormat == 0:
                lstMatches = []
                for intCount in range(0, len(lstTeams)):
                    for intCount2 in range(0, len(lstTeams)):
                        lstMatches.append([lstTeams[intCount], lstTeams[intCount2], None, None, None])
            
                for lstMatch in lstMatches:
                    if lstMatch[0] == lstMatch[1]:
                        lstSend.append(None)
                    else:
                        sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + lstMatch[0] + "\";"
                        cursor.execute(sql)
                        intTeam1ID = cursor.fetchone()["TeamID"]
                        
                        sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + lstMatch[1] + "\";"
                        cursor.execute(sql)
                        intTeam2ID = cursor.fetchone()["TeamID"]
                        
                        sql = "SELECT Team1Score, Team2Score, WinnerTeam FROM Matches_dtl WHERE LeagueID = \"" + str(intLeagueID) + "\" AND Team1Name = \"" + str(lstMatch[0]) + "\" AND Team2Name = \"" + str(lstMatch[1]) + "\";"
                        cursor.execute(sql)
                        dictFetch = cursor.fetchone()
                        if dictFetch is None:
                            sql = "SELECT Team1Score, Team2Score, WinnerTeam FROM Matches_dtl WHERE LeagueID = \"" + str(intLeagueID) + "\" AND Team1Name = \"" + str(lstMatch[1]) + "\" AND Team2Name = \"" + str(lstMatch[0]) + "\";"
                            cursor.execute(sql)
                            dictFetch = cursor.fetchone()
                        
                        if dictFetch["WinnerTeam"] == None:
                            lstSend.append[lstMatch[0], lstMatch[1], None, None, None]
                        
                        else:
                            sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + dictFetch["WinnerTeam"] + "\";"
                            cursor.execute(sql)
                            strWinner = cursor.fetchone()["TeamName"]
                        
                            lstSend.append[lstMatch[0], lstMatch[1], dictFetch["Team1Score"], dictFetch["Team2Score"], strWinner]
                        
                return render_template("viewBracket.html", lstSend = lstSend, lstTeams = lstTeams, intFormat = intFormat)
                
            else:

                lstMatches = CompleteList(lstTeams)

                objMatch = Match(lstMatches)
                lstTraverse = objMatch.TraverseBracket(objMatch, 0, 0, [])
                
                intLevels = 0
                for lstTeam in lstTraverse:
                    if lstTeam[1] not in lstLevels:
                        intLevels += 1
            
                return render_template("viewBracket.html", lstMatches = lstTraverse, intLevels = intLevels, intFormat = intFormat)


    @app.route('/leagueAddTeam', methods = ['GET', 'POST'])
    def leagueAddTeam():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "C":
                database, cursor = cursorCreate()
                
                strLeagueName = request.form["txtLeagueName"]
                strTeamName = request.form["txtTeamName"]
                
                sql = "SELECT LeagueID FROM League_mst WHERE LeagueName = \"" + strLeagueName + "\";"
                try:
                    cursor.execute(sql)
                except:
                    print("Error: invalid league name. Returning client to previous page")
                    return redirect(url_for('manageTeams'))
                intLeagueID = cursor.fetchone()["LeagueID"]
                
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + strTeamName + "\";"
                try:
                    cursor.execute(sql)
                except:
                    print("Error: invalid team name. Returning client to previous page")
                    return redirect(url_for('manageTeams'))
                intTeamID = cursor.fetchone()["TeamID"]
                
                sql = "INSERT INTO TeamToLeague_xrf (LeagueID, TeamID) VALUES (\"" + str(intLeagueID) + "\",\"" + str(intTeamID) + "\");"
                cursor.execute(sql)
                database.commit()

                cursor.close()
                database.close()
                
                return redirect(url_for('manageTeams'))

            else:
                print("Error: client is not a coach account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))


    @app.route('/unstartedLeagues', methods = ['GET', 'POST'])
    def unstartedLeagues():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "A":
                database, cursor = cursorCreate()
                
                sql = "SELECT LeagueID, LeagueName, TeamLimit, RegisteredTeams, Format FROM League_mst WHERE LeagueStarted = 0;"
                cursor.execute(sql)
                
                lstLeagues = []
                for dictLeague in cursor.fetchall():
                    if dictLeague["Format"] == 0:
                        strFormat = "Round Robin"
                    else:
                        strFormat = "Elimination"
                    
                    lstLeagues.append([dictLeague["LeagueID"], dictLeague["LeagueName"], dictLeague["RegisteredTeams"], dictLeague["TeamLimit"], strFormat])

                return render_template("unstartedLeagues.html", lstLeagues = lstLeagues)

            else:
                print("Error: client is not a user account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))
                
                
    @app.route('/viewLeagues/<strTeamName>', methods = ['GET', 'POST'])
    @app.route('/viewLeagues', defaults = {'strTeamName': ''}, methods = ['GET', 'POST'])
    def viewLeagues(strTeamName):
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "U" or session['strAccountType'] == "C":
                database, cursor = cursorCreate()
                
                if strTeamName == "":
                    sql = "SELECT UserID FROM User_mst WHERE Username = \"" + session['strUsername'] + "\";"
                    cursor.execute(sql)
                    intUserID = cursor.fetchone()["UserID"]

                    sql = "SELECT TeamID FROM UserToTeam_xrf WHERE UserID = \"" + str(intUserID) + "\";"
                    cursor.execute(sql)
                else:
                    sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + strTeamName + "\";"
                    cursor.execute(sql)
                    
                lstFetchTeams = cursor.fetchall()

                lstLeagues = []
                for dictTeamID in lstFetchTeams:
                    sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + str(dictTeamID["TeamID"]) + "\";"
                    cursor.execute(sql)
                    strTeamName = cursor.fetchone()["TeamName"]

                    sql = "SELECT LeagueID FROM TeamToLeague_xrf WHERE TeamID = \"" + str(dictTeamID["TeamID"]) + "\";"
                    cursor.execute(sql)
                    lstFetchLeagues = cursor.fetchall()

                    for dictLeagueID in lstFetchLeagues:
                        sql = "SELECT LeagueName, LeagueStarted FROM League_mst WHERE LeagueID = \"" + str(dictLeagueID["LeagueID"]) + "\";"
                        cursor.execute(sql)
                        dictFetch = cursor.fetchone()
                        lstLeagues.append([dictFetch["LeagueName"], strTeamName, dictFetch["LeagueStarted"]])

                return render_template("viewLeagues.html", lstLeagues = lstLeagues)

            else:
                print("Error: client is not a valid account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))



    # Referee Functions
    # -------------------------------------------------------------------------------------------------------------------------------------------------
    
    @app.route('/viewMatches', methods = ['GET', 'POST'])
    def viewMatches():
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "R":
                database, cursor = cursorCreate()

                sql = "SELECT UserID FROM User_mst WHERE Username = \"" + session['strUsername'] + "\";"
                cursor.execute(sql)
                intUserID = cursor.fetchone()["UserID"]

                sql = "SELECT LeagueID, Team1ID, Team2ID FROM Matches_dtl WHERE RefereeID = \"" + str(intUserID) + "\" AND Team1Score IS NULL;"
                cursor.execute(sql)
                lstFetch = cursor.fetchall()

                lstMatches = []
                for dictMatch in lstFetch:
                    sql = "SELECT LeagueName, RulesetID FROM League_mst WHERE LeagueID = \"" + dictMatch["LeagueName"] + "\";"
                    cursor.execute(sql)
                    dictFetch = cursor.fetchone()

                    sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + str(dictMatch["Team1ID"]) + "\";"
                    cursor.execute(sql)
                    strTeam1 = cursor.fetchone()["TeamName"]

                    sql = "SELECT TeamName FROM Team_mst WHERE TeamID = \"" + str(dictMatch["Team2ID"]) + "\";"
                    cursor.execute(sql)
                    strTeam2 = cursor.fetchone()["TeamName"]

                    lstMatch = [dictFetch["LeagueName"], strTeam1, strTeam2]
                    lstMatches.append(lstMatch)

                return render_template("viewMatches.html", lstMatches = lstMatches)

            else:
                print("Error, invalid account type attempting to view referee-only page. Returning client to home page")
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))


    @app.route('/reportScore/<lstMatch>', methods = ['GET', 'POST'])
    @app.route('/reportScore', defaults = {'lstMatch': ''}, methods = ['GET', 'POST'])
    def reportScore(lstMatch):
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "R":

                sql = "SELECT LeagueID FROM League_mst WHERE LeagueName = \"" + lstMatch[0] + "\";"
                cursor.execute(sql)
                intLeagueID = cursor.fetchone()["LeagueID"]
                    
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + lstMatch[1] + "\";"
                cursor.execute(sql)
                intTeam1ID = cursor.fetchone()["TeamID"]
                    
                sql = "SELECT TeamID FROM Team_mst WHERE TeamName = \"" + lstMatch[2] + "\";"
                cursor.execute(sql)
                intTeam2ID = cursor.fetchone()["TeamID"]
            
                if request.method == "POST":
                    database, cursor = cursorCreate()
                    
                    if Team1Score > Team2Score:
                        intWinnerTeamID = intTeam1ID
                    elif Team2Score > Team1Score:
                        intWinnerTeamID = intTeam2ID
                    
                    if lstMatch[5] != None and lstMatch[6] != None:
                        sql = "UPDATE Matches_dtl SET Team1Score = \"" + str(lstMatch[3]) + "\", Team2Score = \"" + str(lstMatch[4]) + "\", Team1Penalties = \"" + str(lstMatch[5]) + "\", Team2Penalties = \"" + str(lstMatch[6]) + "\", WinnerTeam = \"" + str(intWinnerTeamID) + "\" WHERE LeagueID = \"" + strLeagueName + "\" AND Team1ID = \"" + str(intTeam1ID) + "\" AND Team2ID = \"" + str(intTeam2ID) + "\";"
                    else:
                        sql = "UPDATE Matches_dtl SET Team1Score = \"" + str(lstMatch[3]) + "\", Team2Score = \"" + str(lstMatch[4]) + "\", WinnerTeam = \"" + str(intWinnerTeamID) + "\" WHERE LeagueID = \"" + strLeagueName + "\" AND Team1ID = \"" + str(intTeam1ID) + "\" AND Team2ID = \"" + str(intTeam2ID) + "\";"
                    
                    cursor.execute(sql)
                    database.commit()

                    cursor.close()
                    database.close()
                    
                    return redirect(url_for('viewMatches'))
                    
                else:
                    
                    sql = "SELECT RulesetID FROM League_mst WHERE LeagueName = \"" + lstMatch[0] + "\";"
                    cursor.execute(sql)
                    intRulesetID = cursor.fetchone()["RulesetID"]
                    
                    sql = "SELECT Penalties FROM Rules_mst WHERE RulesetID = \"" + str(intRulesetID) + "\";"
                    cursor.execute(sql)
                    intPenalties = cursor.fetchone()["Penalties"]
                    
                    lstMatches.append(intPenalties)
                    
                    return render_template('reportScore.html', lstMatch = lstMatch)
                    
            else:
                print("Error: client is not an referee account type. Returning client to previous page")
                return redirect(url_for('viewMatches'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))


    @app.route('/startLeague', defaults = {'strLeagueName': ''}, methods = ['GET', 'POST'])
    @app.route('/startLeague/<strLeagueName>', methods = ['GET', 'POST'])
    def startLeague(strLeagueName):
        if session.get('userLoggedIn'):
            if session['strAccountType'] == "A":
                if request.method == "POST":
                    database, cursor = cursorCreate()

                    sql = "SELECT LeagueID FROM League_mst WHERE LeagueName = \"" + strLeagueName + "\";"
                    cursor.execute(sql)
                    intLeagueID = cursor.fetchone()["LeagueID"]

                    sql = "SELECT * FROM TeamToLeague_xrf WHERE LeagueID = \"" + str(intLeagueID) + "\";"
                    cursor.execute(sql)
                    lstTeams = cursor.fetchall()

                    arrTeamIDs = []
                    for intLoopCount in range(0, len(lstTeams)):
                        arrTeamIDs.append(lstTeams[intLoopCount]["TeamID"])

                    sql = "SELECT Format, RegisteredTeams FROM League_mst WHERE LeagueID = \"" + str(intLeagueID) + "\";"
                    cursor.execute(sql)
                    dictFetch = cursor.fetchone()

                    intFormat = dictFetch["Format"]
                    intTeamCount = dictFetch["RegisteredTeams"]

                    if intFormat == 0:
                        lstMatches = []

                        for intLoopCount in range(0, (intTeamCount-1)):
                            for intOpponentCount in range((1+intLoopCount), intTeamCount):
                                lstMatches.append([arrTeamIDs[intLoopCount], arrTeamIDs[intOpponentCount]])

                        for lstMatch in lstMatches:
                            sql = "INSERT INTO Matches_dtl (LeagueID, Team1ID, Team2ID) VALUES (\"" + str(intLeagueID) + "\",\"" + str(lstMatch[0]) + "\",\"" + str(lstMatch[1]) + "\");"
                            cursor.execute(sql)

                    elif intFormat == 1:
                        arrMatches = CompleteList(arrTeamIDs)

                        try:
                            print(str(arrMatches) + "\n\n")
                        except:
                            print("No matches found.")

                        objMatch = Match(arrMatches)
                        allowProc = objMatch.TraverseBracket(objMatch, 0)

                    return redirect(url_for('home'))
                return render_template("startLeague.html")
            else:
                print("Error: client is not an administrator account type. Returning client to home page")
                return redirect(url_for('home'))
        else:
            print("Error: client is not logged in. Returning client to home page")
            return redirect(url_for('home'))

    app.secret_key = "some secret key"

    if __name__ == "__main__":
        app.static_folder = 'static'
        app.run(host='0.0.0.0', port=3000)