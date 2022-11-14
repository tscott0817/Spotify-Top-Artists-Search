import csv
import sqlite3
from sqlite3 import Error
from enum import Enum
from pathlib import Path

""" 
This program allows the user to search to some top songs on the Spotify
charts and their associated artists.
 """


def main():
    print("\n")
    print("Welcome to our database querying program.\n"
          "If you don't have a database loaded please enter 'load data'.\n"
          "If you know the query language for the database then you are all set.\n"
          "Otherwise, type 'help' once the database is loaded.\n")

    running = True
    while running:
        user_input = input()  # Ask for user input

        # Only allows to continue if database exists
        if not (data_loaded()) and user_input != Commands.load_data:  # (i.e. it's the first user input)
            print("Data not yet loaded, please enter \"load data\" command")  # print error message for user
        elif user_input == Commands.exit:
            running = False
        elif user_input == Commands.help:
            help_query()
        elif user_input == Commands.load_data:
            load_data()
        else:
            queries(user_input)


# The function to be called on first run of program
# Mostly from sqlite documentation
def load_data():
    # Connect to db, automatically created if doesn't exist
    connection = sqlite3.connect('songs_artists.db')
    cursor = connection.cursor()

    # If table exists already, replace with table of same name
    cursor.execute("DROP TABLE IF EXISTS Songs")
    create_table_songs = '''CREATE TABLE IF NOT EXISTS Songs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    streams TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    artist_name VARCHAR(50) NOT NULL,
                    FOREIGN KEY(artist_name) REFERENCES artists(artist));
                    '''

    # Puts songs table in database
    cursor.execute(create_table_songs)
    file = open('songs.csv')
    content_songs = csv.reader(file)

    # Skips first line of csv file to ignore header
    next(content_songs)
    insert_records = "INSERT INTO songs (title, streams, release_date, duration, artist_name) VALUES(?, ?, ?, ?, ?)"

    # Putting file contents into table
    cursor.executemany(insert_records, content_songs)

    # Print out songs table
    select_all = "SELECT * FROM songs"
    rows = cursor.execute(select_all).fetchall()
    print("Songs Table")
    for r in rows:
        print(r)
    print("\n")

    # If table exists already, replace with table of same name
    cursor.execute("DROP TABLE IF EXISTS Artists")
    create_table_artist = '''CREATE TABLE IF NOT EXISTS Artists(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist VARCHAR(50) NOT NULL,
                    yrs_in_industry INTEGER NOT NULL,
                    hometown VARCHAR(20) NOT NULL,
                    albums INTEGER NOT NULL,
                    top_song VARCHAR(70) NOT NULL);
                    '''
    # Put artists table in database
    cursor.execute(create_table_artist)
    file_artist = open('artists.csv')
    contents_artists = csv.reader(file_artist)

    # Skips first line of csv file to ignore header
    next(contents_artists)
    insert_artist = "INSERT INTO artists (artist, yrs_in_industry, hometown, albums, top_song) VALUES(?, ?, ?, ?, ?)"
    cursor.executemany(insert_artist, contents_artists)

    # Print out artists table
    select_all_artist = "SELECT * FROM artists"
    rows = cursor.execute(select_all_artist).fetchall()
    print("Artists Table")
    for r in rows:
        print(r)
    print("\n")

    # Finish and close db connection
    connection.commit()
    connection.close()


# Checks to make sure that the data has been loaded
# Returns true if database exists, false otherwise
def data_loaded():
    my_file = Path("songs_artists.db")
    if my_file.is_file():
        is_loaded = True
    else:
        is_loaded = False

    return is_loaded


# Commands outside of searchable query language
class Commands(str, Enum):
    load_data = 'load data',
    help = 'help',
    exit = 'exit',
    single = 'single',
    join = 'join',
    meta_songs = 'how many songs',
    meta_artists = 'how many artists'


# The possible keywords the user can search
def query_language():
    # First letter capital = Table
    language_list = ['load data', 'Artist', 'Song', 'yrs_in_industry', 'hometown', 'albums', 'top_song',
                     'streams', 'release', 'duration', 'artist_name', 'help', 'exit', 'single',
                     'join', 'how', 'may', 'songs', 'artists']

    return language_list


# Is this a single table or join search
def check_query_type(user_input_list):
    # Single search if input list is length 3 or join if 5
    single_size = 3
    join_size = 5

    if len(user_input_list) == single_size:
        return "single"
    elif len(user_input_list) == join_size:
        return "join"
    else:
        print("It seems you've entered an invalid query structure.")
        print("Please enter a valid type of query or type 'help' for more.")
        print("\n")


# Check if keywords are in language
def check_keywords(user_input, language_list):
    # Possible searches will either have 2 or 3 keywords (and 1 or 2 elements)
    # Count number of keywords entered to verify the search is allowed
    keyword_itr = 0
    for string in user_input.split():
        if string in language_list:
            keyword_itr += 1

    if keyword_itr == 0:
        print("It looks like no known keyword have been entered!")
        print("Please try again or type 'help' for more.")
        print("\n")
        rtn = False
    elif keyword_itr == 2 or keyword_itr == 4:
        rtn = True
    else:
        print("It seems you've entered and unacceptable number of keywords")
        print("Please try again or type 'help' for more.")
        print("\n")
        rtn = False

    return rtn


# Handles the user input to pass to db for searching
def queries(user_input):
    # The keywords that are allowed to be entered
    language_list = query_language()

    # Each word of the user_input as a list element
    holding_word = ''
    parsed_string = []
    in_quote = False

    # Performs a check for quotation marks
    for element in user_input:  # loop through each character of the string user_input
        if element == '"':
            if in_quote:  # already hit first " so this is the closing one
                parsed_string.append(holding_word)  # add word to list
                holding_word = ''  # reset holding word after adding to list
                in_quote = False  # not in "" anymore
            else:  # first " so everything up to next " should be included
                in_quote = True

        elif element == ' ':  # element is space
            if in_quote:  # if we're in middle of "" ignore space
                holding_word = holding_word + element  # continue adding char to word
            elif holding_word != '':  # not in middle of "" and haven't reset holding_word add to parsed_string
                parsed_string.append(holding_word)
                holding_word = ''  # reset holding word after added to list
        else:
            holding_word = holding_word + element  # add char to holding_word
    if holding_word != '':  # if holding_word isn't empty add to list
        parsed_string.append(holding_word)

    # For metadata
    if user_input == Commands.meta_songs:
        data_string = query_data_interface(parsed_string, 'meta_songs')
        print(data_string)
        print("\n")
    elif user_input == Commands.meta_artists:
        data_string = query_data_interface(parsed_string, 'meta_artists')
        print(data_string)
        print("\n")
    # If keywords are in language, check which type of query it is
    elif check_keywords(user_input, language_list):
        if check_query_type(parsed_string) == Commands.single:
            data_string = query_data_interface(parsed_string, check_query_type(parsed_string))
            print(data_string)
            print("\n")
        elif check_query_type(parsed_string) == Commands.join:
            data_string = query_data_interface(parsed_string, check_query_type(parsed_string))
            print(data_string)
            print("\n")
    # else:
    #     print("Invalid Query. Please try again or type 'help' for more.")


def help_query():
    print("To properly query the database please search using the following form: COLUMN TABLE ELEMENT")
    print(
        "Valid query example: years Artist artistName, where artistName might be Queen or \"Shawn Mendes\". Use quotes if more than one word")
    print("Valid keywords for Artist table: Artist, top_song, years_in_industry, hometown, albums")
    print("Valid keywords for Song table: Song, artist_name, duration, streams, release")
    print('To do a join search between the two tables type: artist_name Song "the song title" Artist yrs_in_industry')
    print("To gather some metadata about each table type : how many songs, how many artists")
    print("You can also execute these non-language commands: load data, help, exit")


""" 
 Interface between the parsing and database. 
 Retrieves appropriate data from db and returns it as a string
 
 @param list query_data_list: A list of the parsed user input
 @param str query_type: If it is a single table search, join, or metadata
 
 """


def query_data_interface(query_data_list, query_type):
    # Search by query type
    if query_type == 'single':
        return_string = single_search(query_data_list[0], query_data_list[1], query_data_list[2])
    elif query_type == 'join':
        return_string = join_search(query_data_list[0], query_data_list[1], query_data_list[2], query_data_list[3],
                                    query_data_list[4])
    elif query_type == 'meta_songs':
        return_string = meta_songs()
    elif query_type == 'meta_artists':
        return_string = meta_artists()
    return return_string


# Database connection
# From sqlite docs for error handling
def create_connection(database):
    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)

    return conn


# Function to return total songs in table
def meta_songs():
    # Connect to database
    database = "songs_artists.db"
    conn = create_connection(database)
    db_cursor = conn.cursor()  # For passing database searching

    songs_count = db_cursor.execute("SELECT COUNT(*) FROM songs")

    return_data = songs_count.fetchone()[0]
    return return_data


# Function to return total artists in table
def meta_artists():
    # Connect to database
    database = "songs_artists.db"
    conn = create_connection(database)
    db_cursor = conn.cursor()  # For passing database searching

    artists_count = db_cursor.execute("SELECT COUNT(*) FROM artists")

    return_data = artists_count.fetchone()[0]
    return return_data


# A possible setup for querying
def single_search(column, table, element):
    # Connect to database
    database = "songs_artists.db"
    conn = create_connection(database)
    db_cursor = conn.cursor()  # For passing database searching

    # If table names exist, check columns
    if table == 'Song':
        # If any column names exist, return the
        if column == 'streams':
            element_string = db_cursor.execute("SELECT streams FROM songs WHERE title = ?", (element,)).fetchall()
        elif column == 'release':
            element_string = db_cursor.execute("SELECT release_date FROM songs WHERE title = ?", (element,)).fetchall()
        elif column == 'duration':
            element_string = db_cursor.execute("SELECT duration FROM songs WHERE title = ?", (element,)).fetchall()
        elif column == 'artist_name':
            element_string = db_cursor.execute("SELECT artist_name FROM songs WHERE title = ?", (element,)).fetchall()
        # If column name does not exist, return error message
        else:
            element_string = "That column name does not exist. Type 'help' for more."
            return_data = element_string
            return return_data

    elif table == 'Artist':
        if column == 'hometown' or column == 'home':
            element_string = db_cursor.execute("SELECT hometown FROM artists WHERE artist = ?", (element,)).fetchall()
        elif column == 'albums':
            element_string = db_cursor.execute("SELECT albums FROM artists WHERE artist = ?", (element,)).fetchall()
        elif column == 'yrs_in_industry' or column == 'years':
            element_string = db_cursor.execute("SELECT yrs_in_industry FROM artists WHERE artist = ?",
                                               (element,)).fetchall()
        elif column == 'top_song':
            element_string = db_cursor.execute("SELECT top_song FROM artists WHERE artist = ?", (element,)).fetchall()
        else:
            element_string = "That column name does not exist. Type 'help' for more."
            return_data = element_string
            return return_data
    # If table name does not exist, return error message
    else:
        element_string = "That table does not exist. Type 'help' for more."
        return_data = element_string
        return return_data

    # If table name does exist return element from column
    try:
        return_data = element_string[0][0]
    except:
        return_data = "That element does not exist. Type 'help' for more."
    return return_data


# Function to join two tables and retrieve data
# Returns the number of years that the artist who made song 'x' has been a musician.
def join_search(column1, table1, element1, table2, column2):
    # Connect to database
    database = "songs_artists.db"
    conn = create_connection(database)
    db_cursor = conn.cursor()  # For passing database searching

    # Joins tables to find artist years in industry based on song title
    if table1 == "Song" and table2 == "Artist":
        if column1 == "artist_name" and column2 == "yrs_in_industry":
            element_string = db_cursor.execute("SELECT artists.yrs_in_industry FROM\
                artists INNER JOIN songs ON artists.Artist = songs.artist_name\
                    WHERE songs.title = ?", (element1,)).fetchall()
    else:
        element_string = "Those tables do not exist. Type 'help' for more."
        return_data = element_string
        return return_data

    # Error handling for invalid return from query
    try:
        return_data = element_string[0][0]
    except:
        return_data = "Something went wrong with retrieving your multi-table query. Type 'help' for more."

    return return_data


if __name__ == "__main__":
    main()
