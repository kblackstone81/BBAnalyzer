import glob
import os
import sys
import sqlite3
import json


sql_fmt = ('SELECT pl.ID AS ID, '
           'pl.strName AS Name, '
           't.DATA_CONSTANT AS Type, '
           'ROUND(pl.Characteristics_fMovementAllowance * 0.12, 0) AS MV, '
           'ROUND(pl.Characteristics_fStrength * 0.06, 0) AS ST, '
           'ROUND(pl.Characteristics_fAgility * 0.06, 0) AS AG, '
           'ROUND(pl.Characteristics_fArmourValue * 0.11, 0) AS AV, '
           'pl.idPlayer_Levels AS Level, '
           'pl.iExperience AS Exp, '
           'pl.iValue AS Value, '
           'Group_Concat(DISTINCT ts.DESCRIPTION) AS DefaultSkills, '
           'Group_Concat(DISTINCT mainsl.DATA_CONSTANT) AS LevelSkills '
           'FROM {0}_Player_Listing pl '
           'LEFT OUTER JOIN {0}_player_types t ON pl.idPlayer_Types = t.ID '
           'LEFT OUTER JOIN {0}_player_Type_Skills ts '
           'ON pl.idPlayer_Types = ts.idPlayer_Types '
           'LEFT OUTER JOIN {0}_Player_Skills ps '
           'ON pl.ID = ps.idPlayer_Listing '
           'LEFT OUTER JOIN MainDB.Skill_Listing mainsl '
           'ON ps.idSkill_Listing = mainsl.ID '
           'GROUP BY pl.ID'
           )

col_headers = [
    'ID',
    'Name',
    'Position',
    'MV',
    'ST',
    'AG',
    'AV',
    'Level',
    'Exp',
    'Value',
    'Default Skills',
    'Level Skills'
]


def fetchData(conn):
    data = {}
    home = "Home"
    away = "Away"
    teamPosition_fmt = "{0} Team"
    data[teamPosition_fmt.format(home)] = fetchTeamData(conn, home)
    data[teamPosition_fmt.format(away)] = fetchTeamData(conn, away)
    return data


def fetchTeamData(conn, teamStr):
    sql = sql_fmt.format(teamStr)
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    data = makeTeamJson(rows)
    return data


def makeTeamJson(teamData):
    data = {}
    roster = {}
    for i, row in zip(range(1, len(teamData) + 1), teamData):
        roster[str(i)] = makePlayerJson(row)
    data["roster"] = roster
    return data


def makePlayerJson(playerData):
    data = {}
    for key, value in zip(col_headers, playerData):
        data[key] = value
    return data


if __name__ == '__main__':

    # Starting point
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            raise ValueError(
                "'{0}' is an invalid file name.".format(sys.argv[1]))
        file = os.path.basename(sys.argv[1])

    else:
        file = max(glob.iglob('*.db'), key=os.path.getctime)
    print("Input: {0}".format(file))

    conn = sqlite3.connect(file)
    print("Opened database successfully")

    conn.execute("ATTACH DATABASE 'WorldCup.db' AS MainDB")
    print("Attached MainDB")

    data = fetchData(conn)
    print("Data fetched")

    outputFileName = os.path.splitext(file)[0] + "_Summary.txt"
    print("Output file: {0}".format(outputFileName))

    with open(outputFileName, "w+", 1) as outputFile:
        outputFile.write(json.dumps(data))
        print("Operation done successfully")

    conn.close()
