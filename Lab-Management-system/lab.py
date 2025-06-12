import tkinter as tk
import threading
import time
import csv

# --------------------- Lab Class ---------------------
class Lab:
    def __init__(self, lab_id, num_computers, softwares_installed):
        self.lab_id = lab_id
        self.num_computers = num_computers
        self.available_computers = num_computers
        self.softwares_installed = softwares_installed
        self.current_class = None
        self.subject = None
        self.assignment_thread = None
        self.assigned_time = None
        self.time_duration = None
        self.total_students = None

    def assign_class(self, class_name, subject, num_students, class_duration_hours):
        if self.current_class is None and num_students <= self.available_computers:
            self.current_class = class_name
            self.subject = subject
            self.available_computers -= num_students
            self.assigned_time = time.strftime("%H:%M:%S")
            self.time_duration = class_duration_hours
            self.total_students = num_students

            if 'status_text' in globals():
                status_text.insert(tk.END, f"✅ Class '{class_name}' (Subject: {subject}) assigned to Lab {self.lab_id} for {class_duration_hours} hours.\n")

            self.assignment_thread = threading.Thread(target=self.run_class, args=(class_name, class_duration_hours * 3600))
            self.assignment_thread.start()

            self.save_to_csv()
            update_lab_status()
        else:
            if 'status_text' in globals():
                status_text.insert(tk.END, f"⚠ Lab {self.lab_id} is occupied or doesn't have enough computers.\n")

    def run_class(self, class_name, class_duration):
        time.sleep(class_duration)
        self.current_class = None
        self.available_computers = self.num_computers

        if 'status_text' in globals():
            status_text.insert(tk.END, f"⏳ Class '{class_name}' completed in Lab {self.lab_id}.\n")

        update_lab_status()

    def save_to_csv(self):
        with open("lab_data.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([self.lab_id, self.current_class, self.subject, self.assigned_time, self.time_duration, self.total_students])

# --------------------- Lab Management System ---------------------
class LabManagementSystem:
    def __init__(self, lab_capacity_list, software_list):
        self.labs = [Lab(i + 1, num_computers, software_list[i]) for i, num_computers in enumerate(lab_capacity_list)]
        self.save_lab_capacities(software_list)

    def assign_class_to_lab(self, class_name, subject, num_students, class_duration_hours):
        for lab in self.labs:
            if lab.current_class is None and num_students <= lab.available_computers:
                lab.assign_class(class_name, subject, num_students, class_duration_hours)
                return
        if 'status_text' in globals():
            status_text.insert(tk.END, "❌ No available labs with enough capacity at the moment.\n")

    def get_occupied_and_vacant_labs(self):
        occupied = sum(1 for lab in self.labs if lab.current_class is not None)
        vacant = len(self.labs) - occupied
        return occupied, vacant

    def save_lab_capacities(self, software_list):
        with open("lab_capacity.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Lab ID", "Total Computers", "Softwares Installed"])
            for i, lab in enumerate(self.labs):
                writer.writerow([lab.lab_id, lab.num_computers, ", ".join(software_list[i])])

# --------------------- UI Functions ---------------------
def setup_lab_entries():
    """Dynamically creates entry fields for lab capacities and software lists with labels."""
    global lab_capacity_entries, software_entries

    num_labs = int(num_labs_entry.get())

    # Clear previous widgets
    for widget in lab_setup_window.winfo_children():
        widget.destroy()

    tk.Label(lab_setup_window, text="Enter Lab Capacities:").grid(row=0, column=0)
    tk.Label(lab_setup_window, text="Softwares Installed:").grid(row=0, column=1)

    lab_capacity_entries = []
    software_entries = []

    for i in range(num_labs):
        tk.Label(lab_setup_window, text=f"Enter Lab {i + 1} Capacity:").grid(row=i + 1, column=0, sticky=tk.W)
        entry = tk.Entry(lab_setup_window)
        entry.grid(row=i + 1, column=1)
        lab_capacity_entries.append(entry)

        tk.Label(lab_setup_window, text=f"Enter Lab {i + 1} Softwares:").grid(row=i + 1, column=2, sticky=tk.W)
        software_entry = tk.Entry(lab_setup_window)
        software_entry.grid(row=i + 1, column=3)
        software_entries.append(software_entry)

    save_button = tk.Button(lab_setup_window, text="Save and Continue", command=save_and_show_data)
    save_button.grid(row=num_labs + 1, column=0, columnspan=4, pady=10)

def save_and_show_data():
    global lab_system, lab_status_text  

    lab_capacity_list = [int(entry.get()) for entry in lab_capacity_entries]
    software_list = [software_entry.get().split(",") for software_entry in software_entries]

    lab_system = LabManagementSystem(lab_capacity_list, software_list)

    if 'lab_status_text' in globals():
        lab_status_text.delete("1.0", tk.END)
        lab_status_text.insert(tk.END, "✅ Lab data saved successfully.\n")

    update_lab_status()
    open_class_assignment_tab()

def update_lab_status():
    if 'lab_system' not in globals():
        return

    occupied, vacant = lab_system.get_occupied_and_vacant_labs()

    if 'lab_status_text' in globals():
        lab_status_text.delete("1.0", tk.END)
        lab_status_text.insert(tk.END, f"📌 Labs Status: {occupied} occupied, {vacant} vacant.\n\n")

        lab_status_text.insert(tk.END, "🔹 Lab Details:\n")
        for lab in lab_system.labs:
            status = "Occupied" if lab.current_class else "Vacant"
            lab_status_text.insert(tk.END, f"Lab {lab.lab_id} - {lab.num_computers} Computers - {status}\n")
            lab_status_text.insert(tk.END, f"Softwares Installed: {', '.join(lab.softwares_installed)}\n\n")

def open_class_assignment_tab():
    lab_setup_window.destroy()
    open_class_assignment_window()

def assign_class():
    """Assigns a class to a lab from UI input."""
    class_name = class_name_entry.get()
    subject = subject_entry.get()
    num_students = int(num_students_entry.get())
    class_duration = int(class_duration_entry.get())

    if 'lab_system' in globals():
        lab_system.assign_class_to_lab(class_name, subject, num_students, class_duration)

def open_class_assignment_window():
    global class_window, subject_entry, class_name_entry, num_students_entry, class_duration_entry, status_text  

    class_window = tk.Tk()
    class_window.title("Class Assignment")

    tk.Label(class_window, text="Enter Software Required:").grid(row=0, column=0, sticky=tk.W)
    subject_entry = tk.Entry(class_window)
    subject_entry.grid(row=0, column=1)

    tk.Label(class_window, text="Enter Class Name:").grid(row=1, column=0, sticky=tk.W)
    class_name_entry = tk.Entry(class_window)
    class_name_entry.grid(row=1, column=1)

    tk.Label(class_window, text="Enter Number of Students:").grid(row=2, column=0, sticky=tk.W)
    num_students_entry = tk.Entry(class_window)
    num_students_entry.grid(row=2, column=1)

    tk.Label(class_window, text="Enter Class Duration (Hours):").grid(row=3, column=0, sticky=tk.W)
    class_duration_entry = tk.Entry(class_window)
    class_duration_entry.grid(row=3, column=1)

    assign_class_button = tk.Button(class_window, text="Assign Class", command=assign_class)
    assign_class_button.grid(row=4, column=0, columnspan=2, sticky=tk.W)

    status_text = tk.Text(class_window, height=10, width=50)
    status_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    class_window.mainloop()

# --------------------- Lab Setup Window ---------------------
lab_setup_window = tk.Tk()
lab_setup_window.title("Lab Setup")

tk.Label(lab_setup_window, text="Enter the number of labs:").grid(row=0, column=0, sticky=tk.W)
num_labs_entry = tk.Entry(lab_setup_window)
num_labs_entry.grid(row=0, column=1)

confirm_button = tk.Button(lab_setup_window, text="Confirm", command=setup_lab_entries)
confirm_button.grid(row=1, column=0, columnspan=2)

lab_setup_window.mainloop()
