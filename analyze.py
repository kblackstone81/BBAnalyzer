import glob
import os
import sys
import sqlite3

#Remove the ending of a string, if it exists
def chopEndOfString(string, ending):
  if string.endswith(ending):
    return string[:-len(ending)]
  return string

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
	for row in conn.execute("""
	SELECT pl.ID, \
	pl.strName as Name, \
	t.DATA_CONSTANT AS Type, \
	ROUND(pl.Characteristics_fMovementAllowance * 0.12, 0) As MV, \
	ROUND(pl.Characteristics_fStrength * 0.06, 0) as ST, \
	ROUND(pl.Characteristics_fAgility * 0.06, 0) as AG, \
	ROUND(pl.Characteristics_fArmourValue * 0.11, 0) as AV, \
	pl.idPlayer_Levels as Level, \
	pl.iExperience as Exp, \
	pl.iValue as Value, \
	Group_Concat(DISTINCT ts.DESCRIPTION) AS DefaultSkills, \
	Group_Concat(DISTINCT mainsl.DATA_CONSTANT) AS LevelSkills \
	from """ + teamListing + """ pl \
	left outer join """ + teamPlayerTypes + """ t on pl.idPlayer_Types = t.ID \
	left outer join """ + teamPlayerTypeSkills + """ ts on pl.idPlayer_Types = ts.idPlayer_Types \
	left outer join """ + teamPlayerSkills + """ ps on pl.ID = ps.idPlayer_Listing \
	left outer join MainDB.Skill_Listing mainsl on ps.idSkill_Listing = mainsl.ID \
	group by pl.ID """):
		outputFile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\n' % row)

	return

if __name__ == '__main__':

    # Starting point
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = min(glob.iglob('*.db'), key=os.path.getctime)
    print(file)

    conn = sqlite3.connect(file)
    print "Opened database successfully";

    conn.execute("ATTACH DATABASE 'WorldCup.db' AS MainDB")
    print "Attached MainDB";

    outputFileName = chopEndOfString(file, ".db") + "_Summary.txt"
    outputFile = open(outputFileName, "w+", 0)
    writeTeamInfo(conn, outputFile, "Home")
    outputFile.write('\n')
    writeTeamInfo(conn, outputFile, "Away")
    outputFile.write('\n')
    print "Operation done successfully";

    outputFile.close();

    conn.close;
