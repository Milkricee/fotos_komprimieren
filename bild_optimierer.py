import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pillow_avif

# --- 1. Definiere hier deine Ziel-Profile ---
# Der Name des Profils (z.B. "mobil") wird zum Ordnernamen
AUSGABE_PROFILE = {
    "mobil": {"width": 800, "max_kb": 100},
    "web":   {"width": 1920, "max_kb": 300}
}

def process_images_logic(source_base, destination_base, progress_callback):
    """
    Dies ist die Kernlogik zur Bildverarbeitung. Sie durchläuft die Quellordner,
    erstellt die Zielstruktur und optimiert die Bilder.
    """
    try:
        # Zähle zuerst die zu verarbeitenden Bilder für die Fortschrittsanzeige
        total_images = 0
        for _, _, filenames in os.walk(source_base):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    total_images += 1
        
        processed_images = 0

        # os.walk durchläuft rekursiv alle Ordner und Dateien
        for source_dir, _, filenames in os.walk(source_base):
            for filename in filenames:
                # Nur Bilddateien verarbeiten
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue

                source_path = os.path.join(source_dir, filename)
                original_name, _ = os.path.splitext(filename)
                output_filename = f"{original_name}.avif"

                # Update Fortschrittsanzeige
                processed_images += 1
                progress_callback(f"Verarbeite Bild {processed_images} von {total_images}: {filename}")

                with Image.open(source_path) as img:
                    # Für jedes definierte Profil eine Version erstellen
                    for profil_name, profil_config in AUSGABE_PROFILE.items():
                        # Erstellt die finale Ordnerstruktur: Ziel/profil/original_struktur
                        relative_dir = os.path.relpath(source_dir, source_base)
                        destination_folder = os.path.join(destination_base, profil_name, relative_dir)
                        os.makedirs(destination_folder, exist_ok=True)
                        
                        output_path = os.path.join(destination_folder, output_filename)

                        # Bild skalieren
                        profil_breite = profil_config["width"]
                        ratio = profil_breite / float(img.size[0])
                        neue_hoehe = int(float(img.size[1]) * ratio)
                        resized_img = img.resize((profil_breite, neue_hoehe), Image.Resampling.LANCZOS)

                        # Qualität anpassen, um KB-Ziel zu erreichen
                        profil_max_kb = profil_config["max_kb"]
                        for qualitaet in range(85, 40, -5):
                            resized_img.save(output_path, 'AVIF', quality=qualitaet)
                            file_size_kb = os.path.getsize(output_path) / 1024
                            if file_size_kb <= profil_max_kb:
                                break
        
        messagebox.showinfo("Fertig", f"Die Verarbeitung von {total_images} Bildern ist abgeschlossen!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{e}")
    finally:
        progress_callback("Bereit.")


# --- Grafische Benutzeroberfläche (GUI) ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Bild-Optimierer v1.0")
        self.root.geometry("600x250") # Fenstergröße
        self.root.resizable(False, False)

        self.source_path = ""

        # UI Elemente erstellen
        self.label = tk.Label(root, text="Wähle den Ordner mit den Originalbildern aus.", pady=10, font=("Helvetica", 12))
        self.label.pack()

        self.btn_source = tk.Button(root, text="1. Quellordner auswählen", command=self.select_source, width=30)
        self.btn_source.pack(pady=5)
        self.lbl_source = tk.Label(root, text="Kein Ordner ausgewählt", fg="red", wraplength=580)
        self.lbl_source.pack()
        
        self.btn_start = tk.Button(root, text="2. Komprimieren & Speichern unter...", command=self.start_processing, font=("Helvetica", 10, "bold"), bg="#4CAF50", fg="white", width=30)
        self.btn_start.pack(pady=15)

        self.status_label = tk.Label(root, text="Bereit.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def select_source(self):
        """Öffnet den Dialog zur Auswahl des Quellordners."""
        path = filedialog.askdirectory(title="Wähle den Ordner mit den Originalbildern")
        if path:
            self.source_path = path
            self.lbl_source.config(text=path, fg="green")

    def start_processing(self):
        """
        Startet den Prozess: Prüft die Quelle, fragt nach dem Ziel
        und ruft dann die Verarbeitungslogik auf.
        """
        if not self.source_path:
            messagebox.showwarning("Achtung", "Bitte wähle zuerst einen Quellordner aus.")
            return

        destination_path = filedialog.askdirectory(title="Wähle den Zielordner, in dem die 'mobil' und 'web' Ordner erstellt werden sollen")
        
        if destination_path:
            self.btn_start.config(state=tk.DISABLED, text="Verarbeite...")
            self.btn_source.config(state=tk.DISABLED)
            
            process_images_logic(self.source_path, destination_path, self.update_status)
            
            self.btn_start.config(state=tk.NORMAL, text="2. Komprimieren & Speichern unter...")
            self.btn_source.config(state=tk.NORMAL)


if __name__ == '__main__':
    # Erstellt und startet das Hauptfenster der App
    main_window = tk.Tk()
    app = App(main_window)
    main_window.mainloop()
