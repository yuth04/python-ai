# 🤖 AI Visual Search

An AI-powered visual search service built with **Python, Flask, and OpenCLIP**.

This service allows users to upload a product image and find visually similar products from the VENDO product dataset.

Instead of searching only by product names or keywords, the system uses **AI image embeddings** to understand the visual features of images and return similar products.

---

## 🚀 Features

- 🖼️ Upload an image for visual search
- 🤖 AI-powered image feature extraction
- 🔍 Find visually similar products
- 📊 Calculate image similarity
- 🛍️ E-commerce product search
- ⚡ Fast similarity matching
- 📦 Search through product images
- 🔢 Return ranked search results
- 🌐 Flask REST API
- 🔗 VENDO integration
- 🐳 Docker support
- ☁️ Hugging Face Spaces deployment

---

## 🧠 How It Works

The system uses **OpenCLIP** to convert images into numerical representations called **image embeddings**.

The uploaded image embedding is compared with product image embeddings using **cosine similarity**.

```text
User Uploads Image
        │
        ▼
   Flask API
        │
        ▼
Image Preprocessing
        │
        ▼
    OpenCLIP
        │
        ▼
 Image Embedding
        │
        ▼
Compare Product Embeddings
        │
        ▼
 Cosine Similarity
        │
        ▼
   Rank Results
        │
        ▼
Similar Products
