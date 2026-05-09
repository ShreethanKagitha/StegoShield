# 🔐 Secure Data Hiding
### Advanced Image Steganography Application

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-WebGL-black?style=for-the-badge&logo=three.js&logoColor=white)

**Secure Data Hiding** is a modern, web-based steganography tool that allows you to securely hide secret text messages within innocent-looking images. Built with Django and featuring a stunning glassmorphism UI powered by Three.js.

---

## 🌟 Key Features

- **🛡️ LSB Steganography**: Uses the Least Significant Bit algorithm to embed data imperceptibly.
- **🖼️ Image Support**: Full support for **PNG** and **BMP** lossless formats.
- **📊 Smart Capacity Analysis**: Real-time calculation of how much data you can hide in a specific image.
- **✨ Interactive 3D UI**: Beautiful, engaging interface with animated particle backgrounds (Three.js).
- **📱 Responsive Design**: Fully optimized for desktop and mobile devices.
- **🔒 Client-Side Privacy**: Images are processed securely; no external storage of your secrets.

## 🚀 Live Demo

> **Note**: This is a local development project. Follow the installation steps below to run it on your machine.

## 🛠️ Technology Stack

- **Backend**: Python, Django 5.x
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework**: Bootstrap 5
- **Visualizations**: Chart.js (Capacity charts), Three.js (3D Backgrounds)

---

## 💾 Installation & Setup

Follow these steps to get the project running locally:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/secure-data-hiding.git
cd "Secure Data Hiding"
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Start the Server
```bash
python manage.py runserver
```

Visit **`http://127.0.0.1:8000/`** in your browser to start using the app.

---

## 📖 Usage Guide

### 🔒 Encoding (Hiding a Message)
1. Navigate to the **Encode** page.
2. Drag & drop or upload a **PNG** or **BMP** image (Cover Image).
3. The app will calculate the **maximum character capacity** for that image.
4. Type your secret message in the text area.
    - *The capacity chart will update in real-time.*
5. Click **"Encode & Generate Stego-Image"**.
6. Download the resulting image. It looks identical to the original but contains your secret data!

### 🔓 Decoding (Extracting a Message)
1. Navigate to the **Decode** page.
2. Upload the **Stego-Image** (the one you downloaded earlier).
3. Click **"Extract Hidden Message"**.
4. Your secret message will be revealed instantly.

---

## 🧠 How It Works (LSB Algorithm)

**Least Significant Bit (LSB)** steganography works by replacing the last bit of pixel color data with message bits.

- Each pixel has 3 color channels: **Red**, **Green**, **Blue**.
- Each channel is 1 byte (8 bits).
- We modify only the **8th bit** (the least significant one).
- **Impact**: The color value changes by at most 1 (e.g., from 255 to 254), which is invisible to the human eye.

**Capacity Formula**:
```
Total Capacity (bytes) = (Image Width × Image Height × 3) / 8
```

---

## 📂 Project Structure

```
Secure Data Hiding/
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
├── secure_data_hiding/     # Project configuration
│   ├── settings.py
│   └── urls.py
└── stego_app/              # Main application
    ├── utils.py            # LSB Algorithm implementation
    ├── views.py            # View logic (Encode/Decode)
    └── templates/
        └── stego_app/
            ├── base.html   # Main layout with Three.js
            ├── home.html   # Landing page
            ├── encode.html # Encoding interface
            └── decode.html # Decoding interface
```

## ⚠️ Important Notes

- **Do NOT use JPEG/JPG images**: JPEG uses lossy compression, which will destroy the hidden bits and corrupt your message. Always use **PNG** or **BMP**.
- **Do not resize**: Resizing a stego-image will scramble the hidden data.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
