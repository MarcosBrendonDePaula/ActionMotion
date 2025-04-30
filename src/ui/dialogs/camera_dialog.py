import tkinter as tk
from tkinter import ttk, messagebox
import cv2

# --- cache global -----------------------------------------------------------
# cam_cache = {índice: "Available" | "Unavailable (...)"}  --------------------
cam_cache: dict[int, str] = {}


def probe_camera(idx: int) -> str:
    """Testa se a câmera em `idx` abre e devolve frames."""
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)          # CAP_DSHOW = +rápido no Windows
    if not cap.isOpened():
        cap.release()
        return "Unavailable (cannot open)"
    ok, _ = cap.read()
    cap.release()
    return "Available" if ok else "Unavailable (no frames)"


def get_cameras(max_ports: int = 20, force_refresh: bool = False) -> dict[int, str]:
    """
    Devolve um dicionário com as portas disponíveis.  
    Usa o cache salvo em `cam_cache`; passe `force_refresh=True`
    para refazer a detecção.
    """
    for i in range(max_ports):
        if force_refresh or i not in cam_cache:
            cam_cache[i] = probe_camera(i)

    # mantém no retorno apenas as que abriram de fato
    return {i: st for i, st in cam_cache.items() if st == "Available"}


# --------------------------------------------------------------------------- #
def change_camera(root: tk.Tk, current_camera_index: int,
                  force_refresh: bool = False) -> int:
    """
    Mostra o diálogo de seleção de câmera e devolve o índice escolhido.
    """
    cameras = get_cameras(force_refresh=force_refresh)

    if not cameras:
        messagebox.showerror("Camera Error",
                             "Nenhuma câmera encontrada. Usando a padrão (0).")
        return 0

    # ------------------ diálogo ---------------------------------------------
    dlg = tk.Toplevel(root)
    dlg.title("Selecionar Câmera")
    dlg.geometry("320x240")
    dlg.transient(root)
    dlg.grab_set()

    ttk.Label(dlg, text="Câmeras disponíveis",
              font=("Arial", 12, "bold")).pack(pady=(10, 5))

    # ------- frame com rolagem ----------
    container = ttk.Frame(dlg)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, highlightthickness=0)
    vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scroll_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # ajustar a região de rolagem sempre que o conteúdo mudar
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # ------------- rádios dentro do frame rolável ---------------------------
    camera_var = tk.IntVar(value=current_camera_index)
    for idx in sorted(cameras):
        ttk.Radiobutton(
            scroll_frame,
            text=f"Câmera {idx}",
            variable=camera_var,
            value=idx
        ).pack(anchor=tk.W, padx=18, pady=2)

    # ---------------- botão confirmar --------------------------------------
    ttk.Button(dlg, text="Selecionar",
               command=lambda: dlg.destroy()).pack(pady=12)

    root.wait_window(dlg)
    return camera_var.get()