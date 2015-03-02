import glob
import os
import sys
import sqlite3


# Get the information for the requested team
    # conn - database connection
    # teamString - prefix for the team requested (Home or Away)
def writeTeamInfo( conn, outputFile, teamString ):

    # define local team variables for the queury
    teamListing = (teamString + "_Player_Listing")
    teamPlayerTypes = teamString + "_player_types"
    teamPlayerTypeSkills = teamString + "_player_Type_Skills"
    teamPlayerSkills = teamString + "_Player_Skills"
    outputFile.write(teamListing + '\n');

    # run the query to get the team data from the db
    sql = ('SELECT pl.ID, '
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
        'LEFT OUTER JOIN {0}_player_Type_Skills ts ON pl.idPlayer_Types = ts.idPlayer_Types '
        'LEFT OUTER JOIN {0}_Player_Skills ps ON pl.ID = ps.idPlayer_Listing '
        'LEFT OUTER JOIN MainDB.Skill_Listing mainsl ON ps.idSkill_Listing = mainsl.ID '
        'GROUP BY pl.ID'
        ).format(teamString)

    rows = [', '.join([str(col) for col in row]) for row in conn.execute(sql)]
    outputFile.write('\n'.join(rows) + '\n')

if __name__ == '__main__':

    # Starting point
    if len(sys.argv) > 1:
        if not os.path.isfile(sys.argv[1]):
            raise ValueError("'{0}' is an invalid file name.".format(sys.argv[1]))
        file = os.path.basename(sys.argv[1])

    else:
        file = min(glob.iglob('*.db'), key=os.path.getctime)
    print("Input: {0}".format(file))

    conn = sqlite3.connect(file)
    print("Opened database successfully");

    conn.execute("ATTACH DATABASE 'WorldCup.db' AS MainDB")
    print("Attached MainDB");

    outputFileName = os.path.splitext(file)[0] + "_Summary.txt"
    print("Output file: {0}".format(outputFileName))

    with open(outputFileName, "w+", 1) as outputFile:
        writeTeamInfo(conn, outputFile, "Home")
        outputFile.write('\n')
        writeTeamInfo(conn, outputFile, "Away")
        outputFile.write('\n')
        print("Operation done successfully")

    conn.close()
