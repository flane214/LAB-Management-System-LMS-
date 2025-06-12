import tkinter as tk
import threading
import time
import csv
import datetime

SOFTWARE_OPTIONS = [
    "ANACONDA3", "DEV C++", "TURBO C++", "PYTHON", "VS CODE", "JAVA", "JDK",
    "TALLY PRIME", "GOOGLE CHROME", "R STUDIO", "MYSQL SERVER AND WORKBENCH",
    "ORACLE VM VIRTUAL BOX", "CISCO PACKET TRACER", "XCODE", "ADOBE READER XI",
    "AUTOCAD 2024", "LINUX (UBUNTU - CMD BASED)", "WINRAR", "NODEJS", "ECLIPCE IDE",
    "LINUX - UBUNTU", "TABLEAU", "MATLAB R2024b"
]

# --------------------- Lab Setup Function ---------------------
def setup_lab_entries():
    global lab_capacity_entries, software_vars
    num_labs = int(num_labs_entry.get())

    for widget in lab_setup_window.winfo_children():
        widget.destroy()

    tk.Label(lab_setup_window, text="Enter Lab Capacities and Select Installed Software:").grid(row=0, column=0, columnspan=3)

    lab_capacity_entries = []
    software_vars = []

    for i in range(num_labs):
        tk.Label(lab_setup_window, text=f"Lab {i + 1} Capacity:").grid(row=i*2, column=0, sticky=tk.W)
        entry = tk.Entry(lab_setup_window)
        entry.grid(row=i*2, column=1)
        lab_capacity_entries.append(entry)

        vars_row = []
        frame = tk.LabelFrame(lab_setup_window, text=f"Software for Lab {i+1}")
        frame.grid(row=i*2+1, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        for j, software in enumerate(SOFTWARE_OPTIONS):
            var = tk.IntVar()
            cb = tk.Checkbutton(frame, text=software, variable=var)
            cb.grid(row=j//4, column=j%4, sticky="w")
            vars_row.append((var, software))
        software_vars.append(vars_row)

    tk.Button(lab_setup_window, text="Save & Continue", command=save_and_show_data).grid(row=num_labs*3, column=0, columnspan=3, pady=10)

# --------------------- Lab & System Classes ---------------------
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
                status_text.insert(tk.END, f"✅ Class '{class_name}' (Software: {subject}) assigned to Lab {self.lab_id} for {class_duration_hours} hours.
")

            self.assignment_thread = threading.Thread(target=self.run_class, args=(class_name, class_duration_hours * 3600))
            self.assignment_thread.start()

            update_lab_status()
        else:
            if 'status_text' in globals():
                status_text.insert(tk.END, f"⚠ Lab {self.lab_id} is occupied or doesn't have enough computers.
")

    def run_class(self, class_name, class_duration):
        time.sleep(class_duration)
        self.current_class = None
        self.available_computers = self.num_computers

        def update_ui():
            if 'status_text' in globals():
                status_text.insert(tk.END, f"⏳ Class '{class_name}' completed in Lab {self.lab_id}.
")
            update_lab_status()

        if 'status_text' in globals() and status_text.winfo_exists():
            status_text.after(0, update_ui)

    def get_remaining_time(self):
        if self.current_class and self.assigned_time:
            today = datetime.datetime.now().date()
            assigned_dt = datetime.datetime.combine(today, datetime.datetime.strptime(self.assigned_time, "%H:%M:%S").time())
            now = datetime.datetime.now()
            elapsed = (now - assigned_dt).total_seconds()
            remaining = self.time_duration * 3600 - elapsed
            if remaining < 0:
                remaining = 0
            return str(datetime.timedelta(seconds=int(remaining)))
        return "-"

    def remove_class(self):
        self.current_class = None
        self.available_computers = self.num_computers
        self.subject = None
        self.assigned_time = None
        self.time_duration = None
        self.total_students = None
        update_lab_status()
        if 'status_text' in globals():
            status_text.insert(tk.END, f"🗑️ Class manually removed from Lab {self.lab_id}.
")

class LabManagementSystem:
    def __init__(self, lab_capacity_list, software_list):
        self.labs = [Lab(i + 1, num_computers, software_list[i]) for i, num_computers in enumerate(lab_capacity_list)]

    def assign_class_to_lab(self, class_name, required_software, num_students, class_duration_hours):
        for lab in self.labs:
            if (
                lab.current_class is None and
                num_students <= lab.available_computers and
                all(software.strip().lower() in (s.lower() for s in lab.softwares_installed) for software in required_software)
            ):
                lab.assign_class(class_name, ", ".join(required_software), num_students, class_duration_hours)
                return

        if 'status_text' in globals():
            status_text.insert(tk.END, "❌ No suitable labs found with required software and capacity.
")

# --------------------- Save and Show Data ---------------------
def save_and_show_data():
    global lab_system
    lab_capacity_list = [int(entry.get()) for entry in lab_capacity_entries]
    software_list = [[software for var, software in row if var.get() == 1] for row in software_vars]
    lab_system = LabManagementSystem(lab_capacity_list, software_list)
    update_lab_status()
    open_class_assignment_tab()

# --------------------- Class Assignment Tab ---------------------
def open_class_assignment_tab():
    global status_text, lab_status_text, software_checklist_vars
    top = tk.Toplevel(root)
    top.title("Assign Class")

    tk.Label(top, text="Class Name: ").grid(row=0, column=0)
    class_name_entry = tk.Entry(top)
    class_name_entry.grid(row=0, column=1)

    tk.Label(top, text="No. of Students: ").grid(row=1, column=0)
    students_entry = tk.Entry(top)
    students_entry.grid(row=1, column=1)

    tk.Label(top, text="Duration (hours): ").grid(row=2, column=0)
    duration_entry = tk.Entry(top)
    duration_entry.grid(row=2, column=1)

    tk.Label(top, text="Select Required Software:").grid(row=3, column=0, columnspan=2)

    software_checklist_vars = []
    software_frame = tk.LabelFrame(top, text="Required Software")
    software_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    for i, software in enumerate(SOFTWARE_OPTIONS):
        var = tk.IntVar()
        cb = tk.Checkbutton(software_frame, text=software, variable=var)
        cb.grid(row=i//4, column=i%4, sticky="w")
        software_checklist_vars.append((var, software))

    def assign_class():
        class_name = class_name_entry.get()
        required_software = [name for var, name in software_checklist_vars if var.get() == 1]
        students = int(students_entry.get())
        duration = float(duration_entry.get())
        lab_system.assign_class_to_lab(class_name, required_software, students, duration)

    tk.Button(top, text="Assign", command=assign_class).grid(row=5, column=0, columnspan=2, pady=10)

    lab_status_text = tk.Text(top, height=10, width=70)
    lab_status_text.grid(row=6, column=0, columnspan=2)

    status_text = tk.Text(top, height=6, width=70)
    status_text.grid(row=7, column=0, columnspan=2)

    update_lab_status()

# --------------------- Fix update_lab_status ---------------------
def update_lab_status():
    if 'lab_status_text' in globals():
        lab_status_text.delete(1.0, tk.END)
        for lab in lab_system.labs:
            status = "Occupied" if lab.current_class else "Vacant"
            lab_status_text.insert(
                tk.END,
                f"Lab {lab.lab_id} | {lab.available_computers}/{lab.num_computers} free | Class: {lab.current_class or '-'} | Software: {lab.subject or '-'} | Time Left: {lab.get_remaining_time()}\n"
            )

# --------------------- Cleaned Lab Dashboard ---------------------
def open_lab_dashboard():
    dashboard = tk.Toplevel(root)
    dashboard.title("Live Lab Dashboard")
    dashboard.geometry("800x500")

    canvas = tk.Canvas(dashboard)
    scrollbar = tk.Scrollbar(dashboard, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    lab_cards = []

    def refresh():
        for card in lab_cards:
            card.destroy()
        lab_cards.clear()

        if 'lab_system' in globals():
            for lab in lab_system.labs:
                if lab.current_class:
                    if lab.available_computers == 0:
                        status = "Occupied"
                        color = "red"
                    else:
                        status = "Partial"
                        color = "orange"
                else:
                    status = "Vacant"
                    color = "green"

                remaining = lab.get_remaining_time()
                frame = tk.Frame(scrollable_frame, bd=2, relief=tk.RIDGE, padx=10, pady=10, bg="#f9f9f9")
                frame.pack(padx=10, pady=10, fill="x")

                tk.Label(frame, text=f"Lab {lab.lab_id}", font=("Arial", 14, "bold"), fg=color).pack(anchor="w")
                tk.Label(frame, text=f"Status: {status}", font=("Arial", 12), fg=color).pack(anchor="w")
                tk.Label(frame, text=f"Usage: {lab.num_computers - lab.available_computers} / {lab.num_computers} computers", font=("Arial", 11)).pack(anchor="w")
                tk.Label(frame, text=f"Class: {lab.current_class or 'None'}", font=("Arial", 11)).pack(anchor="w")
                tk.Label(frame, text=f"Remaining Time: {remaining}", font=("Arial", 11)).pack(anchor="w")
                tk.Label(frame, text=f"Software: {', '.join(lab.softwares_installed)}", font=("Arial", 10), wraplength=700, justify="left").pack(anchor="w")

                if lab.current_class:
                    tk.Button(frame, text="❌ Remove Class", fg="white", bg="red",
                              command=lambda l=lab: [l.remove_class(), refresh()]).pack(anchor="e", pady=5)

                lab_cards.append(frame)

        dashboard.after(5000, refresh)

    refresh()

# --------------------- Main Window ---------------------
root = tk.Tk()
root.title("Lab Management Dashboard")

# UI Elements
tk.Label(root, text="Enter number of labs:").grid(row=0, column=0)
num_labs_entry = tk.Entry(root)
num_labs_entry.grid(row=0, column=1)

tk.Button(root, text="Proceed", command=setup_lab_entries).grid(row=0, column=2, padx=10)

lab_setup_window = tk.Frame(root)
lab_setup_window.grid(row=1, column=0, columnspan=3)

tk.Button(root, text="📊 Open Dashboard", command=open_lab_dashboard).grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
