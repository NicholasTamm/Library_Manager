# Library Manager

## Overview
The **Library Manager** is a Python and Jupyter Notebook-based application designed to manage library operations efficiently. The system offers a user-friendly interface to manage library items, events, patrons, and volunteers. Utilizing SQLite for its database backend, the system provides robust support for CRUD operations and transactional processes.

### Key Features:
1. **Library Item Management**
   - Add, borrow, return, and query items in the library.
   - Supports multiple formats, including books, eBooks, CDs, scientific journals, DVDs, and magazines.

2. **Patron and Guest Support**
   - Allows guests to register as patrons through librarian assistance.
   - Both patrons and librarians can query and manage patron activities.

3. **Event Management**
   - Organize library events like book clubs, author meetings, and art shows.
   - Supports event registration and volunteer involvement.

4. **Administrative Utilities**
   - Database initialization and management.
   - Volunteers and librarians can provide assistance, guided by an integrated table and query system.

## Features in Detail

### 1. Main Application (`main.py`)
The application's core functions include borrowing, returning, and managing library items:
- `borrow_item`: Handles borrowing library items, ensuring valid items and availability.
- `return_item`: Allows patrons to return borrowed items and updates the database status.
- `DB_initialize`: Initializes the SQLite database schema (e.g., tables for Items, Fiction, Non-Fiction).

### 2. User Interface Utilities (`UI_utilities.py`)
Contains utility functionality for interacting with the user:
- `print_welcome`: Greets users and guides them to either create a guest or patron account.
- `printTable`: Display database query results for patrons, items, or loans.

### 3. Database Schema Management
Tables managed include:
- **Items**: Store information about library materials.
- **Loan**: Manages borrow and return transactions.
- **Volunteer**: Keeps track of voluntary work done by library patrons.

### 4. Event Features
Register for events categorized by audience types like **Children**, **Adults**, or **Seniors**.

## Programming Languages
- **Jupyter Notebook**: 69.9%
- **Python**: 30.1%

## How to Use:
1. Clone the repository:
    ```bash
    git clone https://github.com/NicholasTamm/Library_Manager.git
    cd Library_Manager
    ```
2. Make sure you have Python installed and install required dependencies.

3. Run the `main.py` file:
    ```bash
    python main.py
    ```

4. Follow the on-screen menu options to interact with the system.

---


## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
