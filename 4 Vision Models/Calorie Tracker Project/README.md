
# 🍽️ Calorie Tracker with OpenAI Vision

This project demonstrates how to use **OpenAI Vision Models** through their API to analyze food images and extract nutritional information in a structured JSON format.
It combines a **backend** for AI inference and a simple **frontend app** built with Gradio for user interaction.

---

## 📂 Project Structure

```
Calorie-Tracker/
│
├── backend.py       # Core logic: OpenAI Vision integration, JSON parsing, nutrition analysis
├── app.py           # Gradio frontend: upload an image and display results
├── images/          # Sample images for practice and testing
├── Calorie Tracker - Project.ipynb   # Original notebook version
└── README.md        # Project documentation
```

---

## 🚀 Features

* Upload an image of food and receive structured nutritional insights:

  * **Food name**
  * **Serving description**
  * **Calories**
  * **Fat (grams)**
  * **Protein (grams)**
  * **Confidence level**
* Clean **JSON output** for programmatic use.
* User-friendly **visual results** via Gradio (color-coded nutritional values).
* Robust JSON parsing to handle raw model output.

---

## 🎯 Key Learning Outcomes

From this project, you will learn to:

* Communicate with **powerful AI vision models** using their APIs.
* Master the art of **Prompt Engineering**, including context, instructions, input, and output indicators.
* Understand the difference between **zero-shot, few-shot, and chain-of-thought prompting**.
* Discover how to **convert an image into a base64-encoded string** for OpenAI API calls.

---

## 🛠️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Expeavomo15/04-Vision-Models/calorie-tracker.git
cd calorie-tracker
pip install -r requirements.txt
```

Make sure you have a `.env` file in the root directory with your OpenAI key:

```
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Usage

### Run the Gradio app

```bash
python app.py
```

This will launch a local interface where you can:

* Upload an image (e.g., from the `images/` folder).
* Analyze it using OpenAI Vision.
* View both the **structured JSON output** and a **colorful summary**.

---

## 📊 Example Output

```json
{
  "food_name": "Pizza Slice",
  "serving_description": "1 slice",
  "calories": 285,
  "fat_grams": 10.0,
  "protein_grams": 12.0,
  "confidence_level": "High"
}
```

---

## 📸 Sample Images

The `images/` folder includes sample food images you can use to test the model right away.

---

## 👤 Author

**Expe Avomo**
*AI Engineer & Consultant*


