# LectureAI: Intelligent Academic Synthesis

Transform lecture recordings into organized study material with AI-powered transcription and note generation.

## 🌟 Features

- **Multiple Input Methods**
  - Upload audio files (MP3, WAV, M4A, MP4, FLAC, OGG)
  - Process YouTube videos directly via URL

- **AI-Powered Processing**
  - High-accuracy transcription using AssemblyAI Universal-3-pro
  - Intelligent note generation with Groq's Llama 3.3 70B

- **Structured Output**
  - Overview and key concepts
  - Detailed notes with hierarchical structure
  - Examples and applications
  - Key takeaways
  - Review questions

- **Export Options**
  - Download notes as Markdown (.md)
  - Download notes as plain text (.txt)
  - Download full transcript

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Transcription:** AssemblyAI (Universal-3-pro)
- **LLM:** Groq (Llama 3.3 70B)
- **Audio Processing:** yt-dlp, FFmpeg

## 📋 Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- API keys for:
  - AssemblyAI
  - Groq

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lecture-to-notes.git
cd lecture-to-notes
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**MacOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

**Option 1: Streamlit Secrets (Recommended for deployment)**

Create `.streamlit/secrets.toml`:
```toml
ASSEMBLYAI_API_KEY = "your_assemblyai_key_here"
GROQ_API_KEY = "your_groq_key_here"
```

**Option 2: Environment Variables (Local development)**

Create `.env` file:
```bash
ASSEMBLYAI_API_KEY=your_assemblyai_key_here
GROQ_API_KEY=your_groq_key_here
```

Or export directly:
```bash
export ASSEMBLYAI_API_KEY="your_key"
export GROQ_API_KEY="your_key"
```

## 🔑 Getting API Keys

### AssemblyAI
1. Sign up at [assemblyai.com](https://www.assemblyai.com/)
2. Navigate to your dashboard
3. Copy your API key

### Groq
1. Sign up at [console.groq.com](https://console.groq.com/)
2. Create a new API key
3. Copy the key

## 📖 Usage

### Running Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Application

1. **Upload Audio File**
   - Click on "Upload Audio" tab
   - Select or drag-and-drop your audio file
   - Click "Process Audio"

2. **Process YouTube Video**
   - Click on "YouTube URL" tab
   - Paste the YouTube video URL
   - Click "Process Video"

3. **View Results**
   - Generated notes appear in the "Generated Notes" tab
   - Full transcript available in "Full Transcript" tab
   - Download notes in your preferred format

## 🌐 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in the Streamlit Cloud dashboard:
   - `ASSEMBLYAI_API_KEY`
   - `GROQ_API_KEY`
5. Deploy!

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t lecture-ai .
docker run -p 8501:8501 \
  -e ASSEMBLYAI_API_KEY=your_key \
  -e GROQ_API_KEY=your_key \
  lecture-ai
```

## 📁 Project Structure

```
lecture-to-notes/
├── app.py                  # Main Streamlit application
├── api_models.py          # API integrations (AssemblyAI, Groq)
├── youtube_utils.py       # YouTube download utilities
├── formatter.py           # Note formatting functions
├── keyword_utils.py       # Keyword extraction utilities
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Configuration

### Customizing Note Generation

Edit the `system_prompt` in `api_models.py` to customize the note format:

```python
system_prompt = """Your custom prompt here..."""
```

### Adjusting Transcription Settings

Modify transcription config in `api_models.py`:

```python
config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.best,
    language_code="en",  # Change language
    punctuate=True,
    format_text=True,
)
```

## 🐛 Troubleshooting

### "API key not found" error
- Ensure API keys are properly set in secrets or environment
- Restart the Streamlit app after setting keys

### "Transcription failed" error
- Check audio file quality and format
- Ensure audio contains speech in English
- Verify AssemblyAI API key is valid

### "YouTube download failed" error
- Verify the YouTube URL is valid
- Check internet connection
- Ensure FFmpeg is installed

### Import errors
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [AssemblyAI](https://www.assemblyai.com/) for transcription API
- [Groq](https://groq.com/) for fast LLM inference
- [Streamlit](https://streamlit.io/) for the web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloads

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ for students and lifelong learners**
