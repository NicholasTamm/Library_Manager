### MOVE TO A myUI FILE ###
def printTable(rows,params=None):
    '''
    Used in order to print header and query results in a Pandas Dataframe like format.
    '''

    # make space
    print("\n" * 3)

    if not rows:
        print("No matching items found")
    else:

        # get the longest with possible in each coulmn
        column_widths = [len(param) for param in params]

        for row in rows:
            for i in range(len(row)):
                column_widths[i] = max(column_widths[i], len(str(row[i])))

        # if given a header then print it out
        if params:
            header = "".join([f"{params[i]:<{column_widths[i] + 8}}" for i in range(len(params))])
            print(f"{'row':<5}" + header)

        # print each row
        for i,row in enumerate(rows):
            rowContent = "".join([f"{row[i]:<{column_widths[i] + 8}}" for i in range(len(row))])
            print(f"{i:<5}" + rowContent)

    print("\n" * 2)

def print_welcome():
    print('''
    Welcome to the Local Library!
    Please enter your PatronId to get full access to library services.\n
    Enter 0 to continue as a guest
    ''')
    print("\n" * 2)
    print("PatronID:")