import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, UnidentifiedImageError
import pillow_avif  # Stellt sicher, dass AVIF unterstützt wird

# --- Zielprofile definieren ---
AUSGABE_PROFILE = {
    "mobil": {"width": 800, "max_kb": 100},
    "web":   {"width": 1920, "max_kb": 300}
}

# --- Unterstützte Formate (auch Input) ---
SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.heic', '.avif', '.webp',
    '.bmp', '.tif', '.tiff', '.gif'
)

def process_images_logic(source_base, destination_base, progress_callback):
    files_to_process = []
    for filename in os.listdir(source_base):
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):
            files_to_process.append(filename)

    total_images = len(files_to_process)
    if total_images == 0:
        messagebox.showinfo("Information", "Keine unterstützten Bilddateien im gewählten Ordner gefunden.")
        progress_callback("Bereit.")
        return

    failed_files = []
    processed_count = 0

    for i, filename in enumerate(files_to_process, 1):
        progress_callback(f"Verarbeite {i}/{total_images}: {filename}")
        source_path = os.path.join(source_base, filename)

        try:
            with Image.open(source_path) as img:
                img.load()  # Stelle sicher, dass das Bild geladen ist

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                name_stem, _ = os.path.splitext(filename)
                output_filename = f"{name_stem}.avif"

                for profil_name, config in AUSGABE_PROFILE.items():
                    dest_folder = os.path.join(destination_base, profil_name)
                    os.makedirs(dest_folder, exist_ok=True)
                    output_path = os.path.join(dest_folder, output_filename)

                    # Resize, falls nötig
                    if img.width > config["width"]:
                        ratio = config["width"] / float(img.width)
                        new_height = int(img.height * ratio)
                        resized_img = img.resize((config["width"], new_height), Image.Resampling.LANCZOS)
                    else:
                        resized_img = img

                    # Qualität iterativ anpassen
                    for quality in range(85, 40, -5):
                        resized_img.save(output_path, 'AVIF', quality=quality)
                        if os.path.getsize(output_path) / 1024 <= config["max_kb"]:
                            break

            processed_count += 1

        except UnidentifiedImageError:
            failed_files.append(f"{filename}: Bildformat konnte nicht erkannt werden.")
        except Exception as e:
            failed_files.append(f"{filename}: {str(e)}")

    # Ergebnis anzeigen
    final_msg = f"{processed_count} von {total_images} Bildern erfolgreich verarbeitet."
    if failed_files:
        error_list = "\n".join(failed_files)
        messagebox.showwarning("Verarbeitung abgeschlossen mit Fehlern",
                               f"{final_msg}\n\nFehlerhafte Dateien:\n\n{error_list}")
    else:
        messagebox.showinfo("Fertig", final_msg)

    progress_callback("Bereit.")

# --- GUI ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Bild-Optimierer 2025")
        self.root.geometry("600x250")
        self.root.resizable(False, False)

        self.source_path = ""

        tk.Label(root, text="Wähle einen Ordner mit Bildern aus:", pady=10, font=("Helvetica", 12)).pack()

        self.btn_source = tk.Button(root, text="1. Quellordner auswählen", command=self.select_source, width=30)
        self.btn_source.pack(pady=5)

        self.lbl_source = tk.Label(root, text="Kein Ordner ausgewählt", fg="red", wraplength=580)
        self.lbl_source.pack()

        self.btn_start = tk.Button(root, text="2. Komprimieren & Speichern unter...",
                                   command=self.start_processing, font=("Helvetica", 10, "bold"),
                                   bg="#4CAF50", fg="white", width=30)
        self.btn_start.pack(pady=15)

        self.status_label = tk.Label(root, text="Bereit.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def select_source(self):
        path = filedialog.askdirectory(title="Quellordner mit Bildern auswählen")
        if path:
            self.source_path = path
            self.lbl_source.config(text=path, fg="green")

    def start_processing(self):
        if not self.source_path:
            messagebox.showwarning("Fehler", "Bitte wähle zuerst einen Quellordner aus.")
            return

        destination_path = filedialog.askdirectory(title="Zielordner für 'mobil' & 'web'-Ordner wählen")
        if destination_path:
            self.btn_start.config(state=tk.DISABLED, text="Verarbeite...")
            self.btn_source.config(state=tk.DISABLED)

            process_images_logic(self.source_path, destination_path, self.update_status)

            self.btn_start.config(state=tk.NORMAL, text="2. Komprimieren & Speichern unter...")
            self.btn_source.config(state=tk.NORMAL)


if __name__ == '__main__':
    main_window = tk.Tk()
    app = App(main_window)
    main_window.mainloop()
