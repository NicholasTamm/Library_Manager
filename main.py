import os.path
import sqlite3
import time

MENU_OPTIONS = '''
Select your option:

1 - Borrow an item from the library
2 - Return a borrowed item
3 - Donate an item to the library
4 - Find an event in the library
5 - Register for an event in the library
6 - Volunteer for the library
7 - Ask for help from a librarian
x - Close application
'''

FIND_ITEM_MENU_INPUTS = [
    'ItemID: ',
    'Title: ',
    'author\'s first name: ',
    'author\'s last name: ',
    'format: '
]

OPTIONS_7 = '''
Please select what kind of assistance you require:

'''
def cheeckPatronIDValid(PatronID: int)->bool:
    myQuery = '''
    SELECT COUNT(*)
    FROM Patron
    WHERE patronID = ?'''

    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(myQuery, (PatronID,))
            rows = cur.fetchall()


            match(rows[0][0]):
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


def initialize_db():
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

def find_item(itemID: str = "", title: str = "", authorFirstName: str = "",
              authorLastName: str = "", format: str = ""):
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

    for i, (attribute, value) in enumerate(filtered_params.items()):
        if i > 0:
            FindItemQuery += " AND "

        if attribute == "itemID":
            FindItemQuery += f"{attribute}={value}"
        else:
            FindItemQuery += f"{attribute}='{value}'"

    print(FindItemQuery)
    ### TODO: test the execution of the query
    with sqlite3.connect("library.db") as conn:
        cur = conn.cursor()
        try:
            cur.execute(FindItemQuery)
            rows = cur.fetchall()

            if not rows:
                print("No matching items found")
            else:
                print(f"{'itemID':<8}{'Title':<30}{'Author First Name':<20}{'Author Last Name':<20}{'Format':<10}{'isBorrowed':<12}{'isAdded':<8}")
                for row in rows:
                    print(f"{row[0]:<8}{row[1]:<30}{row[2]:<20}{row[3]:<20}{row[4]:<10}{row[5]:<12}{row[6]:<8}")

        # debugging purposes
        except sqlite3.Error as e:
            print(f"sqlite encountered error: {e}")


def return_item(loanID: int):
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


# TODO: Helper func: takes in a userPatronID and lists all the loans currently under Patron. Asks which one they want to return.
### MOVE TO A UI FILE ###
def query_patron_loans(PatronId: str):

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

def librarian_help():
    myQuery = '''
    SELECT E1.firstName, E1.lastName, E2.email 
    FROM Employee E1 JOIN EmployeeEmail E2 ON E1.employeeID = E2.employeeID
    WHERE E1.position = 'Librarian'; 
    '''
    with sqlite3.connect("library.db") as conn:
        try:
            cur = conn.cursor()
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
    print('''
    Welcome to the Local Library!
    Please enter your PatronId to get full access to library services.\n
    If you are looking to volunteer, donate items, find event, or register as patron, enter 0 to continue
    ''')
    print("\n" * 4)
    print("PatronID:")

    currentPatron = input("> ")

    # TODO: implement current patron usage

    while True:
        print(MENU_OPTIONS)
        choice = input('> ')

        match choice.lower():
            case '1':
                print('\n' * 5)
                print('-' * 30)
                print('''Press enter if unknown or you want to skip.
                Enter "x" to skip the current and rest of the prompts (cannot use on itemID).''')

                # list to record all of the parameters to feed into function
                params = []

                for option in FIND_ITEM_MENU_INPUTS:
                    # print out each filter option and get the input
                    print(option)
                    find_input = input("> ")
                    # if the input is x break the loop
                    if find_input.lower() == 'x':
                        break
                    params.append(find_input)

                # check for illegal cases
                if params == [] or all(params == "" for i in params):
                    print("Must enter at least one parameter!")
                    pass
                else:
                    find_item(*params)
                    input('Returning to main menu..Press enter to return...')

            case '2':

                # ensure user is patron
                if not cheeckPatronIDValid(int(currentPatron)):
                    input("Sorry this is a patron only function...Press enter to return...")
                    pass

                # case 2 functionality
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
                        print(f'''{'row':<5}{'loanID':<8}{'itemID':<8}{'dueDate':<20}''')
                        for i, row in enumerate(loan_list):
                            print(f"{i + 1:<5}{row[0]:<8}{row[1]:<8}{row[2]:<20}")

                        # ask user which they want to return
                        print("Enter row number of loan you wish to return:")
                        toReturn = int(input("> ")) -1
                        loanID_to_return = loan_list[toReturn][0]

                        # return item
                        return_item(loanID_to_return)
                        print("Your item was successfully returned!")
                        input("Returning to main menu..Press enter to return...")


            case '3':
                print("not available yet")
            case '4':
                print("not available yet")
            case '5':
                print("not available yet")
            case '6':
                print("not available yet")
            case '7':
                print('\n' * 5)
                print('-' * 30)
                print("Here are the emails of our Librarians. Please contact them for any inquries.")
                librarian_help()
                input('press enter to continute...')

            case 'x':
                print("Closing application...")
                break
            case 'p':
                import sqlite3

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
                print(f"You entered {choice}, please enter a valid menu option")

        # time.sleep(2)
        print('\n' * 10)



def main():
    # initialize DB if it doesnt already exist
    if not os.path.exists('library.db'):
        initialize_db()

    runUI()



if __name__ == "__main__":
    main()
