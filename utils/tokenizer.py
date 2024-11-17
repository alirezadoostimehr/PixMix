import requests
import torch
import clip
from PIL import Image

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "..", "assets")
model_path = os.path.join(assets_dir, "Vit-L-14.pt")
device = "cpu"
model, preprocess = clip.load(model_path, device=device)


def _normalize_and_flatten(features):
    features /= features.norm(dim=-1, keepdim=True)
    result = features.cpu().numpy().flatten().tolist()
    return result


def get_image_vectors(image_url):
    response = requests.get(image_url, stream=True)
    response.raise_for_status()

    image_file = Image.open(response.raw)
    image = preprocess(image_file).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)

    return _normalize_and_flatten(image_features)


def get_text_vector(text):
    with torch.no_grad():
        text_features = model.encode_text(clip.tokenize([text]).to(device))

    return _normalize_and_flatten(text_features)
