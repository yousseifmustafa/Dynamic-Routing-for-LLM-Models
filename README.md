# 🧠 Dynamic LLM Query Router

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Framework](https://img.shields.io/badge/Framework-LangChain-purple)
![Provider](https://img.shields.io/badge/Provider-Hugging%20Face-yellow?logo=huggingface)
![Models](https://img.shields.io/badge/Models-Llama3%20&%20Mixtral-green?logo=meta)
![Dependencies](https://img.shields.io/badge/Dependencies-pip-orange?logo=pypi)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

This project is a smart Python script that classifies user queries into 'Simple', 'Medium', or 'Advanced' and routes them to the most appropriate Large Language Model (LLM) for the job. It uses LangChain and Hugging Face to create an efficient, scalable, and intelligent query-handling system that optimizes for both cost and performance.

---

## ✨ Features

-   **Dynamic Routing**: Intelligently classifies queries to determine their complexity before sending them to an execution model.
-   **Multi-Model Architecture**: Uses different LLMs for different tasks, optimizing for speed, cost, and analytical power.
-   **Robust Fallback Mechanism**: If a chosen model fails, the system automatically retries the query with the next, more powerful model to ensure the user always gets a response.
-   **Response Caching**: Caches answers to previously seen queries to provide instant results and minimize redundant API calls.
-   **Comprehensive Logging**: Saves all successful answers and any errors encountered to separate text files (`Answers.txt` and `logs.txt`) for easy debugging and review.

---

## ⚙️ How It Works

The script follows a simple yet powerful logic:


1.  **Classification**: When a query is received, it's first sent to a small, fast "Router" LLM (`meta-llama/Llama-3.2-3B-Instruct`). The router's sole purpose is to analyze the query and return one word: `Simple`, `Medium`, or `Advanced`.
2.  **Routing**: Based on the classification, the query is dispatched to the corresponding LLM chain.
3.  **Execution & Fallback**: The designated model processes the query. If it fails, the system automatically tries the next model up in the hierarchy (e.g., a failed 'Simple' query is sent to the 'Medium' model).
4.  **Caching & Logging**: The final answer is cached for future use and the response is logged to `Answers.txt`. Any errors are logged in `logs.txt`.

---

## 🛠️ Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/yousseifmustafa/Dynamic-Routing-for-LLM-Models.git](https://github.com/yousseifmustafa/Dynamic-Routing-for-LLM-Models.git)
cd Dynamic-Routing-for-LLM-Models
```

### 2. Create and Activate a Virtual Environment
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all the required Python packages .
```bash
pip install langchain-huggingface python-dotenv

```

### 4. Set Up Environment Variables
Create a file named `.env` in the root directory of the project and add your Hugging Face API token to it. **This file is ignored by Git and should never be shared.**
```
HF_API_KEY="your_hugging_face_api_key_here"
```

---

## 🚀 Usage

To run the script, execute the main Python file from your terminal. Make sure your virtual environment is activated.

```bash
python your_main_script_name.py
```

The script will process the predefined list of test queries, print the classification and final answers to the console, and generate the `Answers.txt` and `logs.txt` files.

---

## 🤖 Models Used

This project is configured to use the following models from Hugging Face:

| Role           | Model Name                               | Purpose                                     |
| :------------- | :--------------------------------------- | :------------------------------------------ |
| **Router** | `meta-llama/Llama-3.2-3B-Instruct`       | Fast and efficient query classification.    |
| **Simple Tier**| `meta-llama/Llama-3.2-3B-Instruct`       | Handling basic, straightforward questions.  |
| **Medium Tier**| `meta-llama/Meta-Llama-3-8B-Instruct`    | General-purpose tasks and explanations.     |
| **Advanced Tier**| `mistralai/Mixtral-8x7B-Instruct-v0.1`   | Complex analysis, coding, and reasoning.    |



---

## 📜 License

This project is licensed under the MIT License.

Created with ❤️ by **[Youssef Mustafa](https://github.com/yousseifmustafa)** © 2024
