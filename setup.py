#!/usr/bin/python

import os
import argparse
import sqlite3
import json
from pathlib import Path

"""
Vulnerability Management Tracking Tools

install and setup script

"""

#
# Default Values
#
verbose = False

db_file = "data.db"
db_schema_file = "db_schema.json"
db_lookup_tables = "db_lookups.json"

argParser = argparse.ArgumentParser()

def debug( message ):
	""" If verbosity is set, print the message

	:param message: message to display
	:return:
	"""
	global verbose
	if verbose:
		print( message )

def create_db_connection(db_file):
	""" Create a database connection to the SQLite database
		specified by the db_file
	:param db_file: database file name
	:return: Connection object or None
	"""

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except NameError as e:
		print(e)

	return None

def init():
	""" Initialization function
	:param : none
	:return: none
	"""
	global verbose, db_file, db_schema_file, db_lookup_tables

	argParser = argparse.ArgumentParser()

	debug( "Enter init() function.")
	# Parse the command line arguments
	argParser.add_argument( "-v", "--verbose", action="store_true", help="Turn on verbose mode." )
	argParser.add_argument( "-d", "--db",                           help="Specifiy the name of the database file.")
	argParser.add_argument( "-c", "--clean",   action="store_true", help="Delete the database file.")
	argParser.add_argument( "-s", "--schema",                       help="Set a database schema description file.")
	argParser.add_argument( "-l", "--lookup",                       help="Set lookup table values.")

	args = vars( argParser.parse_args() )

	# Turn on verbose mode
	if args['verbose']:
		verbose = True

	# Set the database file name
	if args['db'] != None:
		db_file = args['db']
		debug("Database file set to " + db_file + ".")

	# Delete the database file if cleaning up
	if args['clean']:
		debug("About to delete the database file " + db_file + ".")
		file = Path(db_file)
		if file.exists():
			debug("The database file " + db_file + " exists, about to delete it.")
			os.unlink( db_file )
			if not file.exists():
				debug( "Database file was deleted.")
			else:
				debug("Unable to delete the database file.")
		else:
			debug("No need to delete the database file " + db_file + " because it did not exist in the first place.")

	# Set the database schema description file
	if args['schema'] != None:
		db_schema_file = args['schema']
	debug("Database schema description file set to " + db_schema_file + ".")

	# Set the lookup table values file
	if args['lookup'] != None:
		db_lookup_tables = args['lookup']
	debug("Lookup table file is " + db_lookup_tables + ".")

	debug( "Exiting init() function.")
	return

def create_database():
	"""
	Create the database
	:param:     none
	:return:    exit code
	"""
	# Create the database
	debug("Checking to see if the database file " + db_file + " already exist...")
	file = Path(db_file)
	if file.exists():
		debug("The database already exists.")
	else:
		debug("Database file does not exist.  Creating the database file . . .")

	# Open the database file
	dbConn = create_db_connection(db_file)
	debug("Creating database cursor.")
	dbCursor = dbConn.cursor()

	# Open the schema description file
	schemaFilepath = Path(db_schema_file)
	if not schemaFilepath.exists():
		debug("The schema description file [" + db_schema_file + "] does not exist.")
		return 1

	debug("Reading the database schema file.")
	with open(db_schema_file, 'r') as fp:
		tables = json.load(fp)
		sql = "CREATE TABLE "
		for table in tables['tables']:
			debug("Building SQL statement to create the table [" + table['table'] + "] . . .")
			sql = "CREATE TABLE IF NOT EXISTS " + table['table'] + " ("
			## print( table['fields'] )
			for field in table['fields']:
				debug("Adding field " + field['name'] + " of type " + field['type'])
				sql = sql + field['name'] + " " + field['type']
				try:
					for constraint in field['constraints']:
						debug(" with constraint " + constraint['constraint'])
						sql = sql + " " + constraint['constraint'] + " "
				except:
					debug("No constraints")

				sql = sql + ","
			sql = sql[:-1] + ")"
			debug("SQL = " + sql)

			try:
				debug("Executing SQL statement:")
				debug("  \"" + sql + "\"")
				dbCursor.execute(sql)
			except NameError as e:
				debug("Table create failed for " + tables['tables'] + " with error:")
				debug(e)
				return 1
	return 0

def load_lookup_tables():
	"""
	Load lookup table in the database

	:return:    exit code
	"""
	
	return 0
	# Open the database file
	dbConn = create_db_connection(db_file)
	dbCursor = dbConn.cursor()

	# Open the lookup table values file
	schemaFilepath = Path(db_lookup_tables)
	if not schemaFilepath.exists():
		debug("The lookup table values file [" + db_lookup_tables + "] does not exist.")
		return 1

	debug("Reading lookup table file.")
	with open(db_lookup_tables, 'r') as fp:
		tables = json.load(fp)

	for lookup_table in tables['lookup-tables']:
		debug("Load values into [" + lookup_table['table'] + "]")
		for row in lookup_table['rows']:
			sql = "INSERT INTO " + lookup_table['table'] + " ("+ row['field'] + ") VALUES (\"" + row['value'] +"\")"

			try:
				debug("Executing SQL statement:")
				debug("  \"" + sql + "\"")
				# dbCursor.execute(sql)
			except NameError as e:
				debug("Inserting into " + tables['tables'] + " failed with an error:")
				debug(e)
				return 1
	dbConn.commit()

	return 0

def main():
	""" Main procedure goes here
	:return: exit code
	"""

	# Initialize the program
	init()

	# Create the database
	if ( create_database() > 0 ):
		debug("Failed to create the database.")
		return 1

	# Load lookup tables
	if ( load_lookup_tables() > 0 ):
		debug("Failed to load lookup tables.")
		return 1

	return 0


if __name__ == '__main__':
	exit(main())