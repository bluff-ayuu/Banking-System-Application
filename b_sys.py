import mysql.connector
import random
import string
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
)
cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
cursor.execute("USE banking_system")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        account_number VARCHAR(10) PRIMARY KEY,
        name VARCHAR(255),
        dob DATE,
        city VARCHAR(255),
        balance FLOAT,
        contact_number VARCHAR(10),
        email_id VARCHAR(255),
        address TEXT,
        status ENUM('active', 'inactive') DEFAULT 'active'
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS login (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_number VARCHAR(10),
        password VARCHAR(255),
        last_login TIMESTAMP DEFAULT NULL,
        FOREIGN KEY (account_number) REFERENCES users(account_number)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_number VARCHAR(10),
        type ENUM('credit', 'debit', 'transfer', 'received'),
        amount FLOAT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_number) REFERENCES users(account_number)
    )
""")

def is_valid_email(email):
    return "@" in email and "." in email and len(email) > 5

def is_valid_password(password):
    return (
        len(password) >= 8 and
        any(char.isupper() for char in password) and
        any(char.islower() for char in password) and
        any(char.isdigit() for char in password) and
        any(char in string.punctuation for char in password)
    )

def is_valid_contact(contact):
    return contact.isdigit() and len(contact) == 10

def generate_account_number():
    while True:
        account_number = str(random.randint(10**9, 10**10 - 1))
        cursor.execute("SELECT * FROM users WHERE account_number = %s", (account_number,))
        if not cursor.fetchone():
            return account_number

def add_user():
    print("=== Add User ===")
    name = input("Name: ").strip()
    dob = input("Date of Birth (YYYY-MM-DD): ").strip()
    city = input("City: ").strip()
    password = input("Password: ").strip()
    if not is_valid_password(password):
        print("Invalid password. Password must be at least 8 characters, with upper, lower, digit, and special character.")
        return
    initial_balance = float(input("Initial Balance (Min 2000): ").strip())
    if initial_balance < 2000:
        print("Initial balance must be at least 2000.")
        return
    contact_number = input("Contact Number (10 digits): ").strip()
    if not is_valid_contact(contact_number):
        print("Invalid contact number.")
        return
    email_id = input("Email ID: ").strip()
    if not is_valid_email(email_id):
        print("Invalid email address.")
        return
    address = input("Address: ").strip()

    account_number = generate_account_number()
    cursor.execute("""
        INSERT INTO users (account_number, name, dob, city, balance, contact_number, email_id, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (account_number, name, dob, city, initial_balance, contact_number, email_id, address))
    cursor.execute("""
        INSERT INTO login (account_number, password) VALUES (%s, %s)
    """, (account_number, password))
    db.commit()
    print(f"User added successfully! Account Number: {account_number}")

def show_users():
    print("=== Show Users ===")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"""
        Account Number: {user[0]}
        Name: {user[1]}
        DOB: {user[2]}
        City: {user[3]}
        Balance: {user[4]}
        Contact Number: {user[5]}
        Email ID: {user[6]}
        Address: {user[7]}
        Status: {user[8]}
        """)

def login():
    print("=== Login ===")
    acc_num = input("Account Number: ").strip()
    password = input("Password: ").strip()
    cursor.execute("SELECT * FROM login WHERE account_number = %s AND password = %s", (acc_num, password))
    user = cursor.fetchone()
    if not user:
        print("Invalid credentials!")
        return
    print(f"Login successful! Account: {acc_num}")
    cursor.execute("UPDATE login SET last_login = NOW() WHERE account_number = %s", (acc_num,))
    db.commit()
    while True:
        print("""
        1. Show Balance
        2. Credit Amount
        3. Debit Amount
        4. Logout
        """)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            cursor.execute("SELECT balance FROM users WHERE account_number = %s", (acc_num,))
            balance = cursor.fetchone()[0]
            print(f"Balance: {balance}")
        elif choice == "2":
            amount = float(input("Enter amount to credit: ").strip())
            cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, acc_num))
            cursor.execute("INSERT INTO transactions (account_number, type, amount) VALUES (%s, 'credit', %s)", (acc_num, amount))
            db.commit()
            print(f"{amount} credited successfully!")
        elif choice == "3":
            amount = float(input("Enter amount to debit: ").strip())
            cursor.execute("SELECT balance FROM users WHERE account_number = %s", (acc_num,))
            balance = cursor.fetchone()[0]
            if amount > balance:
                print("Insufficient balance!")
            else:
                cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, acc_num))
                cursor.execute("INSERT INTO transactions (account_number, type, amount) VALUES (%s, 'debit', %s)", (acc_num, amount))
                db.commit()
                print(f"{amount} debited successfully!")
        elif choice == "4":
            print("Logged out!")
            break
        else:
            print("Invalid choice!")

def exit_system():
    print("Exiting...")
    db.close()
    exit()

def main():
    while True:
        print("""
        === Banking System ===
        1. Add User
        2. Show Users
        3. Login
        4. Exit
        """)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            add_user()
        elif choice == "2":
            show_users()
        elif choice == "3":
            login()
        elif choice == "4":
            exit_system()
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
