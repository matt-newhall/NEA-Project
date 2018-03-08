def searchRules():
    sql = "SELECT RulesetID FROM Rules_mst WHERE MatchLength = " + str(intMatchLength) + " AND ExtraTime = " + str(boolExtraTime) + " AND ExtraTimeLength = " + str(numExtraTime) + " AND Penalties = " + str(boolPenalties) + " AND NumPlayers = " + str(intTeamPlayers) + ";"
    cursor.execute(sql)
