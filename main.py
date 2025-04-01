import os.path
import sqlite3
import time
from datetime import date, timedelta
from UI_utilities import printTable, print_welcome, get_user_item_input, print_function_intro

MENU_OPTIONS = '''
Select your option:

1 - Find an item in the library
2 - Borrow an item from the library
3 - Return a borrowed item
4 - Donate an item to the library
5 - Find an event in the library
6 - Register for an event in the library
7 - Volunteer for the library
8 - Ask for help from a librarian
x - Close application
'''

OPTIONS_5 = '''
Select your option for the targeted audience:

1. Children
2. Adults
3. Seniors
4. Everyone
5. All events

'''

OPTIONS_8 = '''
Please select what kind of assistance you require:

'''

itemsAttributes = ['itemID', 'Title', 'Author First Name', 'Author Last Name', 'Format', 'isBorrowed', 'isAdded']


def checkPatronIDValid(PatronID: int) -> bool:
    myQuery = '''
    SELECT COUNT(*)
    FROM Patron
    WHERE patronID = ?'''

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(myQuery, (PatronID,))
            rows = cur.fetchall()

            match (rows[0][0]):
                case 0:
                    print("Not a valid patronID!")
                    return False
                case 1:
                    print("valid id")
                    return True
                case _:
                    for row in rows:
                        print(row)
                    print("more than one PatronID!")
                    return False


        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")
            exit(1)


def query_patron_loans(PatronId: str):
    '''
    helper function to query the loan table under the current patronID logged in to the system.
    '''
    # query that will be executed
    loanQuery = '''
    SELECT loanID, itemID, dueDate
    FROM Loan
    WHERE patronID = ? AND isReturned  = 0'''

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(loanQuery, (PatronId,))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def DB_initialize():
    '''
    - takes in a connection and creates all tables
    - should read in data from a csv file
    '''

    # sql queries to create tables
    create_Item = '''
    CREATE TABLE Item (
	    itemID INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL CHECK (LENGTH(title) <= 255),
        authorFirstName TEXT CHECK (LENGTH(authorFirstName) <= 50), 
        authorLastName TEXT CHECK (LENGTH(authorLastName) <= 100), 
        format TEXT CHECK (format IN ('Book', 'eBook', 'CD', 'scientific journal', 'record', 'DVD', 'Blu ray', 'magazine')),
        isBorrowed INTEGER CHECK (isBorrowed IN (0, 1)),
        isAdded INTEGER CHECK (isAdded IN (0, 1))
        
    );
    '''
    create_Fiction = '''
    CREATE TABLE Fiction (
    	itemID INTEGER PRIMARY KEY, 
    	cutter CHAR(3) CHECK (LENGTH(cutter) = 3),
    	FOREIGN KEY(itemID) REFERENCES Item(itemID) ON DELETE CASCADE
    );
    '''
    create_NonFiction = '''
    CREATE TABLE NonFiction (
	    itemID INTEGER PRIMARY KEY,
	    callNum REAL CHECK (callNum < 1000 AND callNum * 10000 = CAST(callNum * 10000 AS INTEGER)), 
	    cutter CHAR(3) CHECK (LENGTH(cutter) = 3),
	    FOREIGN KEY(itemID) REFERENCES Item(itemID) ON DELETE CASCADE
    );
    '''
    create_Patron = ''' 
    CREATE TABLE Patron (
    	patronID INTEGER PRIMARY KEY AUTOINCREMENT,
    	firstName TEXT CHECK (LENGTH(firstName) <= 50), 
    	lastName TEXT CHECK (LENGTH(lastName) <= 100)
    ); 
    '''
    create_Employee = '''
    CREATE TABLE Employee (
    	employeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    	firstName TEXT CHECK (LENGTH(firstName) <= 50), 
    	lastName TEXT CHECK (LENGTH(lastName) <= 100), 
    	position TEXT, 
    	salary INTEGER
    ); 
    '''
    create_EmployeeEmail = '''

    CREATE TABLE EmployeeEmail (
        employeeID INTEGER PRIMARY KEY,
        email TEXT
    );

    '''
    create_Volunteer = ''' 
    CREATE TABLE Volunteer (
        volunteerID INTEGER PRIMARY KEY AUTOINCREMENT, 
        firstName TEXT CHECK (LENGTH(firstName) <= 50),
        lastName TEXT CHECK (LENGTH(lastName) <= 100)
    );
    '''
    create_Event = ''' 
    CREATE TABLE Event (
        eventID INTEGER PRIMARY KEY AUTOINCREMENT, 
        eventName TEXT NOT NULL,
        hostID INTEGER NOT NULL, 
        type TEXT CHECK (type IN ('Book Club', 'Author Event', 'Art Show', 'Movie', 'Other')), 
        advisedFor TEXT CHECK (LENGTH(advisedFor) <= 100),
        roomNumber INTEGER CHECK (roomNumber IN (101, 102, 120, 127, 131, 135)), 
        date DATE NOT NULL, 
        time TIME NOT NULL,
        FOREIGN KEY (hostID) REFERENCES Employee(employeeID)
    ); 
    '''
    create_Loan = ''' 
    CREATE TABLE Loan (
        loanID INTEGER PRIMARY KEY AUTOINCREMENT, 
        itemID INTEGER NOT NULL, 
        patronID INTEGER NOT NULL,
        dueDate DATE NOT NULL, 
        isReturned INTEGER CHECK (isReturned in (0, 1)), 
        FOREIGN KEY (itemID) REFERENCES Item(itemID),
        FOREIGN KEY (patronID) REFERENCES Patron(patronID)
    ); 
    '''
    create_Fine = ''' 
    CREATE TABLE Fine(
        fineID INTEGER PRIMARY KEY, 
        loanID INTEGER NOT NULL,
        fineType TEXT NOT NULL CHECK (fineType IN ('Overdue', 'Damaged')), 
        amount INTEGER, 
        isPaid INTEGER CHECK (isPaid in (0, 1)),
        FOREIGN KEY (loanID) REFERENCES Loan(loanID) 
    );
    '''
    create_Attending = ''' 
    CREATE TABLE Attending (
        eventID INTEGER, 
        patronID INTEGER, 
        PRIMARY KEY (eventID, patronID),
        FOREIGN KEY (eventID) REFERENCES Event(eventID),
        FOREIGN KEY (patronID) REFERENCES Patron(patronID)
    );
    '''
    create_Event_Volunteer = ''' 
        CREATE TABLE Event_Volunteer(
        eventID INTEGER, 
        volunteerID INTEGER, 
        PRIMARY KEY (eventID, volunteerID),
        FOREIGN KEY (eventID) REFERENCES Event(eventID),
        FOREIGN KEY (volunteerID) REFERENCES Volunteer(volunteerID)
    );
    '''

    # create connection and get cursor to try and create tables
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(create_Item)
            cur.execute(create_Fiction)
            cur.execute(create_NonFiction)
            cur.execute(create_Patron)
            cur.execute(create_Employee)
            cur.execute(create_EmployeeEmail)
            cur.execute(create_Volunteer)
            cur.execute(create_Event)
            cur.execute(create_Loan)
            cur.execute(create_Fine)
            cur.execute(create_Attending)
            cur.execute(create_Event_Volunteer)
            conn.commit()
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")

    # TODO: implement csv reading capabillity


def DB_find_item(itemID: str = "", title: str = "", authorFirstName: str = "",
                 authorLastName: str = "", format: str = "", isBorrowed: int = ""):
    '''
    Find an item in the library
    '''

    # filter out params that are empty string
    filtered_params = {key: value for key, value in locals().items() if value != ""}

    # separate the attributes from their values so that we can append properly into query string
    # attributes = list(filtered_params.keys())
    # values = list(filtered_params.values())

    FindItemQuery = '''
    SELECT * 
    FROM Item I 
    WHERE 
    '''

    # special if function called with no params print all
    if not filtered_params:
        FindItemQuery = '''
        SELECT *
        FROM Item'''

    for i, (attribute, value) in enumerate(filtered_params.items()):
        if i > 0:
            FindItemQuery += " AND "

        if attribute == "itemID":
            FindItemQuery += f"{attribute}={value}"
        else:
            FindItemQuery += f"{attribute}='{value}'"

    ### TODO: test the execution of the query
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(FindItemQuery)
            rows = cur.fetchall()
            return rows

        # debugging purposes
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def DB_return_item(loanID: int):
    '''
    Drops row from loan relation. Update corresponding Item record isBorrowed to 0.

    '''

    # query strings
    loanQuery = '''
    Select itemID
    FROM Loan
    WHERE loanID = ?
    '''

    UpdateItemQuery = '''
    UPDATE Item
    SET isBorrowed = 0
    WHERE itemID = ?
    '''

    UpdateLoanQuery = '''
    UPDATE Loan
    SET isReturned = 1
    WHERE loanID = ? AND itemID = ?
    '''

    # open connections
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            # find the desired loan
            cur.execute(loanQuery, (loanID,))
            rows = cur.fetchall()

            # shouldn't be possible but for debug purpose
            if len(rows) != 1:
                print("ERROR ENCOUNTER MORE THAN ONE ITEM WITH CORRESPONDING ITEMID")
            else:
                itemID = rows[0][0]
                cur.execute(UpdateItemQuery, (itemID,))
                cur.execute(UpdateLoanQuery, (loanID, itemID))
                conn.commit()

        # debugging purposes
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def DB_borrow_item(itemID: str, patronID: str):
    borrowQuery = '''
    UPDATE Item
    SET isBorrowed = 1
    WHERE itemID = ?'''

    loanQuery = '''
    INSERT INTO Loan (itemID, patronID, dueDate, isReturned)
    VALUES (?, ?, ?, 0)'''

    duedate = date.today() + timedelta(days=14)

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(borrowQuery, (itemID,))
            cur.execute(loanQuery, (itemID, patronID, duedate.strftime("%Y-%m-%d")))
            conn.commit()


        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")
            exit(1)


def DB_add_item(title: str = "", authorFirstName: str = "",
                authorLastName: str = "", format: str = ""):
    # query
    insertQuery = '''
    INSERT INTO item (title, authorFirstName, authorLastName, format, isBorrowed, isAdded)
    VALUES (?, ?, ?, ?, 0, 0)'''

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(insertQuery, (title, authorFirstName, authorLastName, format))
            conn.commit()
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def find_event(recommended):
    myQuery = '''
    SELECT eventID, eventName, type, advisedFor, roomNumber, date, time 
    FROM Event
    '''

    match recommended:
        case '1':
            myQuery += " WHERE advisedFor = 'Children'"
        case '2':
            myQuery += " WHERE advisedFor = 'Adults'"
        case '3':
            myQuery += " WHERE advisedFor = 'Seniors'"
        case '4':
            myQuery += " WHERE advisedFor = 'Everyone'"
        case '5':
            pass
        case _:
            print(f"You entered {recommended}, please enter a valid menu option")
            return  # exit function early if input is invalid

    with sqlite3.connect("library.db") as conn:
        try:
            cur = conn.cursor()
            cur.execute(myQuery)
            rows = cur.fetchall()
            for eventID, eventName, type, advisedFor, roomNumber, date, time in rows:
                print(
                    f"{eventID}. {eventName} | {type} | Recommended audience: {advisedFor} | Room {roomNumber} | {date} {time}")
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def register_event(currentPatron):
    myQuery = '''
    SELECT eventID, eventName, type, advisedFor, roomNumber, date, time 
    FROM Event
    '''
    with sqlite3.connect("library.db") as conn:
        try:
            cur = conn.cursor()
            cur.execute(myQuery)
            rows = cur.fetchall()
            for eventID, eventName, type, advisedFor, roomNumber, date, time in rows:
                print(
                    f"{eventID}. {eventName} | {type} | Recommended audience: {advisedFor} | Room {roomNumber} | {date} {time}")
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")

    print('\n' * 2)
    print("Select which event you want to register for\n")
    choice = input('> ')
    myQuery = '''
    INSERT INTO Attending (eventID, patronID) VALUES (
        :event, :patron
    );
    '''
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(myQuery, {'event': choice, 'patron': currentPatron})
            conn.commit()
            cur.execute("SELECT * FROM Attending WHERE patronID = ?", (currentPatron,))
            print(cur.fetchall())

        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def librarian_help():
    myQuery = '''
    SELECT E1.firstName, E1.lastName, E2.email 
    FROM Employee E1 JOIN EmployeeEmail E2 ON E1.employeeID = E2.employeeID
    WHERE E1.position = 'Librarian'; 
    '''
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:

            cur.execute(myQuery)
            rows = cur.fetchall()
            for first, last, email in rows:
                print(f"{first} {last} | {email}")
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


# TODO: create DB functions
'''
Borrow an item from the library
Return a borrowed item
Donate an item to the library
Find an event in the library
Register for an event in the library
Volunteer for the library
Ask for help from a librarian
    - implement ticketing system
    - allow user to register as Patron

'''


def runUI():
    # check if current user is a patron or just going to volunteer
    # grab the patronID which will be used for operations such as borrowing, returning, etc.
    print_welcome()

    currentPatron = input("> ")
    while not currentPatron.isdigit():
        print("\n" * 4)
        print(f"{currentPatron} is INVALID....PatronID must be a number!")
        print("If you do not have a PatronID, enter 0 to continue as a guest with limited functionality.")
        print("\n" * 2)
        print("PatronID:")

        currentPatron = input("> ")

    # confirm that user is a patron
    isPatron = checkPatronIDValid(int(currentPatron))

    while True:
        print(MENU_OPTIONS)
        choice = input('> ')

        match choice.lower():
            case '1':
                print('\n' * 5)
                print('-' * 30)

                print(OPTION_INTRO.format("FIND AN ITEM: "))
                print("Enter 'p' into any to print entire items catalogue")

                # list to record all of the parameters to feed into function
                userInput = get_user_item_input()
                itemsRows = []

                # check for illegal cases
                if userInput == [] or all(entry == "" for entry in userInput):
                    print("Must enter at least one parameter!")
                    pass
                elif 'p' in userInput:
                    itemsRows = DB_find_item()
                else:
                    itemsRows = DB_find_item(*userInput)

                if itemsRows:
                    printTable(itemsRows, itemsAttributes)
                else:
                    print("\n" * 5 + "No items found!")
                input('Returning to main menu..Press enter to return...')
            case '2':
                print('\n' * 5)
                print('-' * 30)
                print(OPTION_INTRO.format(" BORROW AN ITEM: "))

                # list to record all of the parameters to feed into function
                userInput = get_user_item_input()

                # check for illegal cases
                if userInput == [] or all(entry == "" for entry in userInput):
                    print("Must enter at least one parameter!")
                else:
                    itemsRows = DB_find_item(*userInput, isBorrowed=0)
                    if itemsRows:
                        printTable(itemsRows, itemsAttributes)

                        # ask user which they want to Borrow
                        print("\n" * 2)
                        print("Enter row number of item you wish to Borrow:")
                        print("Enter 'X' to abort")
                        while True:
                            inputToBorrow = input("> ")
                            if inputToBorrow.isdigit():
                                if int(inputToBorrow) in range(len(itemsRows)):
                                    itemID_to_Borrow = itemsRows[int(inputToBorrow)][0]
                                    DB_borrow_item(itemID_to_Borrow, currentPatron)
                                    print("Your item was successfully borrowed!")
                                    break
                                else:
                                    printTable(itemsRows, itemsAttributes)
                                    print("Enter 'X' to abort")
                                    print("Invalid input! row not in range.")
                            elif inputToBorrow.lower() == 'x':
                                break
                            else:
                                print("Invalid input! Must be a number or 'X' to abort.")
                    else:
                        print("\n" * 5 + "No items found! Please ensure book is not borrowed already!")
                    input("Returning to main menu..Press enter to return...")

            case '3':

                # ensure user is patron
                if not isPatron:
                    input("Sorry this is a patron only function...Press enter to return...")
                    pass

                # case 3 functionality
                else:
                    print('\n' * 5)
                    print('-' * 30)
                    print(f'''
                    RETURN MENU:\n
                    Patron: {currentPatron}
                    ''')
                    loan_list = query_patron_loans(currentPatron)

                    # if patron has no active loans
                    if len(loan_list) == 0:
                        print("You have nothing to return!\n"
                              "Back to Main Menu...")
                        input("Press enter to continue...")

                    # patron has active loans
                    else:
                        printTable(loan_list, ['loanID', 'itemID', 'dueDate'])

                        # ask user which they want to return
                        print("\n" * 2)
                        print("Enter row number of loan you wish to return:")
                        print("Enter 'X' to abort")
                        toReturn = input("> ")
                        if toReturn.isdigit():
                            if int(toReturn) in range(len(loan_list)):
                                loanID_to_return = loan_list[int(toReturn)][0]

                                # return item
                                DB_return_item(loanID_to_return)
                                print("Your item was successfully returned!")
                        elif toReturn.lower() == 'x':
                            pass
                        else:
                            print("Invalid input! Number either not INT or out of range.")
                        input("Returning to main menu..Press enter to return...")

            case '4':
                print(OPTION_INTRO.format("DONATE A BOOK: "))

            case '5':
                print('\n' * 5)
                print('-' * 30)
                print("Please select what kind of events you looking for:\n")
                print(OPTIONS_5)
                choice = input('> ')
                find_event(choice)
                input('press enter to continute...')
            case '6':
                print('\n' * 5)
                print('-' * 30)
                register_event(currentPatron)
                input('press enter to continute...')
            case '7':
                print("not available yet")
            case '8':
                print('\n' * 5)
                print('-' * 30)
                print("Here are the emails of our Librarians. Please contact them for any inquries.")
                librarian_help()
                input('press enter to continute...')

            case 'x':
                print("Closing application...")
                break
            case 'p':

                print("Connecting to library.db and printing all table contents...\n")

                with sqlite3.connect("library.db") as conn:
                    cur = conn.cursor()

                    # Get all user-defined table names
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                    tables = [row[0] for row in cur.fetchall()]

                    for table in tables:
                        print(f"\n--- {table} ---")
                        try:
                            cur.execute(f"SELECT * FROM {table}")
                            rows = cur.fetchall()
                            for row in rows:
                                print(row)
                            if not rows:
                                print("(No rows)")
                        except sqlite3.Error as e:
                            print(f"Error reading table {table}: {e}")

                input("\nDone. Press enter to continue...")
            case _:
                print(f"You entered {choice}, please enter a valid number corresponding to a menu option")

        # time.sleep(1)
        print('\n' * 10)


def main():
    # initialize DB if it doesnt already exist
    if not os.path.exists('library.db'):
        DB_initialize()

    runUI()


if __name__ == "__main__":
    main()
