import os.path
import sqlite3


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
    create_patron = ''' 
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
        dueDate DATE NOT NULL, 
        isReturned INTEGER CHECK (isReturned in (0, 1)), 
        FOREIGN KEY (itemID) REFERENCES Item(ItemID) 
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
            cur.execute(create_patron)
            cur.execute(create_Employee)
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




def find_item(itemID:str = "", title:str = "", authorFirstName:str = "",
              authorLastName:str = "", formatType:str = ""):
    '''
    Find an item in the library
    '''

    # filter out params that are empty string
    filtered_params = {key: value for key, value in locals().items() if value != ""}

    # separate the attributes from their values so that we can append properly into query string
    # attributes = list(filtered_params.keys())
    # values = list(filtered_params.values())

    myQuery = '''
    SELECT * 
    FROM Item I
    WHERE '''

    for i, (attribute, value) in enumerate(filtered_params.items()):
        if i > 0:
            myQuery += " AND "

        myQuery += f"{attribute} = {value}"


    print(myQuery)
    #
    # for i,filter in enumerate(filters):
    #     if filter != "":
    #         if i != 0:
    #             myQuery += " AND "
    #     myQuery += filter
    # print(myQuery)

# TODO: create DB functions
'''
Borrow an item from the library
Return a borrowed item
Donate an item to the library
Find an event in the library
Register for an event in the library
Volunteer for the library
Ask for help from a librarian

'''

def main():
    # initialize DB if it doesnt already exist
    if not os.path.exists('library.db'):
        initialize_db()

    find_item("3001120", "title", "firstName")



if __name__ == "__main__":
    main()

# conn = sqlite3.connect('library.db')
# print("Opened database successfully \n")
# x = True
# while x == True:
#     print("\nSelect your option:\n")
#     print("1 - Borrow an item from the library")
#     print("2 - Return a borrowed item")
#     print("3 - Donate an item to the library")
#     print("4 - Find an event in the library")
#     print("5 - Register for an event in the library")
#     print("6 - Volunteer for the library")
#     print("7 - Ask for help from a librarian")
#     print("x - Close application\n")
#     choice = input('> ')
#
#     if choice == 'x':
#         print("Closing application...")
#         break
#     elif choice == '1':
#         print("bruh")
#     elif choice == '2':
#         print("bruh")
#     elif choice == '3':
#         print("bruh")
#     elif choice == '4':
#         print("bruh")
#     elif choice == '5':
#         print("bruh")
#     elif choice == '6':
#         print("bruh")
#     elif choice == '7':
#         print("bruh")

