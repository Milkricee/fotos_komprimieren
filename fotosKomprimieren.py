import os
from PIL import Image
import pillow_avif
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. Definiere hier deine Ziel-Profile ---
# Der Name des Profils (z.B. "mobil") wird zum Ordnernamen
AUSGABE_PROFILE = {
    "mobil": { "width": 800, "max_kb": 100 },
    "web":   { "width": 1920, "max_kb": 300 }
}

# --- 2. Passe hier deine Ordner an ---
SOURCE_BASE_DIR = 'C:/Users/Daniel/Desktop/Programming/wanderwise/public'
DESTINATION_BASE_DIR = os.path.join(os.path.expanduser('~'), 'Downloads', 'optimierte_bilder')

def create_structured_images():
    if not os.path.isdir(SOURCE_BASE_DIR):
        print(f"❌ Fehler: Der Quellordner '{SOURCE_BASE_DIR}' wurde nicht gefunden.")
        return

    print(f"Quelle: {SOURCE_BASE_DIR}\nZiel:   {DESTINATION_BASE_DIR}")
    print("\n--- Beginne Verarbeitung ---")

    for source_dir, _, filenames in os.walk(SOURCE_BASE_DIR):
        for filename in filenames:
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            source_path = os.path.join(source_dir, filename)
            original_name, _ = os.path.splitext(filename)
            output_filename = f"{original_name}.avif"

            try:
                with Image.open(source_path) as img:
                    print(f"\n📄 Verarbeite: {os.path.relpath(source_path, SOURCE_BASE_DIR)}")

                    for profil_name, profil_config in AUSGABE_PROFILE.items():
                        # Erstelle die finale Ordnerstruktur: Ziel/profil/original_struktur
                        relative_dir = os.path.relpath(source_dir, SOURCE_BASE_DIR)
                        destination_folder = os.path.join(DESTINATION_BASE_DIR, profil_name, relative_dir)
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
                                print(f"  ✔️ '{profil_name}' erstellt ({file_size_kb:.1f} KB)")
                                break
                        else:
                             print(f"  ⚠️ '{profil_name}' Ziel verfehlt ({file_size_kb:.1f} KB)")

            except Exception as e:
                print(f"⚠️ Konnte '{filename}' nicht verarbeiten. Grund: {e}")

    print("\n--- Verarbeitung abgeschlossen ---")

if __name__ == '__main__':
    create_structured_images()
    
AUSGABE_PROFILE = {
    "mobil": { "width": 800, "max_kb": 100 },
    "web":   { "width": 1920, "max_kb": 300 }
}

def process_images_logic(source_base, destination_base):
    """Dies ist deine Kernlogik, jetzt als separate Funktion."""
    if not source_base or not destination_base:
        messagebox.showerror("Fehler", "Bitte wähle einen Quell- und einen Zielordner aus.")
        return

    try:
        # Hier beginnt der bekannte Code von vorhin...
        for source_dir, _, filenames in os.walk(source_base):
            for filename in filenames:
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue

                source_path = os.path.join(source_dir, filename)
                original_name, _ = os.path.splitext(filename)
                output_filename = f"{original_name}.avif"

                with Image.open(source_path) as img:
                    for profil_name, profil_config in AUSGABE_PROFILE.items():
                        relative_dir = os.path.relpath(source_dir, source_base)
                        destination_folder = os.path.join(destination_base, profil_name, relative_dir)
                        os.makedirs(destination_folder, exist_ok=True)
                        
                        output_path = os.path.join(destination_folder, output_filename)
                        
                        profil_breite = profil_config["width"]
                        ratio = profil_breite / float(img.size[0])
                        neue_hoehe = int(float(img.size[1]) * ratio)
                        resized_img = img.resize((profil_breite, neue_hoehe), Image.Resampling.LANCZOS)
                        
                        profil_max_kb = profil_config["max_kb"]
                        for qualitaet in range(85, 40, -5):
                            resized_img.save(output_path, 'AVIF', quality=qualitaet)
                            file_size_kb = os.path.getsize(output_path) / 1024
                            if file_size_kb <= profil_max_kb:
                                break
        
        messagebox.showinfo("Fertig", "Die Verarbeitung der Bilder ist abgeschlossen!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{e}")


# --- HIER BEGINNT DER NEUE GUI-CODE ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Bild-Optimierer")
        self.root.geometry("500x250") # Fenstergröße

        self.source_path = ""
        self.dest_path = ""

        # UI Elemente erstellen
        self.label = tk.Label(root, text="Wähle die Ordner aus und starte die Optimierung.", pady=10)
        self.label.pack()

        self.btn_source = tk.Button(root, text="Quellordner auswählen", command=self.select_source)
        self.btn_source.pack(pady=5)
        self.lbl_source = tk.Label(root, text="Kein Ordner ausgewählt", fg="red")
        self.lbl_source.pack()

        self.btn_dest = tk.Button(root, text="Zielordner auswählen", command=self.select_dest)
        self.btn_dest.pack(pady=5)
        self.lbl_dest = tk.Label(root, text="Kein Ordner ausgewählt", fg="red")
        self.lbl_dest.pack()
        
        self.btn_start = tk.Button(root, text="Verarbeitung starten", command=self.start_processing, font=("Helvetica", 10, "bold"))
        self.btn_start.pack(pady=20)

    def select_source(self):
        # Öffnet den Dialog zur Ordnerauswahl
        path = filedialog.askdirectory(title="Wähle den Quellordner aus")
        if path:
            self.source_path = path
            self.lbl_source.config(text=path, fg="green")

    def select_dest(self):
        path = filedialog.askdirectory(title="Wähle den Zielordner aus")
        if path:
            self.dest_path = path
            self.lbl_dest.config(text=path, fg="green")

    def start_processing(self):
        # Ruft die eigentliche Verarbeitungsfunktion auf
        process_images_logic(self.source_path, self.dest_path)


if __name__ == '__main__':
    # Erstellt und startet das Hauptfenster der App
    main_window = tk.Tk()
    app = App(main_window)
    main_window.mainloop()