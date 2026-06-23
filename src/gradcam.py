"""Explicabilité — Grad-CAM sur la dernière couche convolutive de ResNet-18."""
import argparse
import os

import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from PIL import Image

from dataset import CLASSES
from model import build_model
from train import get_transforms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--model_path", default="models/best_model.pt")
    parser.add_argument("--output", default="outputs/gradcam.png")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = build_model(len(CLASSES)).to(device)
    model.load_state_dict(torch.load(args.model_path, map_location=device))
    model.eval()

    _, eval_t = get_transforms()
    pil = Image.open(args.image).convert("RGB")
    x = eval_t(pil).unsqueeze(0).to(device)

    activations, gradients = {}, {}
    target_layer = model.layer4[-1]
    h1 = target_layer.register_forward_hook(
        lambda m, i, o: activations.__setitem__("v", o.detach())
    )
    h2 = target_layer.register_full_backward_hook(
        lambda m, gi, go: gradients.__setitem__("v", go[0].detach())
    )

    out = model(x)
    cls = out.argmax(1).item()
    model.zero_grad()
    out[0, cls].backward()

    weights = gradients["v"].mean(dim=(2, 3), keepdim=True)
    cam = F.relu((weights * activations["v"]).sum(dim=1, keepdim=True))
    cam = F.interpolate(cam, size=(224, 224), mode="bilinear", align_corners=False)
    cam = cam.squeeze().cpu().numpy()
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    h1.remove()
    h2.remove()

    plt.figure(figsize=(5, 5))
    plt.imshow(pil.resize((224, 224)), cmap="gray")
    plt.imshow(cam, cmap="jet", alpha=0.5)
    plt.title(f"Grad-CAM — prédiction : {CLASSES[cls]}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"Prédiction : {CLASSES[cls]}  ->  {args.output}")


if __name__ == "__main__":
    main()
