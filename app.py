import customtkinter as ctk
import json
import os

# Set UI Theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class OverlayController(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("League of Legends Overlay Controller")
        self.geometry("450x1000")
        self.resizable(False, False)

        # File path for JSON data
        self.json_path = "data.json"

        self.is_loaded = False # Flag to indicate if data has been loaded
        self.current_streak = 0 # win streak counter

        # --- RANK SECTION ---
        self.rank_frame = ctk.CTkFrame(self)
        self.rank_frame.pack(padx=20, pady=(15, 0), fill="x")

        self.rank_label = ctk.CTkLabel(self.rank_frame, text="Current Rank", font=("Arial", 16, "bold"))
        self.rank_label.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        self.rank_list = ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]
        self.division_list = ["I", "II", "III", "IV"]

        self.rank_var = ctk.StringVar(value="Unranked")
        self.rank_menu = ctk.CTkOptionMenu(self.rank_frame, values=self.rank_list, variable=self.rank_var, width=150, command=lambda _: self.save_data())
        self.rank_menu.grid(row=1, column=0, padx=10, pady=(0, 10))

        self.division_var = ctk.StringVar(value="I")
        self.division_menu = ctk.CTkOptionMenu(self.rank_frame, values=self.division_list, variable=self.division_var, width=80, command=lambda _: self.save_data())
        self.division_menu.grid(row=1, column=1, padx=10, pady=(0, 10))

        # --- RECORD SECTION ---
        self.record_frame = ctk.CTkFrame(self)
        self.record_frame.pack(padx=20, pady=15, fill="x")
        
        self.record_type_var = ctk.StringVar(value="Weekly Record")
        self.record_type_menu = ctk.CTkOptionMenu(
            self.record_frame, 
            values=["Daily Record", "Weekly Record", "Monthly Record"],
            variable=self.record_type_var,
            font=("Arial", 14, "bold"),
            width=180,
            command=lambda _: self.save_data()
        )
        self.record_type_menu.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        # Record Headers
        self.wins_label = ctk.CTkLabel(self.record_frame, text="Wins", font=("Arial", 12, "bold"))
        self.wins_label.grid(row=1, column=0, padx=10, pady=(5, 0))
        
        self.losses_label = ctk.CTkLabel(self.record_frame, text="Losses", font=("Arial", 12, "bold"))
        self.losses_label.grid(row=1, column=1, padx=10, pady=(5, 0))

        # --- WINS CONTROL ---
        self.wins_control_frame = ctk.CTkFrame(self.record_frame, fg_color="transparent")
        self.wins_control_frame.grid(row=2, column=0, padx=10, pady=(0, 10))

        self.wins_minus_btn = ctk.CTkButton(self.wins_control_frame, text="-", width=30, font=("Arial", 16, "bold"), command=lambda: self.adjust_score(self.wins_entry, -1))
        self.wins_minus_btn.pack(side="left", padx=(0, 5))

        self.wins_entry = ctk.CTkEntry(self.wins_control_frame, placeholder_text="0", width=100, justify="center")
        self.wins_entry.pack(side="left")

        self.wins_plus_btn = ctk.CTkButton(self.wins_control_frame, text="+", width=30, font=("Arial", 16, "bold"), command=lambda: self.adjust_score(self.wins_entry, 1))
        self.wins_plus_btn.pack(side="left", padx=(5, 0))
        self.wins_entry.bind("<KeyRelease>", lambda event: self.save_data())

        # --- LOSSES CONTROL ---
        self.losses_control_frame = ctk.CTkFrame(self.record_frame, fg_color="transparent")
        self.losses_control_frame.grid(row=2, column=1, padx=10, pady=(0, 10))

        self.losses_minus_btn = ctk.CTkButton(self.losses_control_frame, text="-", width=30, font=("Arial", 16, "bold"), command=lambda: self.adjust_score(self.losses_entry, -1))
        self.losses_minus_btn.pack(side="left", padx=(0, 5))

        self.losses_entry = ctk.CTkEntry(self.losses_control_frame, placeholder_text="0", width=100, justify="center")
        self.losses_entry.pack(side="left")

        self.losses_plus_btn = ctk.CTkButton(self.losses_control_frame, text="+", width=30, font=("Arial", 16, "bold"), command=lambda: self.adjust_score(self.losses_entry, 1))
        self.losses_plus_btn.pack(side="left", padx=(5, 0))
        self.losses_entry.bind("<KeyRelease>", lambda event: self.save_data())

        # --- CHARACTER STATS SECTION ---
        self.chars_frame = ctk.CTkFrame(self)
        self.chars_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.chars_label = ctk.CTkLabel(self.chars_frame, text="Character Stats", font=("Arial", 16, "bold"))
        self.chars_label.pack(pady=10, padx=10, anchor="w")

        # Column Headers
        header_frame = ctk.CTkFrame(self.chars_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(0, 5))

        char_header = ctk.CTkLabel(header_frame, text="Character", font=("Arial", 12, "bold"), width=150, anchor="w")
        char_header.grid(row=0, column=0, padx=5)

        games_header = ctk.CTkLabel(header_frame, text="Games Played", font=("Arial", 12, "bold"), width=100, anchor="center")
        games_header.grid(row=0, column=1, padx=5)

        wins_header = ctk.CTkLabel(header_frame, text="Games Won", font=("Arial", 12, "bold"), width=100, anchor="center")
        wins_header.grid(row=0, column=2, padx=5)

        # Load League of Legends champions dynamically from characerlist file
        try:
            with open("characterlist", "r") as f:
                content = f.read()
                
                # Strip out any brackets, quotes, or line breaks
                clean_content = content.replace("[", "").replace("]", "").replace('"', '').replace("'", "").replace("\n", "")
                
                # Split the text at every comma and remove extra spaces
                self.character_list = [name.strip() for name in clean_content.split(",") if name.strip()]
                
        except FileNotFoundError:
            self.character_list = ["Error: characterlist file missing"]
        
        # Container specifically for the dynamic rows
        self.rows_frame = ctk.CTkFrame(self.chars_frame, fg_color="transparent")
        self.rows_frame.pack(fill="x", pady=0)

        self.char_rows = []
        
        
        for _ in range(3):
            self.add_char_row()

        # Add / Remove Buttons Container
        self.action_btn_frame = ctk.CTkFrame(self.chars_frame, fg_color="transparent")
        self.action_btn_frame.pack(pady=10)

        self.add_btn = ctk.CTkButton(self.action_btn_frame, text="+ Add Character", width=120, command=self.add_char_row)
        self.add_btn.grid(row=0, column=0, padx=10)

        self.remove_btn = ctk.CTkButton(self.action_btn_frame, text="- Remove Character", width=120, fg_color="#b91c1c", hover_color="#991b1b", command=self.remove_char_row)
        self.remove_btn.grid(row=0, column=1, padx=10)

        # --- LAST 5 GAMES SECTION ---
        self.last5_frame = ctk.CTkFrame(self.chars_frame, fg_color="transparent")
        self.last5_frame.pack(fill="x", pady=(15, 0))

        self.last5_label = ctk.CTkLabel(self.last5_frame, text="Last 5 Games History", font=("Arial", 14, "bold"))
        self.last5_label.pack(anchor="w", padx=10, pady=(0, 5))

        self.match_history_vars = []
        for i in range(5):
            row_frame = ctk.CTkFrame(self.last5_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)
            
            char_var = ctk.StringVar(value="None")
            char_menu = ctk.CTkOptionMenu(row_frame, values=["None"] + self.character_list, variable=char_var, width=140, command=lambda _: self.save_data())
            char_menu.pack(side="left", padx=5)
            
            result_var = ctk.StringVar(value="Win")
            result_menu = ctk.CTkOptionMenu(row_frame, values=["Win", "Loss"], variable=result_var, width=80, command=lambda _: self.save_data())
            result_menu.pack(side="left", padx=5)
            
            self.match_history_vars.append({"char": char_var, "result": result_var})

        # --- SETTINGS SECTION ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(padx=20, pady=(10, 0), fill="x")

        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=("Arial", 16, "bold"))
        self.settings_label.pack(pady=0, padx=10, anchor="w")

        self.show_rank_var = ctk.BooleanVar(value=True)
        self.rank_toggle = ctk.CTkCheckBox(
            self.settings_frame,
            text="Show Current Rank",
            variable=self.show_rank_var,
            font=("Arial", 13, "bold"),
            command=self.save_data
        )
        self.rank_toggle.pack(anchor="w", padx=10, pady=(5, 0))

        # Weekly Record Toggle
        self.show_record_var = ctk.BooleanVar(value=True)
        self.record_toggle = ctk.CTkCheckBox(
            self.settings_frame,
            text="Show Weekly Record",
            variable=self.show_record_var,
            font=("Arial", 13, "bold"),
            command=self.save_data
        )
        self.record_toggle.pack(anchor="w", padx=10, pady=(5, 5))

        # Leaderboard Toggle
        self.show_leaderboard_var = ctk.BooleanVar(value=True) 
        self.leaderboard_toggle = ctk.CTkCheckBox(
            self.settings_frame, 
            text="Show Top Characters Leaderboard", 
            variable=self.show_leaderboard_var,
            font=("Arial", 13, "bold"),
            command=self.save_data
        )
        self.leaderboard_toggle.pack(anchor="w", padx=10)

        # Add this right under self.leaderboard_toggle.pack(...)
        self.show_last5_var = ctk.BooleanVar(value=True)
        self.last5_toggle = ctk.CTkCheckBox(
            self.settings_frame,
            text="Show Last 5 Games",
            variable=self.show_last5_var,
            font=("Arial", 13, "bold"),
            command=self.save_data
        )
        self.last5_toggle.pack(anchor="w", padx=10, pady=(5, 5))

        # --- SAVE BUTTON ---
        self.save_btn = ctk.CTkButton(self, text="Update Overlay", command=self.save_data, height=40, font=("Arial", 14, "bold"))
        self.save_btn.pack(padx=20, pady=15, fill="x")

        # Load existing data (will override the 3 default rows if data exists)
        self.load_existing_data()

        self.is_loaded = True  # Set the flag to True after loading data

    def add_char_row(self, name_val=None, games_val="", wins_val=""):
        # Prevent adding an absurd number of rows that break the window height
        if len(self.char_rows) >= 7:
            return 

        row_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=5)

        # Assign a different default character based on row number so they aren't all "Abrams"
        default_index = len(self.char_rows) % len(self.character_list)
        default_name = self.character_list[default_index]

        name_menu = ctk.CTkOptionMenu(row_frame, values=self.character_list, width=150)
        name_menu.set(name_val if name_val else default_name)
        name_menu.grid(row=0, column=0, padx=5)

        games_entry = ctk.CTkEntry(row_frame, placeholder_text="Games", width=100)
        if games_val: games_entry.insert(0, games_val)
        games_entry.grid(row=0, column=1, padx=5)
        games_entry.bind("<KeyRelease>", lambda event: self.save_data())

        char_wins_entry = ctk.CTkEntry(row_frame, placeholder_text="Wins", width=100)
        if wins_val: char_wins_entry.insert(0, wins_val)
        char_wins_entry.grid(row=0, column=2, padx=5)
        char_wins_entry.bind("<KeyRelease>", lambda event: self.save_data())

        self.char_rows.append({
            "frame": row_frame, # Save the frame so we can destroy it later
            "name": name_menu,
            "games": games_entry,
            "wins": char_wins_entry
        })

    def remove_char_row(self):
        # Prevent removing all rows (keep at least 1)
        if len(self.char_rows) > 1:
            last_row = self.char_rows.pop()
            last_row["frame"].destroy()
            self.save_data()

    def save_data(self):
        
        if not getattr(self, "is_loaded", False):
            return
        
        data = {
            "settings": {
                "show_leaderboard": self.show_leaderboard_var.get(),
                "show_record": self.show_record_var.get(),
                "show_rank": self.show_rank_var.get(),
                "show_last5": self.show_last5_var.get()
            },
            "rank_info": {
                "rank": self.rank_var.get(),
                "division": self.division_var.get()
            },
            "weekly_record": {
                "type": self.record_type_var.get(),
                "wins": self.wins_entry.get() or "0",
                "losses": self.losses_entry.get() or "0",
                "streak": getattr(self, "current_streak", 0)  # Save the current streak
            },
            "characters": [],
            "last_5_games": []
        }

        for row in self.char_rows:
            games_str = row["games"].get() or "0"
            wins_str = row["wins"].get() or "0"
            
            try:
                games_num = int(games_str)
                wins_num = int(wins_str)
            except ValueError:
                games_num = 0
                wins_num = 0

            if games_num > 0:
                win_percentage = round((wins_num / games_num) * 100)
                winrate_str = f"{win_percentage}%"
            else:
                winrate_str = "0%"

            data["characters"].append({
                "name": row["name"].get(),
                "games": games_str,
                "wins": wins_str,       
                "winrate": winrate_str 
            })
        
        for match in self.match_history_vars:
            data["last_5_games"].append({
                "char": match["char"].get(),
                "result": match["result"].get()
            })

        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4)
        
        print("Overlay data successfully updated!")

    def load_existing_data(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r") as f:
                    data = json.load(f)
                
                show_rank = data.get("settings", {}).get("show_rank", True)
                self.show_rank_var.set(show_rank)

                rank_info = data.get("rank_info", {})
                self.rank_var.set(rank_info.get("rank", "Unranked"))
                self.division_var.set(rank_info.get("division", "I"))
                
                show_board = data.get("settings", {}).get("show_leaderboard", True)
                self.show_leaderboard_var.set(show_board)

                show_record = data.get("settings", {}).get("show_record", True)
                self.show_record_var.set(show_record)

                show_last5 = data.get("settings", {}).get("show_last5", True)
                self.show_last5_var.set(show_last5)

                record_type = data.get("weekly_record", {}).get("type", "Weekly Record")
                self.record_type_var.set(record_type)

                self.current_streak = data.get("weekly_record", {}).get("streak", 0)

                self.wins_entry.insert(0, data["weekly_record"]["wins"])
                self.losses_entry.insert(0, data["weekly_record"]["losses"])

                loaded_chars = data.get("characters", [])
                loaded_last_5 = data.get("last_5_games", [])
                for i, match_data in enumerate(loaded_last_5):
                    if i < 5:
                        self.match_history_vars[i]["char"].set(match_data.get("char", "None"))
                        self.match_history_vars[i]["result"].set(match_data.get("result", "Win"))
                
                if loaded_chars:
                    # Clear the 3 default rows first
                    while self.char_rows:
                        self.char_rows.pop()["frame"].destroy()
                    
                    # Rebuild rows based on exact JSON data
                    for char_data in loaded_chars:
                        self.add_char_row(
                            name_val=char_data["name"],
                            games_val=char_data["games"],
                            wins_val=char_data.get("wins", "")
                        )

            except Exception as e:
                print(f"Error loading existing JSON: {e}")
    
    def adjust_score(self, entry_widget, amount):
        current_val = entry_widget.get()
        
        try:
            current_num = int(current_val) if current_val else 0
        except ValueError:
            current_num = 0
            
        new_num = current_num + amount
        
        if new_num < 0:
            new_num = 0 
            
        entry_widget.delete(0, "end")
        entry_widget.insert(0, str(new_num))

        # --- STREAK LOGIC ---
        if entry_widget == self.wins_entry:
            if amount > 0:
                self.current_streak += amount
            elif amount < 0: # If you accidentally added a win and need to subtract it
                self.current_streak = max(0, self.current_streak - 1)
        elif entry_widget == self.losses_entry and amount > 0:
            self.current_streak = 0 # Instantly break streak on a loss

        self.save_data()

if __name__ == "__main__":
    app = OverlayController()
    app.mainloop()