# Insightmate

Insightmate is an AI-powered assistant for career, resume, and professional development guidance. It features a FastAPI backend and an Angular frontend, supporting file uploads, portfolio links, and personalized chat using OpenAI.

---

## Features

- **AI Chat**: General and personalized chat powered by OpenAI.
- **File Upload**: Upload resumes, certificates, and more.
- **Portfolio Links**: Add LinkedIn, GitHub, or personal website links.
- **User Data Summary**: View uploaded files and links.
- **Modern UI**: Responsive Angular frontend.

---

## Prerequisites

- **Python 3.8+**
- **Node.js 16+ & npm**
- **OpenAI API Key** (for full AI features)

---

## Backend Setup (FastAPI)

1. **Install dependencies:**
    ```sh
    cd insightmate/backend
    pip install -r requirements.txt
    ```

2. **Configure environment variables:**
    - Create a `.env` file or set these variables in your environment:
      ```
      OPENAI_API_KEY=your_openai_api_key
      HOST=localhost
      PORT=8001
      ```

3. **Run the backend server:**
    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```

---

## Frontend Setup (Angular)

1. **Install dependencies:**
    ```sh
    cd insightmate/frontend
    npm install
    ```

2. **Run the frontend:**
    ```sh
    ng serve
    ```
    - The app will be available at [http://localhost:4200](http://localhost:4200)

---

## Usage

- Open [http://localhost:4200](http://localhost:4200) in your browser.
- Use the chat, upload files, and add portfolio links.
- The backend API runs at [http://localhost:8001](http://localhost:8001).

---

## Project Structure

```
insightmate/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── services/
│       ├── ai_service.py
│       ├── data_service.py
│       └── file_service.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.ts
│   │   │   └── services/
│   │   │       ├── api.service.ts
│   │   │       └── chat.service.ts
│   │   └── styles.scss
│   └── ...
```

---

## Troubleshooting

- **CORS errors:** Ensure backend CORS settings allow your frontend origin.
- **OpenAI errors:** Make sure your API key is valid and set in the environment.
- **File upload issues:** Check file size and allowed file types in `config.py`.

---

## License

This project is for educational and demonstration purposes.

---

## Author

- Anubhav Sharma"# InsightMate" 
"# InsightMate" 
