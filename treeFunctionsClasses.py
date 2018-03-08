import pymysql
from cursorCreate import *

class Match:
    def __init__(self, data):
        self.leftTeam = None
        self.winnerTeam = data
        self.rightTeam = None

        if not(isinstance(self.winnerTeam, int)) and self.winnerTeam != None:
            self.DivideBracket()

    def DivideBracket(self):
        if len(self.winnerTeam) != 1:
            self.leftTeam, self.rightTeam = Match(self.winnerTeam[:(int(len(self.winnerTeam)/2))]), Match(self.winnerTeam[(int(len(self.winnerTeam)/2)):])
            self.winnerTeam = None
        else:
            self.leftTeam, self.rightTeam = Match(self.winnerTeam[0][0]), Match(self.winnerTeam[0][1])
            self.winnerTeam = None


    def TraverseBracket(self, Match, intLevel, intMode, lstPass):
        
        self.DeleteNull(Match)

        # Left Child
        if Match.leftTeam != None:
            lstPass = self.TraverseBracket(Match.leftTeam, intLevel+1, intMode, lstPass)
        elif Match.leftTeam == None and Match.rightTeam != None:
            lstPass.append([None, None, None, None, None, intLevel])

        if intMode == 0:
            # Inspect Node
            try:
                if Match.leftTeam.winnerTeam != None and Match.rightTeam.winnerTeam != None:
                    database, cursor = cursorCreate()

                    sql = "SELECT LeagueID FROM League_mst WHERE LeagueName = \"" + strLeagueName + "\";"
                    cursor.execute(sql)
                    intLeagueID = cursor.fetchone()["LeagueID"]

                    sql = "SELECT MatchID FROM Matches_dtl WHERE Team1ID = \"" + Match.leftTeam.winnerTeam + "\" AND Team2ID = \"" + Match.rightTeam.winnerTeam + "\" AND LeagueID = \"" + strLeagueName + "\";"
                    cursor.execute(sql)
                    if cursor.fetchall() == ():
                        sql = "INSERT INTO Match_dtl (LeagueID, Team1ID, Team2ID) VALUES (\"" + str(intLeagueID) + "\",\"" + str(Match.leftTeam.winnerTeam) + "\",\"" + str(Match.rightTeam.winnerTeam) + "\");"
                        cursor.execute(sql)
                        database.commit()
            except:
                pass

            try:
                cursor.close()
                database.close()
            except:
                pass
        else:
            database, cursor = cursorCreate()
            
            try:
                sql = "SELECT Team1Score, Team2Score, WinnerTeam FROM Matches_dtl WHERE Team1ID = \"" + Match.leftTeam.winnerTeam + "\" AND Team2ID = \"" + Match.rightTeam.winnerTeam + "\" AND LeagueID = \"" + strLeagueName + "\";"
                cursor.execute(sql)
                dictFetch = cursor.fetchone()
            
                lstPass.append([str(Match.leftTeam.winnerTeam), str(Match.rightTeam.winnerTeam), dictFetch[0], dictFetch[1], dictFetch[2], intLevel])
            except:
                if Match.leftTeam.winnerTeam == None:
                    lstPass.append([None, str(Match.rightTeam.winnerTeam), None, None, None, intLevel])
                else:
                    lstPass.append([str(Match.leftTeam.winnerTeam), None, None, None, None, intLevel])

        # Right Child
        if Match.rightTeam != None:
            lstPass = self.TraverseBracket(Match.rightTeam, intLevel+1, intMode, lstPass)

        if intMode == 1:
            return lstPass
        else:
            return None


    def DeleteNull(self, Match):
        try:
            if Match.rightTeam.winnerTeam == None and Match.leftTeam.winnerTeam != None:
                Match.winnerTeam = Match.leftTeam.winnerTeam
                Match.leftTeam, Match.rightTeam = None, None
        except:
            pass

        return Match


def halfList(arrIn):
    intHalf = int(len(arrIn)/2)
    return arrIn[:intHalf], arrIn[intHalf:]


def CompleteList(arrTeams):
    intNumOfTeams = int(len(arrTeams))
    boolEven, intTwoPower, intAddNone = False, 0, 0

    if intNumOfTeams == 0 or intNumOfTeams == 1:
        print("Not enough teams in league.")
        return None
    elif intNumOfTeams == 2:
        return [arrTeams]
    else:
        while boolEven == False:
            intTwoPower += 1

            if (intNumOfTeams - 2**intTwoPower) == 0:
                boolEven = True
            elif (intNumOfTeams - 2**intTwoPower) < 0:
                boolEven = True

                while intAddNone == 0:
                    if len(arrTeams) != 2**intTwoPower:
                        arrTeams.append(None)
                    else:
                        intAddNone = 1
    print(arrTeams)
    arrMatches1, arrMatches2 = CondenseList(arrTeams)

    if len(arrMatches1) != 1:
        arrOut1, arrOut2 = StartPositionMatches(arrMatches1), StartPositionMatches(arrMatches2)
    else:
        arrOut1, arrOut2 = arrMatches1, arrMatches2

    return arrOut1 + arrOut2

def CondenseList(arrOld):
    import math, cmath
    if len(arrOld) != 2 and len(arrOld) != 1:
        arrLeft, arrRight, complexCount = [], [], 1j

        for intLoopCount in range(0, int(len(arrOld)/2)):
            if math.copysign(intLoopCount, (complexCount.real + complexCount.imag)) == intLoopCount:
                arrLeft.append([arrOld[intLoopCount], arrOld[len(arrOld)-intLoopCount-1]])
            else:
                arrRight.append([arrOld[intLoopCount], arrOld[len(arrOld)-intLoopCount-1]])
            complexCount *= 1j

        return arrLeft, arrRight
    return arrOld


def ReverseList(arrIn):
    arrIn.reverse()
    return arrIn


def StartPositionMatches(arrIn):
    arrHalf1, arrHalf2 = halfList(arrIn)
    arrHalf2 = ReverseList(arrHalf2)
    return PositionMatches(arrHalf1, arrHalf2)


def PositionMatches(arrHalf1, arrHalf2):
    arrNew1 = []

    while len(arrHalf1) != 0:
        try:
            arrNew1.extend([arrHalf1.pop(0), arrHalf2.pop(0)])
            arrNew1.extend([arrHalf1.pop(len(arrHalf1)-1), arrHalf2.pop(len(arrHalf2)-1)])
        except:
            return arrNew1
        if len(arrHalf1) != 0:
            arrNew1.extend([arrHalf1.pop((len(arrHalf1)/2-1)), arrHalf2.pop((len(arrHalf2)/2-1))])
            arrNew1.extend([arrHalf1.pop(int(math.floor(len(arrHalf1)/2))), arrHalf2.pop(int(math.floor(len(arrHalf2)/2)))])

    return arrNew1
