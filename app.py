"""SolarScan - demo Gradio (detection de defauts sur panneaux solaires).

Charge le modele entraine (solarscan_resnet18.pt + classes.json) et lance une
interface web : on depose une image thermique -> prediction + carte Grad-CAM.
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
from PIL import Image

import torch
import torch.nn as nn
from torchvision import transforms, models
import gradio as gr

ROOT = Path(__file__).parent
DEVICE = 'cpu'

with open(ROOT / 'classes.json', encoding='utf-8') as f:
    CLASSES = json.load(f)

model = models.resnet18()
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
model.load_state_dict(torch.load(ROOT / 'solarscan_resnet18.pt', map_location=DEVICE))
model.eval()

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
eval_tf = transforms.Compose([
    transforms.Grayscale(3), transforms.Resize((224, 224)),
    transforms.ToTensor(), transforms.Normalize(MEAN, STD)])


def gradcam(x, target_layer):
    acts, grads = {}, {}
    h1 = target_layer.register_forward_hook(lambda m, i, o: acts.__setitem__('v', o.detach()))
    h2 = target_layer.register_full_backward_hook(lambda m, gi, go: grads.__setitem__('v', go[0].detach()))
    out = model(x)
    cls = out.argmax(1).item()
    model.zero_grad()
    out[0, cls].backward()
    h1.remove(); h2.remove()
    a, g = acts['v'][0], grads['v'][0]
    cam = torch.relu((g.mean(dim=(1, 2))[:, None, None] * a).sum(0))
    return (cam / (cam.max() + 1e-8)).detach().cpu().numpy()


def make_overlay(img, cam):
    base = np.array(img.convert('L').resize((224, 224)))
    cam_up = np.array(Image.fromarray((cam * 255).astype('uint8')).resize((224, 224))) / 255.0
    heat = (matplotlib.colormaps['jet'](cam_up)[:, :, :3] * 255).astype('uint8')
    blend = (0.5 * np.stack([base] * 3, axis=-1) + 0.5 * heat).astype('uint8')
    return Image.fromarray(blend)


def predict(img):
    if img is None:
        return {}, None
    x = eval_tf(img).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(model(x), 1)[0].numpy()
    confidences = {CLASSES[i]: float(probs[i]) for i in range(len(CLASSES))}
    cam = gradcam(x, model.layer4[-1])
    return confidences, make_overlay(img, cam)


demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type='pil', label='Image thermique du module PV'),
    outputs=[gr.Label(num_top_classes=5, label='Prediction'),
             gr.Image(type='pil', label='Grad-CAM (zones regardees)')],
    title='SolarScan - Detection de defauts sur panneaux solaires',
    description='Depose une image thermique infrarouge d un module PV. Le modele predit la classe d anomalie et montre ou il a regarde.')

if __name__ == '__main__':
    demo.launch(server_name='127.0.0.1', server_port=7860)
