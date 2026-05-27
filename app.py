from flask import Flask, request, jsonify
from PIL import Image
import torch
import open_clip
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LARAVEL_API_URL = os.environ.get("LARAVEL_API_URL")

# =========================
# Load OpenCLIP Model
# =========================

model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32',
    pretrained='laion2b_s34b_b79k'
)

model.eval()

tokenizer = open_clip.get_tokenizer('ViT-B-32')

# =========================
# Global Variables
# =========================

image_features = []
products_data = []
index_matrix = np.array([])

# =========================
# Fetch Products From Laravel
# =========================

def fetch_products():
    response = requests.get(
        f"{LARAVEL_API_URL}/api/v1/public/product-images/all"
    )

    response.raise_for_status()

    return response.json()

# =========================
# Load Image From URL
# =========================

def load_image_from_url(url):

    response = requests.get(url)

    response.raise_for_status()

    image = Image.open(
        BytesIO(response.content)
    ).convert("RGB")

    return preprocess(image).unsqueeze(0)

# =========================
# Build AI Index
# =========================

def build_index():

    global image_features
    global products_data
    global index_matrix

    image_features = []
    products_data = []

    products = fetch_products()

    print(f"Found {len(products)} products")

    for product in products:

        try:

            image_tensor = load_image_from_url(
                product["image"]
            )

            with torch.no_grad():

                feature = model.encode_image(
                    image_tensor,
                    normalize=True
                )

            image_features.append(
                feature.cpu().numpy()
            )

            products_data.append({
                "id": product["id"],
                "image": product["image"]
            })

            print(f"Indexed: {product['id']}")

        except Exception as e:

            print(f"Skip {product['image']}")

            print(str(e))

    if image_features:

        index_matrix = np.vstack(image_features)

    else:

        index_matrix = np.array([])

    print("Index completed")

# =========================
# Build Index On Startup
# =========================

build_index()

# =========================
# Image Search
# =========================

@app.route('/search', methods=['POST'])
def search():

    if index_matrix.size == 0:

        return jsonify({
            "error": "No indexed images"
        }), 500

    if 'image' not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400

    try:

        image = Image.open(
            request.files['image']
        ).convert("RGB")

        image_tensor = preprocess(
            image
        ).unsqueeze(0)

        with torch.no_grad():

            query_feature = model.encode_image(
                image_tensor,
                normalize=True
            )

        query_feature = query_feature.cpu().numpy()

        similarities = cosine_similarity(
            query_feature,
            index_matrix
        )[0]

        top_indices = similarities.argsort()[-10:][::-1]

        results = []

        for i in top_indices:

            results.append({
                "id": products_data[i]["id"],
                "image": products_data[i]["image"],
                "similarity": round(
                    float(similarities[i]),
                    4
                )
            })

        return jsonify(results)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# Text Search
# =========================

@app.route('/search/text', methods=['POST'])
def search_text():

    if index_matrix.size == 0:

        return jsonify({
            "error": "No indexed images"
        }), 500

    data = request.get_json()

    if not data or not data.get("query"):

        return jsonify({
            "error": "No query provided"
        }), 400

    try:

        text = tokenizer([
            data["query"]
        ])

        with torch.no_grad():

            text_feature = model.encode_text(
                text,
                normalize=True
            )

        text_feature = text_feature.cpu().numpy()

        similarities = cosine_similarity(
            text_feature,
            index_matrix
        )[0]

        top_indices = similarities.argsort()[-10:][::-1]

        results = []

        for i in top_indices:

            results.append({
                "id": products_data[i]["id"],
                "image": products_data[i]["image"],
                "similarity": round(
                    float(similarities[i]),
                    4
                )
            })

        return jsonify(results)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# Refresh Index
# =========================

@app.route('/refresh', methods=['POST'])
def refresh():

    build_index()

    return jsonify({
        "message": "Index refreshed",
        "total": len(products_data)
    })

# =========================
# Run Server
# =========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )