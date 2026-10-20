"""Roda as celulas de codigo do notebook localmente com Ultralytics/SAM SIMULADO.

Valida que o codigo executa de ponta a ponta (carregamento, prompts, figuras,
metricas, teste de contraste, exportacao). Nao valida a qualidade da segmentacao.
Uso: python fonte/teste_ultra.py <pasta_libs> <pasta_trabalho> <imagem.jpg>
"""
import json
import os
import pathlib
import shutil
import sys
import traceback
import types

LIBS, TRABALHO, IMAGEM = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.append(LIBS)
NB = pathlib.Path(__file__).resolve().parent.parent / "Segmentacao_Pluma_SAM.ipynb"

os.makedirs(TRABALHO, exist_ok=True)
shutil.copy(IMAGEM, os.path.join(TRABALHO, "pluma.jpg"))
os.chdir(TRABALHO)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cv2

plt.show = lambda *a, **k: plt.close("all")

# ---------------------------------------------------------------- torch falso
torch = types.ModuleType("torch")
torch.cuda = types.SimpleNamespace(is_available=lambda: False, get_device_name=lambda i: "fake")
torch.manual_seed = lambda s: None
sys.modules["torch"] = torch


# ------------------------------------------------------- ultralytics falso
class _Tensor:
    """Imita o minimo da API de tensor usada: .cpu().numpy() e len()."""

    def __init__(self, a):
        self.a = a

    def cpu(self):
        return self

    def numpy(self):
        return self.a

    def __len__(self):
        return len(self.a)


class _Masks:
    def __init__(self, a):
        self.data = _Tensor(a)


class _Result:
    def __init__(self, a):
        self.masks = _Masks(a)


class FakeSAM2Predictor:
    """Mapa de 'cara de fumaca' (claro + pouco saturado) deslocado pelos prompts,
    para que prompts diferentes produzam mascaras diferentes."""

    def __init__(self, overrides=None):
        self.overrides = overrides or {}

    def set_image(self, caminho):
        img = cv2.imread(caminho)
        if img is None:
            raise FileNotFoundError(caminho)
        self.img = img
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        s = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1].astype(np.float32) / 255
        self.mapa = cv2.GaussianBlur(np.clip(1.15 * g - 1.4 * s + 0.12, 0, 1), (0, 0), 3)

    def __call__(self, bboxes=None, points=None, labels=None, **kw):
        h, w = self.img.shape[:2]
        base = self.mapa.copy()
        # Reproduz o contrato de forma do SAM2Predictor._prepare_prompts (v8.4.x):
        # pontos (N, 2) viram (N, 1, 2), e a caixa (1, 2, 2) e concatenada em dim=1,
        # o que exige que o numero de grupos de pontos seja igual ao numero de caixas.
        if points is not None:
            pts = np.asarray(points, float)
            lbl = np.asarray(labels, int)
            assert pts.shape[-2] == lbl.shape[-1], "pontos e rotulos com tamanhos diferentes"
            if pts.ndim == 2:
                pts, lbl = pts[:, None, :], lbl[:, None]
            if bboxes is not None:
                n_caixas = np.asarray(bboxes, float).reshape(-1, 2, 2).shape[0]
                if pts.shape[0] != n_caixas:
                    raise RuntimeError(
                        "Sizes of tensors must match except in dimension 1. Expected size "
                        f"{n_caixas} but got size {pts.shape[0]} for tensor number 1 in the list.")
            points = pts.reshape(-1, 2)
            labels = lbl.reshape(-1)
        if bboxes is not None:
            x0, y0, x1, y1 = [int(round(v)) for v in np.asarray(bboxes, float).reshape(-1)[:4]]
            dentro = np.zeros((h, w), np.float32)
            dentro[max(y0, 0):max(y1, 0), max(x0, 0):max(x1, 0)] = 1
            base *= 0.25 + 0.75 * dentro
        if points is not None and len(points):
            yy, xx = np.mgrid[0:h, 0:w]
            sig = 0.07 * max(h, w)
            for (x, y), lab in zip(np.asarray(points, float), np.asarray(labels, int)):
                bump = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sig ** 2))
                base = base + (0.45 * bump if lab == 1 else -0.9 * bump)
        return [_Result((np.clip(base, 0, 1.5) > 0.5)[None].astype(np.uint8))]


ul = types.ModuleType("ultralytics")
ul_sam = types.ModuleType("ultralytics.models.sam")
ul_sam.SAM2Predictor = FakeSAM2Predictor
ul_sam.Predictor = FakeSAM2Predictor
ul_models = types.ModuleType("ultralytics.models")
ul_models.sam = ul_sam
ul.models = ul_models
sys.modules.update({"ultralytics": ul, "ultralytics.models": ul_models,
                    "ultralytics.models.sam": ul_sam})

# ---------------------------------------------------------------- google.colab falso
gc = types.ModuleType("google.colab")
gc.files = types.SimpleNamespace(upload=lambda: {"pluma.jpg": b""}, download=lambda p: None)
gc.drive = types.SimpleNamespace(mount=lambda *a, **k: None)
google = types.ModuleType("google")
google.colab = gc
sys.modules.setdefault("google", google)
sys.modules["google.colab"] = gc

# ---------------------------------------------------------------- executa
nb = json.loads(NB.read_text(encoding="utf-8"))
ns = {"__name__": "__main__", "display": lambda *a, **k: [print(x) for x in a]}

for i, c in enumerate(nb["cells"], 1):
    if c["cell_type"] != "code":
        continue
    fonte = "".join(c["source"])
    limpo = "\n".join("pass" if l.lstrip().startswith(("!", "%")) else l
                      for l in fonte.splitlines())
    print(f"\n{'='*70}\n== CELULA {i}\n{'='*70}")
    try:
        exec(compile(limpo, f"<celula {i}>", "exec"), ns)
    except Exception:
        traceback.print_exc()
        print(f"\n### FALHOU NA CELULA {i}")
        sys.exit(1)

print("\n\n### TODAS AS CELULAS DE CODIGO RODARAM ATE O FIM")
