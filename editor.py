import tkinter as tk
import json

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def create_editor():
    config = load_config()

    window = tk.Tk()
    window.title("Game Settings Editor")

    entries = {}

    for i, (key, value) in enumerate(config.items()):
        label = tk.Label(window, text=key)
        label.grid(row=i, column=0, padx=10, pady=5)

        entry = tk.Entry(window)
        entry.insert(0, value)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[key] = entry

    def save_and_close():
        for key, entry in entries.items():
            config[key] = int(entry.get()) # Assuming all values are integers for now
        save_config(config)
        window.destroy()

    save_button = tk.Button(window, text="Save and Close", command=save_and_close)
    save_button.grid(row=len(config.items()), columnspan=2, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_editor()
