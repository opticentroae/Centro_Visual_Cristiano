import os
import re
import subprocess
import shutil
import stat
import tkinter as tk
from tkinter import messagebox, simpledialog

# --- CONFIGURACIÓN ---
REPO_URL = "https://github.com/opticentroae/Centro_Visual_Cristiano.git"
IMG_DIR = 'img'
EXTENSIONS = ('.html', '.css', '.js')

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class AppAuditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Ocultar ventana principal

    def solicitar_mensaje(self):
        msg = simpledialog.askstring("Git Push", "Escribe el mensaje del commit:", 
                                     initialvalue="🚀 Producción: Opticentro Pro (Optimized)")
        return msg if msg else "🚀 Update: Centro Visual Cristiano"

    def auditoria_reparacion(self):
        print("🛠️  Iniciando Auditoría Visual...")
        log = []
        real_files = os.listdir(IMG_DIR) if os.path.exists(IMG_DIR) else []
        real_files_lower = {f.lower(): f for f in real_files}
        
        for root, dirs, files in os.walk('.'):
            if '.git' in dirs: dirs.remove('.git')
            for file in files:
                if file.endswith(EXTENSIONS):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 1. Corregir Slashes iniciales (para GitHub Pages)
                        new_content = re.sub(r'((?:src|href)=["\'])/(?!http|https|//)', r'\1', content)

                        # 2. Corregir Case Sensitivity y detectar archivos faltantes
                        def fix_img_logic(match):
                            img_name = match.group(1)
                            if img_name.lower() in real_files_lower:
                                correct_name = real_files_lower[img_name.lower()]
                                if img_name != correct_name:
                                    log.append(f"🔧 Renombrado: {img_name} -> {correct_name} en {file}")
                                return f'img/{correct_name}'
                            else:
                                log.append(f"❌ ERROR: La imagen '{img_name}' referenciada en {file} NO EXISTE en /img")
                                return match.group(0)

                        new_content = re.sub(r'img/([a-zA-Z0-9\._\-\s]+\.(?:jpg|jpeg|png|gif|svg|webp))', 
                                             fix_img_logic, new_content, flags=re.IGNORECASE)

                        if content != new_content:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                    except Exception as e:
                        print(f"⚠️ Error procesando {path}: {e}")
        
        return "\n".join(log) if log else "No se encontraron errores de rutas."

    def ejecutar(self):
        # 1. Preguntar qué hacer
        opcion = messagebox.askyesnocancel("Auditor ArticDash", 
                                          "¿Deseas ejecutar REPARACIÓN y DESPLIEGUE?\n\n"
                                          "Yes: Reparar y Subir a GitHub\n"
                                          "No: Solo Reparar localmente\n"
                                          "Cancel: Salir")
        
        if opcion is None: return # Salir

        # 2. Reparación
        resultado = self.auditoria_reparacion()
        messagebox.showinfo("Resultado Auditoría", resultado)

        # 3. Despliegue (Si eligió Yes)
        if opcion is True:
            commit_msg = self.solicitar_mensaje()
            try:
                if os.path.exists('.git'):
                    print("🧹 Limpiando historial previo...")
                    shutil.rmtree('.git', onerror=remove_readonly)
                
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                subprocess.run(["git", "branch", "-M", "main"], check=True)
                subprocess.run(["git", "remote", "add", "origin", REPO_URL], check=True)
                
                print("📤 Subiendo a GitHub...")
                subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
                
                messagebox.showinfo("Éxito", "✨ ¡Proyecto en línea!\nhttps://opticentroae.github.io/Centro_Visual_Cristiano/")
            except Exception as e:
                messagebox.showerror("Error", f"Hubo un problema con Git:\n{e}")

if __name__ == "__main__":
    app = AppAuditor()
    app.ejecutar()