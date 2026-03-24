import json, os, shutil, subprocess, customtkinter as ctk
from PIL import Image, ImageOps
from tkinter import messagebox, filedialog
from datetime import datetime

# --- CLASE BASE SEGURA PARA DRAG & DROP ---
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    class BaseApp(TkinterDnD.Tk): pass
    DND_DISPONIBLE = True
except Exception:
    class BaseApp(ctk.CTk): pass
    DND_DISPONIBLE = False

class MotorInventario:
    def __init__(self, img_folder, json_file):
        self.img_folder = img_folder
        self.json_file = json_file
        self.abc = list("abcdefghijklmnopqrstuvwxyz")
        self.blacklist = ["logo.jpeg", "banner.jpeg", "logo.jpg", "banner.jpg", "logo.png", "banner.png"]

    def reparar_item(self, item):
        n = item.get('nombre', 'S/N')
        if isinstance(n, list):
            plano = []
            for x in n:
                if isinstance(x, list):
                    for sub in x: plano.append(str(sub))
                else:
                    plano.append(str(x))
            item['nombre'] = plano[:2]
        else:
            item['nombre'] = str(n)
        return item

    def cargar_json(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                try: 
                    datos = json.load(f)
                    return [self.reparar_item(i) for i in datos]
                except: return []
        return []

    def guardar_json(self, datos):
        categorias_validas = ["linia de marca", "linia fina", "linia media", "linia niño/a", "auditoria", "papelera"]
        prefijos = {"linia de marca": "MARC", "linia fina": "FINA", "linia media": "MEDI", "linia niño/a": "NINO", "auditoria": "AUDI", "papelera": "PAPE"}
        for i, item in enumerate(datos):
            item = self.reparar_item(item)
            cat = item.get('cat', 'auditoria').lower()
            if cat not in categorias_validas: cat = "auditoria"
            if not isinstance(item.get('nombre'), list):
                item['id'] = f"{prefijos.get(cat, 'OPT')}-{str(i+1).zfill(3)}"
            item['cat'] = cat
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def generar_nombre_unico(self, inventario):
        nombres_en_uso = set()
        for item in inventario:
            n = item.get('nombre', '')
            if isinstance(n, list): 
                for x in n: nombres_en_uso.add(str(x).lower())
            else: nombres_en_uso.add(str(n).lower())
        v, l = 0, 0
        while True:
            nom = self.abc[l].upper() if v == 0 else f"{self.abc[l].upper()}{v}"
            if nom.lower() not in nombres_en_uso: return nom
            l += 1
            if l >= len(self.abc): l=0; v+=1

    def succionar_archivo(self, ruta_original, inventario):
        nombre_archivo = os.path.basename(ruta_original).lower()
        if nombre_archivo in self.blacklist: return inventario
        if not ruta_original.lower().endswith((".jpeg", ".jpg", ".png", ".webp")): return inventario
        nombre_nuevo = self.generar_nombre_unico(inventario)
        ruta_destino = os.path.join(self.img_folder, f"{nombre_nuevo}.jpeg")
        try:
            # --- MEJORA NINJA: AUTO-ROTACIÓN ---
            img = Image.open(ruta_original)
            img = ImageOps.exif_transpose(img) # <--- Esta línea hace la magia
            img = img.convert("RGB")
            # -----------------------------------
            img.save(ruta_destino, "JPEG", quality=85)
            os.remove(ruta_original)
            inventario.append({
                "nombre": nombre_nuevo, "cat": "auditoria",
                "desc": "Aspirado ninja", "visible_en_auditoria": True
            })
        except Exception as e: print(f"Error: {e}")
        return inventario

class OptiAdmin(BaseApp):
    def __init__(self):
        super().__init__()
        self.title("Opticentro A&E - NINJA MASTER V7.0 👑")
        self.geometry("1550x950")
        ctk.set_appearance_mode("dark")
        
        self.ruta_img = "../img/"
        self.ruta_json = "../inventario.json"
        if not os.path.exists(self.ruta_img): os.makedirs(self.ruta_img)
        
        self.motor = MotorInventario(self.ruta_img, self.ruta_json)
        self.inventario = self.motor.cargar_json()
        self.seleccionados_idx = [] 
        self.img_vacia = ctk.CTkImage(Image.new("RGBA", (1, 1), (40,40,40,255)), size=(420, 420))
        
        self.tabs_info = {
            "auditoria": "🛠 AUDITORÍA", "linia de marca": "Marca", 
            "linia fina": "Fina", "linia media": "Media", 
            "linia niño/a": "Niño/a", "papelera": "🗑 PAPELERA"
        }
        self.setup_ui()
        
        if DND_DISPONIBLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.handle_drop)

    def subir_a_github(self):
        """ Ejecuta comandos de Git desde la raíz del proyecto """
        try:
            self.motor.guardar_json(self.inventario)
            print("🚀 Sincronizando con GitHub desde la raíz...")
            
            # Buscamos la carpeta raíz (un nivel arriba de /tool)
            ruta_raiz = os.path.abspath(os.path.join(os.getcwd(), ".."))
            
            # Ejecutamos los comandos especificando el directorio de trabajo (cwd)
            subprocess.run(["git", "add", "."], cwd=ruta_raiz, check=True)
            subprocess.run(["git", "commit", "-m", "Update Catalog"], cwd=ruta_raiz, check=True)
            subprocess.run(["git", "push"], cwd=ruta_raiz, check=True)
            
            messagebox.showinfo("NINJA CLOUD", "✅ ¡Catálogo actualizado en la web con éxito!")
        except subprocess.CalledProcessError as e:
            print(f"Error Git: {e}")
            messagebox.showerror("Error Git", "No hay cambios nuevos o error de conexión.")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", str(e))

    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            self.inventario = self.motor.succionar_archivo(f, self.inventario)
        self.finalizar("Archivos soltados con éxito.")

    def crear_backup(self):
        if not os.path.exists("backups"): os.makedirs("backups")
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(self.ruta_json):
            shutil.copy(self.ruta_json, f"backups/inventario_{fecha}.json")

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=350)
        self.sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.entry_busqueda = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Buscar...", height=35)
        self.entry_busqueda.pack(fill="x", padx=15, pady=15)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.actualizar_lista())
        f_aspirar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        f_aspirar.pack(fill="x", padx=10)
        ctk.CTkButton(f_aspirar, text="📁 CARPETA", fg_color="#d35400", width=100, command=self.ui_aspirar_carpeta).pack(side="left", padx=2)
        ctk.CTkButton(f_aspirar, text="🖼 + IMÁGENES", fg_color="#e67e22", width=100, command=self.ui_aspirar_archivos).pack(side="left", padx=2)
        ctk.CTkButton(f_aspirar, text="🛡️ SUPER SCAN", fg_color="#27ae60", width=100, command=self.super_escaneo).pack(side="left", padx=2)
        self.tabview = ctk.CTkTabview(self.sidebar, command=self.actualizar_lista)
        self.tabview.pack(expand=True, fill="both", padx=5, pady=5)
        self.scrolls = {cat: ctk.CTkScrollableFrame(self.tabview.add(name)) for cat, name in self.tabs_info.items()}
        for s in self.scrolls.values(): s.pack(expand=True, fill="both")
        self.main = ctk.CTkScrollableFrame(self)
        self.main.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        f_imgs = ctk.CTkFrame(self.main, fg_color="transparent")
        f_imgs.pack(pady=10)
        self.img_v1 = ctk.CTkLabel(f_imgs, text="FRONTAL", width=420, height=420, fg_color="#1e1e1e", corner_radius=12)
        self.img_v1.pack(side="left", padx=15)
        self.img_v2 = ctk.CTkLabel(f_imgs, text="PERFIL", width=420, height=420, fg_color="#1e1e1e", corner_radius=12)
        self.img_v2.pack(side="left", padx=15)
        f_flow = ctk.CTkFrame(self.main, fg_color="transparent")
        f_flow.pack(pady=10)
        ctk.CTkButton(f_flow, text="🔗 UNIR", fg_color="#8e44ad", width=150, height=40, command=self.unir_piezas).pack(side="left", padx=5)
        ctk.CTkButton(f_flow, text="✂ DESUNIR", fg_color="#c0392b", width=150, height=40, command=self.desunir_piezas).pack(side="left", padx=5)
        ctk.CTkButton(f_flow, text="🔄 SWAP", fg_color="#2980b9", width=100, height=40, command=self.invertir_seleccion).pack(side="left", padx=5)
        self.txt_desc = ctk.CTkTextbox(self.main, height=100, width=650, font=("Arial", 16))
        self.txt_desc.pack(pady=10)
        self.combo_cat = ctk.CTkOptionMenu(self.main, values=list(self.tabs_info.keys()), width=350)
        self.combo_cat.pack(pady=5)
        
        f_final = ctk.CTkFrame(self.main, fg_color="transparent")
        f_final.pack(pady=20)
        # BOTONES FINALES ACOPLADOS
        ctk.CTkButton(f_final, text="🚀 ACTUALIZAR", fg_color="#27ae60", width=180, height=50, command=self.guardar_datos).pack(side="left", padx=10)
        ctk.CTkButton(f_final, text="☁️ SUBIR A WEB", fg_color="#3498db", width=180, height=50, command=self.subir_a_github).pack(side="left", padx=10)
        ctk.CTkButton(f_final, text="🗑 PAPELERA", fg_color="#e74c3c", width=150, height=50, command=self.eliminar_item).pack(side="left", padx=10)
        self.actualizar_lista()

    def super_escaneo(self):
        self.crear_backup()
        for i in range(len(self.inventario)):
            self.inventario[i] = self.motor.reparar_item(self.inventario[i])
        reg = set()
        for it in self.inventario:
            n = it['nombre']
            if isinstance(n, list): 
                for x in n: reg.add(f"{str(x).lower()}.jpeg")
            else: reg.add(f"{str(n).lower()}.jpeg")
        borrados = 0
        for f in os.listdir(self.ruta_img):
            archivo = f.lower()
            if archivo.endswith(('.jpeg', '.jpg', '.png')) and archivo not in self.motor.blacklist:
                if archivo not in reg:
                    try: os.remove(os.path.join(self.ruta_img, f)); borrados += 1
                    except: pass
        self.motor.guardar_json(self.inventario)
        self.actualizar_lista()
        messagebox.showinfo("SUPER SCAN", f"✅ Reparado y Backup creado.\n✅ {borrados} Fotos borradas.")

    def actualizar_lista(self):
        busq = self.entry_busqueda.get().lower()
        for s in self.scrolls.values():
            for w in s.winfo_children(): w.destroy()
        for i, p in enumerate(self.inventario):
            nom = p.get('nombre', 'S/N')
            txt = (", ".join(nom) if isinstance(nom, list) else str(nom)).upper()
            cat = p.get('cat', 'auditoria').lower()
            if busq in txt.lower() or busq in p.get('desc','').lower():
                bg = "#2980b9" if i in self.seleccionados_idx else "transparent"
                ctk.CTkButton(self.scrolls.get(cat, self.scrolls['auditoria']), text=txt, fg_color=bg, anchor="w", command=lambda idx=i: self.clic_item(idx)).pack(fill="x", pady=1)

    def ui_aspirar_carpeta(self):
        folder = filedialog.askdirectory()
        if folder:
            for f in os.listdir(folder): self.inventario = self.motor.succionar_archivo(os.path.join(folder, f), self.inventario)
            self.finalizar("Carpeta succionada.")

    def ui_aspirar_archivos(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
        if files:
            for f in files: self.inventario = self.motor.succionar_archivo(f, self.inventario)
            self.finalizar("Imágenes succionadas.")

    def clic_item(self, idx):
        if idx in self.seleccionados_idx: self.seleccionados_idx.remove(idx)
        else:
            if len(self.seleccionados_idx) >= 2: self.seleccionados_idx.pop(0)
            self.seleccionados_idx.append(idx)
        if self.seleccionados_idx:
            p = self.inventario[self.seleccionados_idx[0]]
            self.txt_desc.delete("1.0", "end")
            self.txt_desc.insert("1.0", p.get('desc', ''))
            self.combo_cat.set(p.get('cat', 'auditoria'))
        self.mostrar_imagenes(); self.actualizar_lista()

    def mostrar_imagenes(self):
        self.img_v1.configure(image=self.img_vacia, text="FRONTAL")
        self.img_v2.configure(image=self.img_vacia, text="PERFIL")
        if not self.seleccionados_idx: return
        p = self.inventario[self.seleccionados_idx[0]]
        if isinstance(p['nombre'], list): imgs = p['nombre']
        else: imgs = [self.inventario[i]['nombre'] for i in self.seleccionados_idx if not isinstance(self.inventario[i]['nombre'], list)]
        for i, n in enumerate(imgs[:2]):
            ruta = os.path.join(self.ruta_img, f"{n}.jpeg")
            if os.path.exists(ruta):
                img = ctk.CTkImage(Image.open(ruta), size=(420, 420))
                if i == 0: self.img_v1.configure(image=img, text="")
                else: self.img_v2.configure(image=img, text="")

    def unir_piezas(self):
        if len(self.seleccionados_idx) == 2:
            idx1, idx2 = self.seleccionados_idx
            p1, p2 = self.inventario[idx1], self.inventario[idx2]
            def limpio(p): return p['nombre'] if not isinstance(p['nombre'], list) else p['nombre'][0]
            self.inventario.append({
                "nombre": [limpio(p1), limpio(p2)], "cat": self.combo_cat.get(),
                "desc": self.txt_desc.get("1.0", "end-1c"), "old_desc": [p1.get('desc',''), p2.get('desc','')]
            })
            for i in sorted([idx1, idx2], reverse=True): self.inventario.pop(i)
            self.seleccionados_idx = [len(self.inventario)-1]
            self.finalizar("Unido.")

    def desunir_piezas(self):
        if self.seleccionados_idx:
            idx = self.seleccionados_idx[0]
            it = self.inventario[idx]
            if isinstance(it['nombre'], list):
                noms, descs = it['nombre'], it.get('old_desc', ["Separado", "Separado"])
                self.inventario.pop(idx)
                for n, d in zip(noms, descs): self.inventario.append({"nombre": n, "cat": "auditoria", "desc": d})
                self.seleccionados_idx = []; self.finalizar("Desunido.")

    def invertir_seleccion(self):
        if self.seleccionados_idx:
            it = self.inventario[self.seleccionados_idx[0]]
            if isinstance(it['nombre'], list):
                it['nombre'].reverse()
                if 'old_desc' in it: it['old_desc'].reverse()
                self.mostrar_imagenes(); self.finalizar("Swap.")

    def guardar_datos(self):
        if self.seleccionados_idx:
            idx = self.seleccionados_idx[0]
            self.inventario[idx]['cat'] = self.combo_cat.get()
            self.inventario[idx]['desc'] = self.txt_desc.get("1.0", "end-1c")
            self.finalizar("OK.")

    def eliminar_item(self):
        for idx in sorted(self.seleccionados_idx, reverse=True):
            if self.inventario[idx]['cat'] == 'papelera': self.inventario.pop(idx)
            else: self.inventario[idx]['cat'] = 'papelera'
        self.seleccionados_idx = []; self.finalizar("Papelera.")

    def finalizar(self, msg):
        self.crear_backup()
        self.motor.guardar_json(self.inventario)
        self.actualizar_lista(); self.mostrar_imagenes()

# --- CIERRE LIMPIO ---
if __name__ == "__main__":
    app = OptiAdmin()
    try:
        app.mainloop()
    except (KeyboardInterrupt, SystemExit): pass
    except Exception as e: print(f"\n⚠️ Error: {e}")
    finally: 
        print("\n✅ NINJA MASTER: Panel cerrado con éxito.")
        try: app.destroy()
        except: pass