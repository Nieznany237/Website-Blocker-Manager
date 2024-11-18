import ctypes
import os
import subprocess
import customtkinter as ctk
from datetime import datetime
import tkinter

# Program settings
ENABLE_ADMIN_CHECK = True  # Admin check mode flag
DEFAULT_IP = "127.0.0.1"  # Default IP address

# Function to check administrator rights
def check_admin_rights():
    if not ENABLE_ADMIN_CHECK:
        return True  # If admin check mode is disabled, assume full permissions
    try:
        return os.getuid() == 0  # Unix
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # Windows
    
# Path to the test file (instead of the real hosts file)
HOST_FILE_PATH = r"C:\Windows\System32\drivers\etc\hosts"

# Application class
class HostsEditorApp(ctk.CTk):
    def __init__(self, admin_mode):
        super().__init__()
        self.admin_mode = admin_mode
        self.title("Website Blocker Manager")
        self.geometry("800x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark") #system, dark, light

        # File path
        self.file_path = HOST_FILE_PATH  # You can set any path

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # User section
        self.user_frame = ctk.CTkFrame(self.main_frame)
        self.user_frame.pack(pady=10, padx=10, fill="x")
        
        # IP address field
        ctk.CTkLabel(self.user_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ip_entry = ctk.CTkEntry(self.user_frame, width=150)
        self.ip_entry.insert(0, DEFAULT_IP)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.ip_entry.bind("<KeyRelease>", self.validate_ip_input)

        # Website field
        ctk.CTkLabel(self.user_frame, text="Website:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.site_entry = ctk.CTkEntry(self.user_frame, width=300)
        self.site_entry.grid(row=0, column=3, padx=5, pady=5)

        # Frame for buttons and checkbox
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.pack(pady=10, padx=10, fill="x")

        # Remove options
        self.remove_all_var = ctk.BooleanVar(value=True)
        self.remove_all_checkbox = ctk.CTkCheckBox(
            self.action_frame,
            text="Remove all related entries",
            state="normal" if self.admin_mode else "disabled",
            variable=self.remove_all_var
        )
        self.remove_all_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Buttons
        self.add_button = ctk.CTkButton(
            self.action_frame,
            text="Block",
            border_color="#8f0000",
            border_width=2,
            fg_color = "#d10000",
            hover_color = "#9e0000",
            command=self.add_site,
            state="normal" if self.admin_mode else "disabled",
            width=92
        )
        self.add_button.grid(row=0, column=1, padx=10, pady=5)

        self.remove_button = ctk.CTkButton(
            self.action_frame,
            text="Unblock",
            command=self.remove_site,
            state="normal" if self.admin_mode else "disabled",
            width=92
        )
        self.remove_button.grid(row=0, column=2, padx=10, pady=5)
        
        # Save changes button
        self.save_button = ctk.CTkButton(
            self.action_frame,
            text="Save File",
            command=self.save_to_file,
            state="normal" if self.admin_mode else "disabled",
            width=92
        )
        self.save_button.grid(row=0, column=3, padx=10, pady=5)

        self.backup_button = ctk.CTkButton(
            self.action_frame,
            text="Create Backup",
            command=self.create_backup,
            state="normal" if self.admin_mode else "disabled",
            width=92
        )
        self.backup_button.grid(row=0, column=4, padx=10, pady=5)

        self.DNSFlushButton = ctk.CTkButton(
            self.action_frame,
            text="DNS flush",
            command=self.DNSFlush,
            state="normal" if self.admin_mode else "disabled",
            width=92
        )
        self.DNSFlushButton.grid(row=0, column=5, padx=10, pady=5)

        # Preview window
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(self.preview_frame, text=f"Preview of hosts file: {HOST_FILE_PATH}").pack(pady=5, anchor="w")
        self.textbox = ctk.CTkTextbox(self.preview_frame, wrap="none", corner_radius=0)
        self.textbox.pack(pady=0, padx=0, fill="both", expand=True)

        # Disable modifications in the preview window
        self.textbox.bind("<Key>", lambda e: "break")  # Disable keyboard input
        self.textbox.bind("<Button-1>", lambda e: "break")  # Disable mouse clicks

        self.load_file_content()

        # Program information
        self.version_label = ctk.CTkLabel(
            master=self.main_frame,
            text="By @Nieznany237 | Version 1.1c 18.11.2024 | First release: 16.11.2024",
            text_color="#7E7E7E"
        )
        self.version_label.pack(side="right", pady=0)

        # Warning for read-only mode
        if not self.admin_mode:
            warning_label = ctk.CTkLabel(
                self.main_frame,
                text="Read-only mode: No administrator rights",
                text_color="red"
            )
            warning_label.pack(pady=0)

    
    # IP address input validation + flag
    def validate_ip_input(self, event, flag=True):
        if flag:
            valid_chars = "0123456789ABCDEF:."
            input_text = self.ip_entry.get().upper()
            filtered_text = "".join(char for char in input_text if char in valid_chars)
            self.ip_entry.delete(0, "end")
            self.ip_entry.insert(0, filtered_text)
    
    # Function to load file content
    def load_file_content(self):
        try:
            with open(HOST_FILE_PATH, "r") as file:
                lines = file.readlines()
            
            self.textbox.delete("1.0", "end")
            for line in lines:
                if line.strip().startswith("#") or not line.strip():
                    continue  # Ignore comments and empty lines
                self.textbox.insert("end", line)
        except FileNotFoundError:
            self.textbox.insert("1.0", "File does not exist.")

    # Function to add a site
    def add_site(self):
        ip = self.ip_entry.get().strip()
        site = self.site_entry.get().strip()
        if ip and site:
            current_content = self.textbox.get("1.0", "end").strip()
            if f"{ip} {site}" not in current_content:
                self.textbox.insert("end", f"\n{ip} {site}")
                self.site_entry.delete(0, "end")
    
    # Function to remove a site
    def remove_site(self):
        ip = self.ip_entry.get().strip()
        site = self.site_entry.get().strip()
        if site:
            lines = self.textbox.get("1.0", "end").strip().split("\n")
            if self.remove_all_var.get():
                # Remove all entries related to the site
                updated_lines = [line for line in lines if site not in line]
            else:
                # Remove only the entry with the specific IP and site
                updated_lines = [line for line in lines if line.strip() != f"{ip} {site}"]
            
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", "\n".join(updated_lines))
            self.site_entry.delete(0, "end")
    
    def save_to_file(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(self.textbox.get("1.0", "end").strip())  # Save content from the preview window
            tkinter.messagebox.showinfo("Success", "Changes saved successfully!")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to save the file: {e}")

    def DNSFlush(self):
        try:
            # Wykonanie komendy w terminalu
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                shell=True
            )
            # Wyświetlenie wyniku w oknie
            if result.returncode == 0:
                tkinter.messagebox.showinfo("Success", "DNS Cache flushed successfully!")
            else:
                tkinter.messagebox.showerror("Error", f"Failed to flush DNS: {result.stderr}")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Exception: {str(e)}")

    def create_backup(self):
        try:
            # Create user directory path
            username = os.getenv("USERNAME")
            backup_dir = f"C:\\Users\\{username}\\Documents\\HostsBackup"
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup file name
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_path = os.path.join(backup_dir, f"hosts_{timestamp}.bak")

            # Save backup
            with open(backup_path, "w", encoding="utf-8") as backup_file:
                backup_file.write(self.textbox.get("1.0", "end").strip())  # Save content from the preview window
            
            tkinter.messagebox.showinfo("Success", f"Backup created:\n{backup_path}")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to create backup: {e}")


# Check administrator rights
is_admin = check_admin_rights()

# Create application
app = HostsEditorApp(admin_mode=is_admin)
app.mainloop()
