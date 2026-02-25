import streamlit as st
import os
from pathlib import Path
import tempfile
from api_models import transcribe_audio, generate_notes, extract_keywords
from youtube_utils import download_youtube_audio, get_video_info, validate_youtube_url
from formatter import format_notes, extract_sections
import traceback
import time

# Page configuration
st.set_page_config(
    page_title="LectureAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS matching the screenshot aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Styles */
    .main {
        background-color: #F5F3EF;
        padding: 0;
    }
    
    .block-container {
        padding: 3rem 5rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Title Styling */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .main-title .ai-text {
        color: #D4A574;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #E5E5E5;
        padding-left: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        color: #999;
        padding: 1rem 0;
        border-bottom: 3px solid transparent;
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #E57373;
        border-bottom-color: #E57373;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        border: 1px solid #D4C4B0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        background-color: white;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #D4C4B0;
        border-radius: 12px;
        padding: 2rem;
        background-color: #FAFAF8;
        text-align: center;
    }
    
    [data-testid="stFileUploader"] label {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #666;
    }
    
    /* Button Styling */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        color: white;
        background: linear-gradient(135deg, #FF6B6B 0%, #E57373 100%);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(229, 115, 115, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(229, 115, 115, 0.4);
    }
    
    .stButton > button:before {
        content: "⚡ ";
        margin-right: 0.5rem;
    }
    
    /* Section Headers */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #D4C4B0;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #E8DCC8 0%, #F0E6D6 100%);
        border-left: 4px solid #D4A574;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #5C4A33;
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, #D4EDDA 0%, #E8F5E9 100%);
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #155724;
    }
    
    /* Error Box */
    .error-box {
        background: linear-gradient(135deg, #F8D7DA 0%, #FFEBEE 100%);
        border-left: 4px solid #F44336;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #721C24;
    }
    
    /* Notes Section */
    .notes-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    .topic-header {
        background: linear-gradient(135deg, #D4A574 0%, #C99A5E 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0;
    }
    
    .key-takeaway {
        background: #FFF9F0;
        border-left: 4px solid #D4A574;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
    }
    
    .theory-box {
        background: #F5F5F5;
        border-left: 4px solid #666;
        padding: 1.25rem;
        margin: 1rem 0;
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .example-box {
        background: #FFF0F0;
        border-left: 4px solid #E57373;
        padding: 1.25rem;
        margin: 1rem 0;
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-style: italic;
        line-height: 1.6;
    }
    
    /* Key Concepts Tags */
    .key-concepts {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }
    
    .concept-tag {
        background: #FFF9E6;
        border: 1px solid #D4A574;
        color: #5C4A33;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Progress Indicators */
    .stProgress > div > div {
        background-color: #E57373;
        height: 8px;
        border-radius: 4px;
    }
    
    /* Flowchart Section */
    .flowchart-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .flow-step {
        background: #F5F3EF;
        border-left: 4px solid #D4A574;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }
    
    .flow-step-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .flow-step-desc {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .flow-arrow {
        text-align: center;
        color: #D4A574;
        font-size: 1.5rem;
        margin: 0.5rem 0;
    }
    
    /* Download Button Styling */
    .stDownloadButton > button {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #5C4A33;
        background: white;
        border: 2px solid #D4A574;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #D4A574;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Transcript Container */
    .transcript-container {
        background: white;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 2rem;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
        color: #333;
    }
    
    /* Statistics */
    .stats-container {
        display: flex;
        gap: 2rem;
        margin: 1rem 0;
        padding: 1rem;
        background: #FAFAF8;
        border-radius: 8px;
    }
    
    .stat-item {
        font-family: 'Inter', sans-serif;
        color: #666;
        font-size: 0.9rem;
    }
    
    .stat-value {
        font-weight: 600;
        color: #1a1a1a;
        font-size: 1.1rem;
    }
    
    /* Spinner Override */
    .stSpinner > div {
        border-top-color: #E57373 !important;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    if 'notes' not in st.session_state:
        st.session_state.notes = None
    if 'keywords' not in st.session_state:
        st.session_state.keywords = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'flow_data' not in st.session_state:
        st.session_state.flow_data = None

def validate_api_keys():
    """Validate required API keys"""
    required_keys = {
        'ASSEMBLYAI_API_KEY': 'AssemblyAI',
        'GROQ_API_KEY': 'Groq'
    }
    
    missing_keys = []
    for key, name in required_keys.items():
        if not os.getenv(key):
            try:
                if key not in st.secrets:
                    missing_keys.append(name)
            except:
                missing_keys.append(name)
    
    return missing_keys

def display_header():
    """Display the main header"""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 4rem;">
            <h1 class="main-title">Lecture<span class="ai-text">AI</span></h1>
            <p class="subtitle">Intelligent, structured notes for Academic Lectures</p>
        </div>
    """, unsafe_allow_html=True)

def process_audio_file(file_path, file_type="uploaded"):
    """Process audio file and generate notes"""
    try:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Transcription
        status_text.markdown("🎙️ **Transcribing audio...** This may take a few minutes.")
        progress_bar.progress(20)
        
        transcript = transcribe_audio(file_path)
        
        if not transcript or len(transcript.strip()) < 50:
            st.error("⚠️ Transcription failed or returned insufficient content.")
            return False
        
        st.session_state.transcript = transcript
        progress_bar.progress(60)
        status_text.markdown("✅ **Transcript generated.**")
        
        # Extract keywords
        status_text.markdown("🔍 **Extracting key concepts...**")
        progress_bar.progress(70)
        keywords = extract_keywords(transcript, max_keywords=10)
        st.session_state.keywords = keywords
        
        # Generate notes
        status_text.markdown("🤖 **Analyzing lecture structure...** Please wait.")
        progress_bar.progress(80)
        
        notes = generate_notes(transcript)
        
        if not notes:
            st.error("⚠️ Note generation failed. Please try again.")
            return False
        
        st.session_state.notes = notes
        progress_bar.progress(100)
        status_text.markdown("✅ **Notes generated successfully!**")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return True
        
    except Exception as e:
        st.markdown(f'<div class="error-box">❌ Error processing audio: {str(e)}</div>', 
                   unsafe_allow_html=True)
        with st.expander("View detailed error"):
            st.code(traceback.format_exc())
        return False

def display_notes_section():
    """Display the generated notes in a structured format"""
    if not st.session_state.notes:
        return
    
    # Create tabs for different views
    notes_tab, flowchart_tab = st.tabs(["📝 Notes", "🔄 Flowchart"])
    
    with notes_tab:
        # Display key concepts as tags
        if st.session_state.keywords:
            st.markdown('<div class="section-header">Key Concepts</div>', unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.keywords) if len(st.session_state.keywords) <= 5 else 5)
            for i, keyword in enumerate(st.session_state.keywords[:5]):
                with cols[i % 5]:
                    st.markdown(f'<span class="concept-tag">{keyword}</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Display notes content
        st.markdown('<div class="notes-container">', unsafe_allow_html=True)
        
        # Parse and display sections
        sections = extract_sections(st.session_state.notes)
        
        for section_title, section_content in sections.items():
            if section_title.lower() == "introduction":
                st.markdown(f'<div class="section-header">{section_title} 🔗</div>', unsafe_allow_html=True)
                st.markdown(section_content)
            elif "topic" in section_title.lower() or "technique" in section_title.lower():
                st.markdown(f'<div class="topic-header">{section_title}</div>', unsafe_allow_html=True)
                
                # Parse theory and examples
                if "Theory:" in section_content:
                    parts = section_content.split("Example:")
                    theory_part = parts[0].replace("Theory:", "").strip()
                    st.markdown(f'<div class="theory-box"><strong>Theory:</strong> {theory_part}</div>', 
                              unsafe_allow_html=True)
                    
                    if len(parts) > 1:
                        example_part = parts[1].strip()
                        st.markdown(f'<div class="example-box"><strong>Example:</strong> {example_part}</div>', 
                                  unsafe_allow_html=True)
                else:
                    st.markdown(section_content)
            else:
                st.markdown(f'<div class="section-header">{section_title}</div>', unsafe_allow_html=True)
                st.markdown(section_content)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.notes,
                file_name="lecture_notes.md",
                mime="text/markdown"
            )
        with col2:
            st.download_button(
                label="📥 Download TXT",
                data=st.session_state.notes,
                file_name="lecture_notes.txt",
                mime="text/plain"
            )
    
    with flowchart_tab:
        st.markdown('<div class="flowchart-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">Sequence Flow</div>', unsafe_allow_html=True)
        
        # Example flow steps (you can make this dynamic based on content)
        flow_steps = [
            {"title": "Start with a hook", "desc": "Grab the audience's attention with an interesting fact or story"},
            {"title": "Set the location", "desc": "Establish the setting and create a mental image"},
            {"title": "Introduce actions", "desc": "Bring forward momentum and create a sense of movement"},
            {"title": "Share thoughts and emotions", "desc": "Make the story more relatable and personal"},
            {"title": "Use dialogue", "desc": "Add depth and variety to the story"}
        ]
        
        for step in flow_steps:
            st.markdown(f'''
                <div class="flow-step">
                    <div class="flow-step-title">{step["title"]}</div>
                    <div class="flow-step-desc">{step["desc"]}</div>
                </div>
                <div class="flow-arrow">↓</div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_transcript_section():
    """Display the full transcript"""
    if not st.session_state.transcript:
        return
    
    st.markdown('<div class="section-header">Full Transcript</div>', unsafe_allow_html=True)
    
    # Display transcript in a styled container
    st.markdown(f'''
        <div class="transcript-container">
            {st.session_state.transcript}
        </div>
    ''', unsafe_allow_html=True)
    
    # Statistics
    word_count = len(st.session_state.transcript.split())
    char_count = len(st.session_state.transcript)
    
    st.markdown(f'''
        <div class="stats-container">
            <div class="stat-item">
                <div class="stat-value">{word_count:,}</div>
                <div>Words</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{char_count:,}</div>
                <div>Characters</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Transcript",
        data=st.session_state.transcript,
        file_name="transcript.txt",
        mime="text/plain"
    )

def main():
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Check API keys
    missing_keys = validate_api_keys()
    if missing_keys:
        st.markdown(f'''
            <div class="error-box">
                <strong>⚠️ Missing API Keys:</strong> {', '.join(missing_keys)}<br><br>
                Please configure your API keys in <code>.streamlit/secrets.toml</code> or as environment variables.
            </div>
        ''', unsafe_allow_html=True)
        with st.expander("📖 How to set up API keys"):
            st.markdown("""
            **Option 1: Streamlit Secrets (Recommended)**
            1. Create `.streamlit/secrets.toml` in your project
            2. Add:
            ```toml
            ASSEMBLYAI_API_KEY = "your_key_here"
            GROQ_API_KEY = "your_key_here"
            ```
            
            **Option 2: Environment Variables**
            ```bash
            export ASSEMBLYAI_API_KEY="your_key_here"
            export GROQ_API_KEY="your_key_here"
            ```
            
            **Get API Keys:**
            - AssemblyAI: https://www.assemblyai.com/
            - Groq: https://console.groq.com/
            """)
    
    # Main tabs
    tabs = st.tabs(["🎵 Audio Upload", "▶️ YouTube URL"])
    
    # Tab 1: Upload Audio
    with tabs[0]:
        st.markdown('<div class="section-header">Upload English audio recording</div>', 
                   unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drag and drop file here",
            type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg4'],
            help="Limit 200MB per file • MP3, WAV, M4A, MP4, MPEG4",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.markdown('<div class="info-box">✓ File uploaded successfully</div>', 
                       unsafe_allow_html=True)
            
            if st.button("Generate Notes", disabled=st.session_state.processing or bool(missing_keys)):
                if missing_keys:
                    st.error("Please configure API keys first!")
                else:
                    st.session_state.processing = True
                    
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        success = process_audio_file(tmp_path, "uploaded")
                        if success:
                            st.rerun()
                    finally:
                        # Cleanup
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                        st.session_state.processing = False
    
    # Tab 2: YouTube URL
    with tabs[1]:
        st.markdown('<div class="section-header">YouTube Lecture URL</div>', 
                   unsafe_allow_html=True)
        
        youtube_url = st.text_input(
            "Enter YouTube URL",
            placeholder="https://youtu.be/hNuAv-42jzY?si=Vnu6F-UuUbjSHXJs",
            label_visibility="collapsed"
        )
        
        if youtube_url:
            if validate_youtube_url(youtube_url):
                st.markdown('<div class="info-box">✓ Source link detected.</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">⚠️ Invalid YouTube URL</div>', 
                           unsafe_allow_html=True)
            
            if st.button("Generate Notes", key="yt_generate", 
                        disabled=st.session_state.processing or bool(missing_keys)):
                if missing_keys:
                    st.error("Please configure API keys first!")
                elif not validate_youtube_url(youtube_url):
                    st.error("Please enter a valid YouTube URL")
                else:
                    st.session_state.processing = True
                    
                    try:
                        # Download audio
                        with st.spinner("📥 Downloading audio from YouTube..."):
                            audio_path = download_youtube_audio(youtube_url)
                        
                        if audio_path and os.path.exists(audio_path):
                            success = process_audio_file(audio_path, "YouTube")
                            
                            # Cleanup
                            if os.path.exists(audio_path):
                                os.unlink(audio_path)
                            
                            if success:
                                st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', 
                                  unsafe_allow_html=True)
                        with st.expander("View detailed error"):
                            st.code(traceback.format_exc())
                    finally:
                        st.session_state.processing = False
    
    # Results section
    if st.session_state.notes or st.session_state.transcript:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<hr style="border: 1px solid #E5E5E5; margin: 3rem 0;">', unsafe_allow_html=True)
        
        result_tabs = st.tabs(["📝 Notes", "📜 Full Transcript"])
        
        with result_tabs[0]:
            display_notes_section()
        
        with result_tabs[1]:
            display_transcript_section()

if __name__ == "__main__":
    main()
