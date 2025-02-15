import threading
import tkinter as tk
from tkinter import END, IntVar, messagebox
import mysql.connector
from datetime import datetime
import schedule
import time
from tkcalendar import DateEntry 
import bcrypt
from tkinter import ttk
from datetime import datetime
import sqlite3
class ChurchOffertoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Offertory Maintenance System")
        
        self.config(bg="#43e640")

        try:
            # Connect to SQLite database (creates the file if it doesn't exist)
          # Connect to SQLite Database (using 'churchdb.sqlite3')
            self.conn = sqlite3.connect('churchdb.sqlite3')
            self.cursor = self.conn.cursor()
            self.cursor.execute('PRAGMA foreign_keys = ON;')

        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")
        
       
         # Create tables if they do not exist
        self.create_tables()

        # Function to check if admin exists when the app starts
        self.check_admin()
 
        
        # Dictionary to hold frames (windows)
        self.frames = {}

        for F in (LoginPage, AdminPage,OffertoryRecordsPage,ExpensesPage,AdminRegisterPage,AllUsersPage):
            page_name = F.__name__
            # Wrap each page class in ScrollableFrame
            frame = F(parent=self, controller=self) 
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.config(background="#43e640")
            

        # Show login page first
        self.show_frame("LoginPage")
    def create_tables(self):
        # Create the users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                password TEXT DEFAULT NULL,
                role INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create the attendance table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(10,2),
                approved_by INTEGER NOT NULL,
                category TEXT NULLABLE,
                description TEXT NULLABLE,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
              
                FOREIGN KEY (approved_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS offertory_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount DECIMAL(10,2),
                received_by INTEGER NOT NULL,
                service_type TEXT NULLABLE,
                
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
              
                FOREIGN KEY (received_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        self.conn.commit()

    def check_admin(self):
        self.cursor.execute("SELECT * FROM users WHERE role = 1")
        admin = self.cursor.fetchone()

        if admin:
            # If admin exists, show success message and close the app
            messagebox.showinfo("Info", "Admin user already set up!")
            self.quit()  # Close the app if admin exists
        else:
            # If no admin exists, show the admin setup form
            self.show_admin_setup()

    def show_admin_setup(self):
        # Create and show the admin setup form in a new window
        admin_setup_window = tk.Toplevel(self)
        admin_setup_window.lift()
        admin_setup_window.attributes("-topmost", True)
        admin_setup_window.title("Admin Setup")
        admin_setup_window.geometry("500x500")

        label_name = tk.Label(admin_setup_window, text="Name:")
        label_name.grid(row=0, column=0)
        entry_name = tk.Entry(admin_setup_window)
        entry_name.grid(row=0, column=1)

        label_phone = tk.Label(admin_setup_window, text="Phone:")
        label_phone.grid(row=1, column=0)
        entry_phone = tk.Entry(admin_setup_window)
        entry_phone.grid(row=1, column=1)

        label_password = tk.Label(admin_setup_window, text="Password:")
        label_password.grid(row=2, column=0)
        entry_password = tk.Entry(admin_setup_window, show="*")
        entry_password.grid(row=2, column=1)

        submit_button = tk.Button(admin_setup_window, text="Create Admin", command=lambda: self.create_admin(entry_name, entry_phone, entry_password))
        submit_button.grid(row=3, columnspan=2)

    def create_admin(self, entry_name, entry_phone, entry_password):
        name = entry_name.get()
        phone = entry_phone.get()
        password = entry_password.get()

        if not name or not phone or not password:
            messagebox.showerror("Error", "All fields must be filled")
            return

        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
      
        try:
            # Insert admin user into the database
            self.cursor.execute("INSERT INTO users (name, phone, password, role) VALUES (?, ?, ?, ?)", 
                                (name, phone, hashed_password, 1))
            self.conn.commit()
            messagebox.showinfo("Success", "Admin user created successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error creating admin: {e}")
        
        # Close the setup window after admin creation
        self.check_admin()

       
    def show_frame(self, page_name):
        #Switches to the given frame
        frame = self.frames[page_name]
        frame.tkraise()
    
      # Call load_expenses() only when navigating to ExpensesPage
        if page_name == "ExpensesPage":
            frame.load_expenses()
            frame.update_totals()
        elif page_name=="OffertoryRecordsPage":
            frame.load_offertory()
            frame.update_totals()
        elif page_name=="AllUsersPage":
            frame.load_users()
   

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="OFFERTORY SYSTEM", font=("Arial", 35),bg="#a1e640")
        label.pack(pady=10,fill=tk.X,padx=80)

        label = tk.Label(self, text="Admin Login", font=("Arial", 25),bg="#daf5f4")
        label.pack(pady=10)

        tk.Label(self, text="Username",font=("Verdana",20),bg="#79ede9").pack(padx=5,pady=10)
        self.username_entry = tk.Entry(self,font=("Verdana",20),width=20,)
        self.username_entry.pack()

        tk.Label(self, text="Password",font=("Verdana",20),bg="#79ede9").pack(padx=5,pady=20)
        self.password_entry = tk.Entry(self, show="*",font=("Verdana",20),width=20)
        self.password_entry.pack(pady=10)

        login_button = tk.Button(self, text="Login", command=self.check_login,font=("Verdana",20),width=20,bg="green",activebackground="green")
        login_button.pack(pady=10)
        self.x=IntVar()
        checkpassword=tk.Checkbutton(self,command=self.showPassword,text="Show Password",variable=self.x,onvalue=1,offvalue=0)
        checkpassword.pack(padx=5,pady=5)
       
    def showPassword(self):

        if (self.x.get()==1):
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show="*")

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill all input")
            return

        try:
        # Fetch all users with the given username
            self.controller.cursor.execute("SELECT password, role FROM users WHERE name = ?", (username,))
            users = self.controller.cursor.fetchall()

            if users:  # If at least one user is found
                for user in users:
                    stored_password = user[0]
                    role = user[1]

                # Check if the stored password matches and if the role is 1 (admin)
                    #if stored_password == password and role == 1:
                    if role == 1 and bcrypt.checkpw(password.encode('utf-8'), stored_password):
                        messagebox.showinfo("Success", "Login Successful")
                        self.username_entry.delete(0,END)
                        self.password_entry.delete(0,END)
                        self.controller.show_frame("AdminPage")
                        return  # Exit the loop after successful login
                      
                   

            # If no admin user found with the matching password
                messagebox.showerror("Error", "Invalid username or password")
            else:
                messagebox.showerror("Error", "User not found")

        except mysql.connector.Error as e:
             print(f"Error: {e}")
             messagebox.showerror("Error", "Database error occurred")

        finally:
        # You can leave the cursor open for reuse
           pass


class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="ADMIN PANEL", font=("verdana", 25),bg="#528268")
        label.pack(pady=10,fill=tk.X,padx=80)

        viewUsersbtn=tk.Button(self,text="View All Users",command=lambda: controller.show_frame("AllUsersPage"),
                                 bg="#393b60",activebackground="#393b60",fg="white",activeforeground="white",
                                 font=("Verdana",15))
        viewUsersbtn.pack(pady=20)
        add_user_button = tk.Button(self, text="Add User",font=("verdana", 15), command=self.add_user,bg="#20e641",
                                    activebackground="#20e641",fg="red",activeforeground="red")
        add_user_button.pack(pady=20)
        offertoryRecords_button = tk.Button(self, text="View Offertory Record",
                                       command=lambda: controller.show_frame("OffertoryRecordsPage"),bg="#b4e620",
                                    activebackground="#b4e620",fg="red",activeforeground="red",font=("verdana", 15))
        offertoryRecords_button.pack(pady=20)
        addOffertory_button = tk.Button(self, text="Add New Offertory Record",
                                       command=self.addNewOffertory,bg="#30dbc2",
                                    activebackground="#30dbc2",fg="red",activeforeground="red",font=("verdana", 15))
        addOffertory_button.pack(pady=20)

        viewExpenses_button = tk.Button(self, text="View Expenses",
                                       command=lambda: controller.show_frame("ExpensesPage"),bg="#5cd15a",
                                    activebackground="#5cd15a",fg="red",activeforeground="red",font=("verdana", 15))
        viewExpenses_button.pack(pady=10)


        addExpenses_button = tk.Button(self, text="Add New Expenses",
                                       command=self.addNewExpenses,bg="#685ad1",
                                    activebackground="#685ad1",fg="red",activeforeground="red",font=("verdana", 15))
        addExpenses_button.pack(pady=20)

        createAdminBtn=tk.Button(self,text="Create Admin",command=lambda: controller.show_frame("AdminRegisterPage"),
                                 bg="#393b35",activebackground="#393b35",fg="white",activeforeground="white",
                                 font=("Verdana",15))
        createAdminBtn.pack(pady=10)
        logout_button = tk.Button(self, text="Logout", command=lambda: controller.show_frame("LoginPage"), bg="#ed0e25",activebackground="#ed0e25",fg="white",activeforeground="white",
                                 font=("Verdana",15))
        logout_button.pack(pady=20)
    def load_users(self):
   
        try:
            self.controller.cursor.execute(
        "SELECT id,name,phone FROM users", 
        )
        except mysql.connector.Error as e:
            messagebox.showerror("Error",f"Error loading Users: {e}")
        finally:
            self.controller.cursor.fetchall()  # Ensure all results are fetched or clear the cursor buffer


    def add_user(self):
        new_window = tk.Toplevel(self)
        new_window.title("Add User")
        new_window.geometry("500x500")


        tk.Label(new_window, text="Name:",font=("Verdana",20)).pack(pady=15)
        name_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        name_entry.pack()

        tk.Label(new_window, text="Phone Number:",font=("Verdana",20)).pack(pady=15)
        phone_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        phone_entry.pack()


        def save_user():
            name = name_entry.get()
            phone = phone_entry.get()
            if (name==""):
                messagebox.showerror("Error","Please Fill Input")
            elif (not phone.isdigit() and not len(phone)==10):
                messagebox.showerror("Error","Please enter valid Phone number")
            elif name and phone:
                self.controller.cursor.execute("INSERT INTO users (name, phone) VALUES (?, ?)", (name, phone))
                self.controller.conn.commit()
                messagebox.showinfo("Success", f"User {name} added!")
                self.load_users()
                new_window.destroy()
            
            else:
                messagebox.showwarning("Warning", "Please enter all details")

        save_button = tk.Button(new_window, text="Save",font=("Verdana",20), command=save_user,bg="#3ff260",activebackground="#3ff260",fg="red",activeforeground="red",width=10)
        save_button.pack(pady=30)

    def addNewOffertory(self):
        new_window = tk.Toplevel(self)
        new_window.title("Add New Offertory Record")
        new_window.geometry("500x500")
       
       
        tk.Label(new_window, text="Amount GHS:",font=("Verdana",20)).pack(pady=15)
        amount_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        amount_entry.pack()

        tk.Label(new_window, text="Service Type:",font=("Verdana",20)).pack(pady=15)
        servicetype_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        servicetype_entry.pack()

        tk.Label(new_window, text="Date:", font=("Verdana", 20)).pack(pady=15)
        date_entry = DateEntry(new_window, font=("Verdana", 20), width=20)  # Using DateEntry
        date_entry.pack()

       
        tk.Label(new_window, text="Received By:", font=("Verdana", 20)).pack(pady=15)
        user_combobox = ttk.Combobox(new_window, font=("Verdana", 20), width=20)
        user_combobox.pack()

        
        def loadOffertoryReceivingUsers():
            try:
                self.controller.cursor.execute("SELECT id, name FROM users")
                records = self.controller.cursor.fetchall()  # Corrected fetch method
                user_list = [(record[1], record[0]) for record in records]  # List of (name, id)

                user_combobox['values'] = [user[0] for user in user_list]  # Populate names

                # Store user IDs in a dictionary for easy lookup
                self.user_dict = {user[0]: user[1] for user in user_list}
            except mysql.connector.Error as e:
                messagebox.showerror("Error",f"Error loading users: {e}")
            finally:
                self.controller.cursor.fetchall()  # Ensure all results are fetched or clear the cursor buffer

       
        def saveNewOffertory(date_entry):
            amount = amount_entry.get()  
            servicetype = servicetype_entry.get() 
            date = date_entry.get_date().strftime('%Y-%m-%d')  # Correctly format the date
            user_name = user_combobox.get()  # Get selected user name
            user_id = self.user_dict.get(user_name)  # Lookup user ID from the dictionary


            if (amount==""  or date==""):
                messagebox.showerror("Error","Please fill all input")
            elif (not amount.isdecimal()):
                messagebox.showerror("Error","Please enter valid amount")
            else:
                try:
                    self.controller.cursor.execute(
                    """INSERT INTO offertory_record (amount, service_type, date, received_by) 
                    VALUES (?, ?, ?, ?)""",
                    (amount, servicetype, date, user_id)
                )
                    self.controller.conn.commit()
                    messagebox.showinfo("Success", "New Record added!")
                    new_window.destroy()
                except mysql.connector.Error as e:
                    print(f"Error loading expenses: {e}")
               
                    
                
        loadOffertoryReceivingUsers()

        saveOffertory_button = tk.Button(
            new_window,
            text="Save",
            font=("Verdana", 20),
            command=lambda:saveNewOffertory(date_entry),
            bg="#3ff260",
            activebackground="#3ff260",
            fg="red",
            activeforeground="red",
            width=20
        )
        saveOffertory_button.pack(pady=30)
        
    def addNewExpenses(self):
        new_window = tk.Toplevel(self)
        new_window.title("Add New Expenses")
        new_window.geometry("500x500")
       
       
        tk.Label(new_window, text="Amount GHS:",font=("Verdana",20)).pack(pady=15)
        amount_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        amount_entry.pack()

        tk.Label(new_window, text="Enter Category/Item:",font=("Verdana",20)).pack(pady=15)
        category_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        category_entry.pack()

        tk.Label(new_window, text="Item Description:",font=("Verdana",20)).pack(pady=15)
        description_entry = tk.Entry(new_window,font=("Verdana",20),width=20)
        description_entry.pack()

        tk.Label(new_window, text="Date:", font=("Verdana", 20)).pack(pady=15)
        date_entry = DateEntry(new_window, font=("Verdana", 20), width=20)  # Using DateEntry
        date_entry.pack()

       
        tk.Label(new_window, text="Approved By:", font=("Verdana", 20)).pack(pady=15)
        user_combobox = ttk.Combobox(new_window, font=("Verdana", 20), width=20)
        user_combobox.pack()

        
        def loadApprovalUsers():
            try:
                self.controller.cursor.execute("SELECT id, name FROM users")
                records = self.controller.cursor.fetchall()  # Corrected fetch method
                user_list = [(record[1], record[0]) for record in records]  # List of (name, id)

                user_combobox['values'] = [user[0] for user in user_list]  # Populate names

                # Store user IDs in a dictionary for easy lookup
                self.user_dict = {user[0]: user[1] for user in user_list}
            except mysql.connector.Error as e:
                messagebox.showerror("Error",f"Error loading expenses: {e}")
            finally:
                self.controller.cursor.fetchall() 
                
       
        def saveNewExpenses(date_entry):
            amount = amount_entry.get()  
            category = category_entry.get() 
            description = description_entry.get() 
            date = date_entry.get_date().strftime('%Y-%m-%d')  # Correctly format the date
            user_name = user_combobox.get()  # Get selected user name
            user_id = self.user_dict.get(user_name)  # Lookup user ID from the dictionary


            if (amount==""  or date==""):
                messagebox.showerror("Error","Please fill all input")
            elif (not amount.isdecimal()):
                messagebox.showerror("Error","Please enter valid amount")
            else:
                try:
                    self.controller.cursor.execute(
                    """INSERT INTO expenses (amount, category, date, approved_by,description) 
                    VALUES (?, ?, ?, ?,?)""",
                    (amount, category, date, user_id,description)
                    )
                    self.controller.conn.commit()
                    messagebox.showinfo("Success", "New Expenses added!")
                    new_window.destroy()
                except  mysql.connector.Error as e:
                    print("Error",f"Error in database: {e}")
               
                
               
        
        loadApprovalUsers()

        saveExpenses_button = tk.Button(
            new_window,
            text="Save",
            font=("Verdana", 20),
            command=lambda:saveNewExpenses(date_entry),
            bg="#3ff260",
            activebackground="#3ff260",
            fg="red",
            activeforeground="red",
            width=20
        )
        saveExpenses_button.pack(pady=30)
        

           
       

#admin register class
class AdminRegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="CREATE ADMIN", font=("Arial", 35),bg="#d557de")
        label.pack(pady=10,padx=40)

        tk.Label(self, text="Username",font=("Verdana",20),bg="#bad66b").pack(pady=18)
        self.username_entry = tk.Entry(self,font=("Verdana",20),width=20)
        self.username_entry.pack(pady=10)

        tk.Label(self, text="Password",font=("Verdana",20),bg="#bad66b").pack(pady=18)
        self.password_entry = tk.Entry(self, show="*",font=("Verdana",20),width=20)
        self.password_entry.pack(pady=10)

        tk.Label(self, text="Phone",font=("Verdana",20),bg="#bad66b").pack(pady=18)
        self.phoneEntry = tk.Entry(self,font=("Verdana",20),width=20)
        self.phoneEntry.pack(padx=4,pady=10)

        register_button = tk.Button(self, text="Register", command=self.registerAdmin,bg="#6bd686",activebackground="#6bd686",
                                    fg="red",activeforeground="red",font=("Verdana",20),width=20)
        register_button.pack(pady=5)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("AdminPage")
                                ,bg="black",activebackground="black",
                                    fg="white",activeforeground="white",font=("Verdana",20))
        back_button.pack(pady=5,side="right")

    
    def hash_password(self,password):
    # Generate salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def registerAdmin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        phone=self.phoneEntry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill all input")
            return

        try:
        # Fetch all users with the given username
            if username and password:
                hashedpass=self.hash_password(password)
                role=1
                self.controller.cursor.execute("INSERT INTO users (name,password,role,phone) VALUES (?,?,?,?)", (username,hashedpass,role,phone))
                self.controller.conn.commit()
           
                messagebox.showerror("Success", "New Admin Added")
                self.username_entry.delete(0,END)
                self.password_entry.delete(0,END)
            else:
                messagebox.showerror("Error","Process Failed..please try again..")

        except mysql.connector.Error as e:
             print(f"Error: {e}")
             messagebox.showerror("Error", "Database error occurred")

        finally:
        # You can leave the cursor open for reuse
           pass


class OffertoryRecordsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.update_totals()
        # Define columns for the Treeview
        self.columns = ('No','Amount','Date','Service Type', 'Received By')

       # Create Treeview
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
        # Create a hidden 'id' column
        self.tree.column("#0", width=0, stretch=tk.NO)  # This hides the 'id' column
        self.tree.heading('No', text='No')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Service Type', text='Service Type')
        self.tree.heading('Received By', text='Received By')
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        # Add a scroll bar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=2, sticky='ns')

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

        delete_button = tk.Button(button_frame, text="Delete Record", command=self.deleteRecord,
                                bg="#6bd686", activebackground="#6bd686",
                                fg="#cf6bd6", activeforeground="#cf6bd6", 
                                font=("Verdana", 15))
        delete_button.pack(side=tk.LEFT, padx=5)
       
        # Back button
        back_button = tk.Button(button_frame, text="Back", command=lambda: controller.show_frame("AdminPage")
                                ,bg="black",activebackground="black",
                                    fg="white",activeforeground="white",font=("Verdana",20))
        back_button.pack(side=tk.RIGHT,padx=80)

        # Configure row and column weights for proper resizing
        self.grid_rowconfigure(1, weight=1)  # Allow Treeview to expand vertically
        self.grid_columnconfigure(0, weight=0)  # First column expands horizontally
        self.grid_columnconfigure(1, weight=1)  # Second column expands horizontally
        self.grid_columnconfigure(2, weight=0)  # Scrollbar column does not expand

        #self.load_offertory()
    # Method to calculate and display totals
    def update_totals(self):
        try:
            # Total for Today
            self.controller.cursor.execute(
                 "SELECT SUM(amount) AS total_today FROM offertory_record WHERE DATE(date) = CURRENT_DATE"
  )
            total_today = self.controller.cursor.fetchone()[0] or 0  # Get the result or 0 if None

            # Total for This Month
            self.controller.cursor.execute(
                "SELECT SUM(amount) AS total_month FROM offertory_record WHERE strftime('%Y-%m', date) = strftime('%Y-%m', CURRENT_DATE)"
   )
            total_month = self.controller.cursor.fetchone()[0] or 0

            # Total for This Year
            self.controller.cursor.execute(
                 "SELECT SUM(amount) AS total_year FROM offertory_record WHERE strftime('%Y', date) = strftime('%Y', CURRENT_DATE)"
  )
            total_year = self.controller.cursor.fetchone()[0] or 0

            # Update labels to display totals


            Totallabel_today = tk.Label(self, text=f"Total Offertory Amount Today GHS: {total_today}", font=("Arial", 14))
            Totallabel_today.grid(row=0, column=0, pady=10)

            Totallabel_month = tk.Label(self, text=f"Total Offertory This Month GHS:{total_month}", font=("Arial", 14))
            Totallabel_month.grid(row=0, column=1, pady=10)

            Totallabel_year = tk.Label(self, text=f"Amount This Year GHS: {total_year}", font=("Arial", 14))
            Totallabel_year.grid(row=0, column=1, pady=10,padx=(700, 0), sticky="ns")

        except mysql.connector.Error as e:
            print(f"Error fetching totals: {e}")

    def load_offertory(self):
   
        try:
            self.controller.cursor.execute(
            """
            SELECT offertory_record.id, offertory_record.amount, offertory_record.date, offertory_record.service_type, users.name AS received_by_name
            FROM offertory_record
            LEFT JOIN users ON offertory_record.received_by = users.id
            """ 
        )

            records = self.controller.cursor.fetchall()
        
            if not records:
                
                return 
        # Clear the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

        # Insert records into the Treeview
            self.count=0
            for record in records:
                self.count+=1
                self.tree.insert('', tk.END,text=record[0], values=(self.count,record[1],record[2],record[3],record[4]))
        except mysql.connector.Error as e:
            messagebox.showerror("Error",f"Error loading offertory record: {e}")
        finally:
            self.controller.cursor.fetchall() 
    def deleteRecord(self):
        selected_items = self.tree.selection()  # Get all selected items

        if not selected_items:
            messagebox.showerror("Error", "No Record selected.")
            return

      
        for item in selected_items:
            id = self.tree.item(item, 'text')  # Get the id from the selected item

       
            try:
                self.controller.cursor.execute(
                "DELETE FROM offertory_record WHERE id =?",
                (id,)
                )

                self.controller.conn.commit()
                self.load_offertory()  # Refresh the Treeview
                messagebox.showinfo("Succcess","Record removed Successfully")
            except  mysql.connector.Error as e:
                messagebox.showerror("Error",f"Error deleting: {e}")
            finally:
                self.controller.cursor.fetchall() 

class ExpensesPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.update_totals()

        # Define columns for the Treeview
        self.columns = ('No','Item/Category','Item Description','Amount','Date', 'Approved By')

       # Create Treeview
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
          # Create a hidden 'id' column
        self.tree.column("#0", width=0, stretch=tk.NO)  # This hides the 'id' column
       
        self.tree.heading('No', text='No')
        self.tree.heading('Item/Category', text='Item/Category')
        self.tree.heading('Item Description', text='Item Description')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Approved By', text='Approved By')
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

        # Add a scroll bar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=2, sticky='ns')

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

        delete_button = tk.Button(button_frame, text="Delete Expense Record", command=self.deleteExpenseRecord,
                                bg="#6bd686", activebackground="#6bd686",
                                fg="#cf6bd6", activeforeground="#cf6bd6", 
                                font=("Verdana", 15))
        delete_button.pack(side=tk.LEFT, padx=5)
       
        # Back button
        back_button = tk.Button(button_frame, text="Back", command=lambda: controller.show_frame("AdminPage")
                                ,bg="black",activebackground="black",
                                    fg="white",activeforeground="white",font=("Verdana",20))
        back_button.pack(side=tk.RIGHT,padx=80)

        # Configure row and column weights for proper resizing
        self.grid_rowconfigure(1, weight=1)  # Allow Treeview to expand vertically
        self.grid_columnconfigure(0, weight=0)  # First column expands horizontally
        self.grid_columnconfigure(1, weight=1)  # Second column expands horizontally
        self.grid_columnconfigure(2, weight=0)  # Scrollbar column does not expand

        #self.load_expenses()
    
    def update_totals(self):
        try:
            # Total for Today
            self.controller.cursor.execute(
                "SELECT SUM(amount) AS total_today FROM offertory_record WHERE DATE(date) = CURRENT_DATE"
    )
            total_today = self.controller.cursor.fetchone()[0] or 0  # Get the result or 0 if None

            # Total for This Month
            self.controller.cursor.execute(
                 "SELECT SUM(amount) AS total_month FROM offertory_record WHERE strftime('%Y-%m', date) = strftime('%Y-%m', CURRENT_DATE)"
  )
            total_month = self.controller.cursor.fetchone()[0] or 0

            # Total for This Year
            self.controller.cursor.execute(
                "SELECT SUM(amount) AS total_year FROM offertory_record WHERE strftime('%Y', date) = strftime('%Y', CURRENT_DATE)"
    )
            total_year = self.controller.cursor.fetchone()[0] or 0

            # Update labels to display totals


            Totallabel_today = tk.Label(self, text=f"Expenses Today GHS: {total_today}", font=("Arial", 15))
            Totallabel_today.grid(row=0, column=0, pady=10)

            Totallabel_month = tk.Label(self, text=f"Expenses This Month GHS: {total_month}", font=("Arial", 15))
            Totallabel_month.grid(row=0, column=1, pady=10,)

            Totallabel_year = tk.Label(self, text=f"Expenses {datetime.now().year} GHS:{total_year}", font=("Arial", 15))
            Totallabel_year.grid(row=0, column=1, pady=10, padx=(700,0))

        except mysql.connector.Error as e:
            print(f"Error fetching totals: {e}")


    def load_expenses(self):   
        
        try:
            self.controller.cursor.execute(
            """
            SELECT expenses.id, expenses.amount, expenses.date, expenses.category, users.name AS received_by_name,expenses.description
            FROM expenses
            LEFT JOIN users ON expenses.approved_by = users.id
            """ 
            )

            records = self.controller.cursor.fetchall()
            if not records:
                # messagebox.showerror("Error", "No records found")
                return 
        # Clear the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

        # Insert records into the Treeview
            self.count=0
            for record in records:
                self.count+=1
                self.tree.insert('', tk.END,text=record[0], values=(self.count,record[3],record[5],record[1],record[2],record[4]))
        except  mysql.connector.Error as e:
            messagebox.showerror("Error",f"Error loading expenses: {e}")
        finally:
            self.controller.cursor.fetchall() 

    def deleteExpenseRecord(self):
        selected_items = self.tree.selection()  # Get all selected items

        if not selected_items:
            messagebox.showerror("Error", "No Record selected.")
            return

      
        for item in selected_items:
            id = self.tree.item(item, 'text')  # Get the id from the selected item

       
            try:  
                self.controller.cursor.execute(
                "DELETE FROM expenses WHERE id =?",
                (id,)
            )

                self.controller.conn.commit()
                self.load_expenses()  # Refresh the Treeview
                messagebox.showinfo("Succcess","Record removed Successfully")
            except mysql.connector.Error as e:
                messagebox.showerror("Error",f"Error deleting : {e}")
           


   
class AllUsersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

       
        today = datetime.now().strftime('%Y-%m-%d')
        

      
        label = tk.Label(self, text="All Users", font=("Arial", 16))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        datelabel = tk.Label(self, text=today, font=("Arial", 16))
        datelabel.grid(row=0,column=4,pady=10)

        

        # Define columns for the Treeview
        self.columns = ('NO','Name', 'Phone')

       # Create Treeview
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings')
          # Create a hidden 'id' column
        self.tree.column("#0", width=0, stretch=tk.NO)  # This hides the 'id' column
       
        self.tree.heading('NO', text='NO')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Phone', text='Phone')
        self.tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        # Add a scroll bar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=2, sticky='ns')

        self.tree.bind("<Double-1>", self.on_row_click)  # Double-click to trigger update window


        # Button frame
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky='ew')

        # delete button
        delete_button = tk.Button(button_frame, text="Delete User", command=self.deleteUser ,bg="#6bd686",activebackground="#6bd686",
                                    fg="#cf6bd6",activeforeground="#cf6bd6",font=("Verdana",15))
        delete_button.pack(side=tk.LEFT, padx=5)

        # Back button
        back_button = tk.Button(button_frame, text="Back", command=lambda: controller.show_frame("AdminPage")
                                ,bg="black",activebackground="black",
                                    fg="white",activeforeground="white",font=("Verdana",20))
        back_button.pack(side=tk.RIGHT,padx=80)

        # Configure row and column weights for proper resizing
        self.grid_rowconfigure(1, weight=1)  # Allow Treeview to expand vertically
        self.grid_columnconfigure(0, weight=1)  # First column expands horizontally
        self.grid_columnconfigure(1, weight=1)  # Second column expands horizontally
        self.grid_columnconfigure(2, weight=0)  # Scrollbar column does not expand

        self.load_users()
    def open_update_window(self, user_id, user_name, user_phone):
    # Create a new top-level window (popup window)
        update_window = tk.Toplevel(self)
        update_window.title("Update User")
        update_window.geometry("300x200")

    # Create entry fields for name and phone
        tk.Label(update_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(update_window,font=("Verdana",20),width=20)
        name_entry.pack(pady=5)
        name_entry.insert(0, user_name)  # Pre-fill with current name

        tk.Label(update_window, text="Phone:").pack(pady=5)
        phone_entry = tk.Entry(update_window,font=("Verdana",20),width=20)
        phone_entry.pack(pady=5)
        phone_entry.insert(0, user_phone)  # Pre-fill with current phone

    # Create a Save button
        tk.Button(update_window, text="Save", command=lambda: self.update_user(user_id, name_entry.get(), phone_entry.get(), update_window)).pack(pady=10)

        update_window.transient(self)  # Keep the popup window on top
        update_window.grab_set()  # Disable interaction with the main window

    
    def update_user(self, user_id, new_name, new_phone, update_window):
        if not new_name or not new_phone:
            messagebox.showerror("Error", "Both fields must be filled.")
            return
    #Update the user's details in the database
        try:
            self.controller.cursor.execute("UPDATE users SET name = ?, phone = ? WHERE id = ?",
                (new_name, new_phone, user_id))
            self.controller.conn.commit()

        # Reload the users in the Treeview
            self.load_users()

        # Close the update window
            update_window.destroy()

            messagebox.showinfo("Success", "User updated successfully.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error",f"Error loading expenses: {e}")
       

    def on_row_click(self, event):
    # Get the selected row
        selected_item = self.tree.selection()[0]
        user_id = self.tree.item(selected_item, 'text')  # Get the user_id
        user_name = self.tree.item(selected_item, 'values')[1]  # Get the name
        user_phone = self.tree.item(selected_item, 'values')[2]  # Get the phone

    # Open the update window
        self.open_update_window(user_id, user_name, user_phone)

  

    def load_users(self):
        try:
            self.controller.cursor.execute(
            "SELECT id,name,phone FROM users", 
            
        )
            records = self.controller.cursor.fetchall()
            if not records:
                return
                # messagebox.showinfo('no records found')

        # Clear the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

        # Insert records into the Treeview
            self.count=0
            for record in records:
                self.count+=1
                id=record[0]
                names=record[1]
                phones=record[2]
                self.tree.insert('', tk.END,text=id,values=(self.count,names,phones))
        except mysql.connector.Error as e:
            messagebox.showerror("Error",f"Error loading users: {e}")
        finally:
            self.controller.cursor.fetchall() 

    def get_status_text(self, status_code):
    # Converts status code (1, 2, 3) to text
        return {1: 'Absent', 2: 'Late', 3: 'Present'}.get(status_code, 'Unknown')
    def deleteUser(self):
        selected_items = self.tree.selection()  # Get all selected items

        if not selected_items:
            messagebox.showerror("Error", "No user selected.")
            return

      
        for item in selected_items:
            id = self.tree.item(item, 'text')  # Get the id from the selected item

        # Update attendance status to 'Present' (3)
            self.controller.cursor.execute(
            "DELETE FROM users WHERE id =?",
            (id,)
        )

        self.controller.conn.commit()
        self.load_users()  # Refresh the Treeview
        messagebox.showinfo("Succcess","User removed Successfully")

   

if __name__ == "__main__":
    app = ChurchOffertoryApp()
    app.minsize(800,600)
    #app.attributes('-fullscreen', True)
    
    app.update()  # Update to get the latest geometry
    x = (app.winfo_width() // 2) - (app.winfo_width() // 2)
    y = (app.winfo_height() // 2) - (app.winfo_height() // 2)
    app.geometry(f"+{x}+{y}")  # Center the window on the screen
    app.mainloop()   
    