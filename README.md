🎓 Study with Subha
An AI-powered RAG-style study assistant built with Python and Streamlit. Upload your notes (PDF, TXT or DOCX), ask a question, and get a simple, exam-friendly answer based only on your own study material.
Features
📎 Upload study material in PDF, TXT or DOCX format
🧩 Automatic text extraction, cleaning and overlapping chunking (1200 characters, 200 overlap)
🔎 Keyword-based retrieval of the most relevant sections for each question
🤖 Answers generated with the OpenAI API, grounded in the retrieved context
🌐 Explanations in simple English or Bengali
📝 Exam-style answers (short for 3-mark questions, structured for 5-mark questions)
💬 Chat history, New Chat button and a custom dark UI
How it works
Upload a PDF, TXT or DOCX file from the sidebar.
The text is extracted, cleaned and split into overlapping chunks.
When you ask a question, the app finds the chunks that best match your keywords.
Those chunks are sent to the OpenAI model with a study-focused prompt.
The answer is shown in the chat. If nothing relevant is found, the app says so instead of guessing.
Tech stack
Python
Streamlit
OpenAI API
PyPDF2
python-docx
python-dotenv
Setup
Clone the repository
git clone https://github.com/subhadeepdutta659-cpu/study-with-subha.git
cd study-with-subha
Install dependencies
pip install -r requirements.txt
Add your OpenAI API key
Create a file named .env in the project folder:
OPENAI_API_KEY=your_api_key_here
Never upload your .env file to GitHub.
Run the app
streamlit run app.py
Future improvements
Semantic search using embeddings instead of keyword matching
Support for more file types
Saving chat history
Author
Subhadeep Dutta
B.Tech CSE, Adamas University
GitHub · LinkedIn
