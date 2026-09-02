# Google Forms MCQ Solver

A local Python automation tool that uses **Playwright** to open Google Forms and **Groq AI** to solve multiple-choice questions automatically.

It supports:
- Google Forms links entered directly in the terminal
- Multiple forms in one run
- Persistent Google login session
- Automatic student information filling
- Automatic email-recording checkbox selection
- AI-powered MCQ solving using Groq
- Forms with labeled or unlabeled options
- Forms with extra/empty radio elements
- Optional/non-standard radio questions with a fallback selection
- Optional automatic form submission

> **Note:** This project is intended for personal/educational use. Use it only on forms you are authorized to access and submit.

---

## Requirements

- Python **3.10+**
- A Google account with access to the forms
- A **Groq API key**
- Windows, Linux, or macOS

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the repository URL with your GitHub repository URL.

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal after activation.

---

## 3. Install Python Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, install:

```bash
pip install playwright groq
```

Then install the Playwright browser:

```bash
python -m playwright install chromium
```

---

## 4. Get a Groq API Key

Create a Groq account and generate an API key from the Groq console.

Do **not** put the API key directly inside your Python files.

The project reads the key from:

```text
GROQ_API_KEY
```

### Windows PowerShell

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

### Windows CMD

```cmd
set GROQ_API_KEY=your_groq_api_key
```

### Linux / macOS

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Verify that the variable exists before running the program.

> For permanent environment-variable setup, use your operating system's environment-variable settings or your shell configuration.

---

## 5. Configure Student Information

Open:

```text
config.py
```

Set your information:

```python
EMAIL = "your@email.com"
NAME = "Your Name"
ROLL_NO = "12345"
BRANCH = "CSE"

AUTO_SUBMIT = False
```

### `AUTO_SUBMIT`

```python
AUTO_SUBMIT = False
```

The program will fill the answers but will **not submit** the form.

Set:

```python
AUTO_SUBMIT = True
```

if you want the program to automatically click the Google Forms **Submit** button.

For safety, it is recommended to keep:

```python
AUTO_SUBMIT = False
```

until you have tested the program.

---

## 6. First Run

Run:

```bash
python main.py
```

A Chromium browser will open.

On the first run:

1. Open the Google Form.
2. Log in to Google if required.
3. Complete any required Google authentication.
4. The program will then process the form.

The browser profile is stored locally in:

```text
google_profile/
```

This allows the Google login session to persist between runs.

### Important

Do **not** upload `google_profile/` to GitHub.

It may contain your browser session data.

---

## 7. Enter a Form Link

After starting the program:

```text
Enter Google Form link (or type 'exit'):
```

Paste the Google Form URL:

```text
https://docs.google.com/forms/d/e/...
```

The program will:

1. Open the form
2. Check the "Record email" option when available
3. Fill Email
4. Fill Name
5. Fill Roll No
6. Fill Branch
7. Detect MCQ questions
8. Send MCQs to Groq
9. Select the returned answers
10. Handle questions that cannot be processed by the AI
11. Submit if `AUTO_SUBMIT = True`

---

## 8. Process Multiple Forms

You can process multiple forms without restarting the program.

Example:

```text
Enter Google Form link (or type 'exit'): https://docs.google.com/forms/d/e/FORM1/...
```

After processing:

```text
Press Enter to continue to next form...
```

Then enter another form:

```text
Enter Google Form link (or type 'exit'): https://docs.google.com/forms/d/e/FORM2/...
```

Continue entering forms as needed.

When finished:

```text
Enter Google Form link (or type 'exit'): exit
```

The browser context will then close.

---

## Project Structure

```text
fcukQuizes/
│
├── main.py
├── solver.py
├── form_parser.py
├── config.py
├── requirements.txt
├── README.md
│
├── google_profile/        # Created automatically - DO NOT COMMIT
└── venv/                  # Local virtual environment - DO NOT COMMIT
```

Your exact files may differ depending on your project structure.

---

## Groq Model

The solver currently uses:

```python
MODEL = "openai/gpt-oss-20b"
```

The model is called through the Groq API.

The solver sends all detected MCQs in a **single API request** rather than making one request per question.

---

## How Question Handling Works

The program supports questions such as:

```text
A. Option A
B. Option B
C. Option C
D. Option D
```

and:

```text
Option A
Option B
Option C
Option D
```

It also handles Google Forms DOM variations where additional empty radio elements may appear.

For example:

```text
A
B
C
[empty radio]
D
```

The program attempts to identify the actual option text rather than relying only on radio-button indexes.

If a question cannot be processed correctly by the parser or AI, the program uses a fallback radio selection instead of stopping the entire run.

---

## Environment Variables

The project requires:

```text
GROQ_API_KEY
```

Example:

```text
GROQ_API_KEY=your_api_key_here
```

Never commit your real API key.

---

## `.gitignore`

Before pushing the project to GitHub, create a `.gitignore` file containing at least:

```gitignore
venv/
__pycache__/
*.pyc

google_profile/

.env
.env.*
```

If your API key is stored anywhere locally, make sure that file is also ignored.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'playwright'`

Activate your virtual environment and run:

```bash
pip install playwright
```

Then:

```bash
python -m playwright install chromium
```

---

### `ModuleNotFoundError: No module named 'groq'`

Run:

```bash
pip install groq
```

---

### `KeyError: 'GROQ_API_KEY'`

The API key environment variable is not available in the current terminal.

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

Linux/macOS:

```bash
export GROQ_API_KEY="your_groq_api_key"
```

Then run the program again.

---

### Browser does not open

Run:

```bash
python -m playwright install chromium
```

Then retry:

```bash
python main.py
```

---

### Google asks for login again

The Google session is stored in:

```text
google_profile/
```

Do not delete this folder if you want to keep the existing session.

If the session expires, log in again when Chromium opens.

---

### Form questions are not detected correctly

Google Forms can have different HTML structures depending on how the form was created.

Check the terminal output to see which questions were detected and whether the parser or selector failed.

---

## Security Notes

### Never commit:

- `GROQ_API_KEY`
- `google_profile/`
- personal credentials
- cookies/session data
- `.env` files containing secrets

Your Google browser profile can contain authentication/session information. Treat it as sensitive.

---

## Disclaimer

This software automates interaction with Google Forms and uses an AI model to select answers.

AI-generated answers can be incorrect. Always verify results when accuracy matters.

Use this project only with forms you are authorized to access and submit, and follow the rules of the organization or institution that owns the form.

---

## License

Add your preferred license here, for example:

```text
MIT License
```

If you choose MIT, add a `LICENSE` file containing the standard MIT License text.
