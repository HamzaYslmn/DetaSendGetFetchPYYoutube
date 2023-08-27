import tkinter as tk
from tkinter import ttk
from deta import Deta

# Instantiate the Deta object
deta = Deta('a0qrhpfdxy4_xxxxxxxxxxxxxxxxxx')  # Api Key
db = deta.Base('DetaBase')  # DB ismi

# Function to add data to the database
def add_data():
    name = name_entry.get()
    age = age_entry.get()
    
    if name and age:
        data = {"name": name, "age": int(age)}
        try:
            db.put(data)
            status_label.config(text="Data added successfully")
            fetch_all_data()  # Refresh the data after adding
        except Exception as e:
            status_label.config(text="Error adding data: " + str(e))
    else:
        status_label.config(text="Name and age are required fields")

def fetch_all_data():
    try:
        response = db.fetch()
        items = response.items
        
        # Clear the Treeview
        for item in tree.get_children():
            tree.delete(item)
        
        if items:
            # Get column names from all items' keys
            all_column_names = set()
            for item in items:
                all_column_names.update(item.keys())
            column_names = list(all_column_names)
            
            # Move 'key' to the beginning of the column names
            if 'key' in column_names:
                column_names.remove('key')
                column_names.insert(0, 'key')
            
            # Sort the rest of the columns alphabetically
            column_names[1:] = sorted(column_names[1:])
            
            tree["columns"] = column_names
            
            # Set headers and enable sorting by clicking
            for col_index, col in enumerate(column_names):
                tree.heading(col, text=col, command=lambda col_index=col_index: sort_treeview(col_index))
            
            # Insert fetched data into the Treeview
            for item in items:
                values = [item.get(col, "") for col in column_names]
                tree.insert("", "end", values=values)
            
            # Adjust window width based on the number of columns
            root.update_idletasks()  # Update widget sizes before calculating
            col_width = max(map(len, column_names)) * 10  # Adjust the multiplier as needed
            tree_width = tree.winfo_reqwidth()
            new_width = max(tree_width, col_width) + 20  # Add padding
            
            # Adjust window height to accommodate status messages
            new_height = 450  # Adjust as needed
            root.geometry(f"{new_width}x{new_height}")
            
            status_label.config(text="Fetched data successfully")
        else:
            status_label.config(text="No data available")
    except Exception as e:
        status_label.config(text="Error fetching data: " + str(e))

# Function to sort the Treeview by column heading
def sort_treeview(col_index):
    items = [(tree.set(child, col_index), child) for child in tree.get_children("")]
    items.sort()

    for index, (value, child) in enumerate(items):
        tree.move(child, "", index)
        
# Function to delete selected entry
def delete_selected():
    selected_item = tree.selection()
    if selected_item:
        item_id = tree.item(selected_item)["values"][0]  # Assuming "key" is the first column
        try:
            db.delete(item_id)
            fetch_all_data()  # Refresh the data after deleting
            status_label.config(text="Data deleted successfully")
        except Exception as e:
            status_label.config(text="Error deleting data: " + str(e))
    else:
        status_label.config(text="No item selected")

# Create the main application window
root = tk.Tk()
root.title("Deta Base Interface")
root.geometry("600x450")  # Initial window size

# Create and arrange widgets
name_label = tk.Label(root, text="Name:")
name_label.pack()
name_entry = tk.Entry(root)
name_entry.pack()

age_label = tk.Label(root, text="Age:")
age_label.pack()
age_entry = tk.Entry(root)
age_entry.pack()

# Create a frame to hold buttons
button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=10)

# Create the Add Data button
add_button = tk.Button(button_frame, text="Add Data", command=add_data, bg="green", fg="white")
add_button.pack(side=tk.LEFT, padx=5)

# Create the Fetch Data button
fetch_button = tk.Button(button_frame, text="Fetch All Data", command=fetch_all_data, bg="blue", fg="white")
fetch_button.pack(side=tk.LEFT, padx=5)

# Create the Delete Selected button
delete_button = tk.Button(button_frame, text="Delete Selected", command=delete_selected, bg="red", fg="white")
delete_button.pack(side=tk.RIGHT)

# Create a Treeview widget
tree = ttk.Treeview(root, show='headings')
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))  # Add padding at the bottom

# Create a vertical scrollbar and associate it with the Treeview widget
tree_scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
tree_scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=tree_scrollbar.set)

# Configure grid weights to make the Treeview expand when resized
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

# Start the main event loop
root.mainloop()
