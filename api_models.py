import streamlit as st
import os
from pathlib import Path
import tempfile
from api_models import transcribe_audio, generate_notes, extract_keywords
from formatter import format_notes, extract_sections
import traceback
import time

# Page configuration
st.set_page_config(
    page_title="LectureAI",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Elegant serif CSS matching reference design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,300;1,8..60,400&display=swap');
    
    :root {
        --cream: #FAF7F2;
        --parchment: #F2EDE3;
        --paper: #EDE6D6;
        --ink: #1C1612;
        --ink-soft: #3D342A;
        --ink-muted: #7A6E62;
        --amber: #C8831A;
        --sienna: #9B4A1E;
        --border: rgba(120,100,75,0.16);
    }
    
    *, body {
        font-family: 'Source Serif 4', Georgia, serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--cream) !important;
        color: var(--ink);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Title Block */
    .title-block {
        padding: 2.5rem 0;
        text-align: center;
        border-bottom: 2px solid var(--border);
        margin-bottom: 1.8rem;
    }
    
    .title-block h1 {
        font-family: 'Playfair Display', serif;
        font-weight: 900;
        font-size: 3rem;
        color: var(--ink);
        margin: 0;
    }
    
    .title-block h1 em {
        color: var(--amber);
        font-style: italic;
    }
    
    .title-block p {
        font-size: 1.1rem;
        color: var(--ink-muted);
        margin-top: 0.5rem;
    }
    
    .title-block .subtitle-highlight {
        color: var(--amber);
        font-weight: 600;
        font-size: 1.05rem;
        margin-top: 0.75rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid var(--border);
        padding-left: 0;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Source Serif 4', serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: var(--ink-muted);
        padding: 1rem 0;
        border-bottom: 3px solid transparent;
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--amber);
        border-bottom-color: var(--amber);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border);
        border-radius: 4px;
        padding: 2rem;
        background-color: var(--parchment);
        text-align: center;
    }
    
    [data-testid="stFileUploader"] label {
        font-family: 'Source Serif 4', serif;
        font-size: 1rem;
        color: var(--ink-soft);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        font-family: 'Source Serif 4', serif;
        font-size: 1rem;
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.75rem 1rem;
        background-color: white;
        color: var(--ink);
    }
    
    /* Button Styling */
    .stButton > button {
        font-family: 'Source Serif 4', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: white;
        background: var(--amber);
        border: none;
        border-radius: 4px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: var(--sienna);
        transform: translateY(-1px);
    }
    
    /* Topic Cards */
    .topic-card {
        background: var(--parchment);
        border: 1px solid var(--border);
        border-radius: 4px;
        margin-bottom: 1.2rem;
        overflow: hidden;
    }
    
    .topic-header {
        background: var(--amber);
        padding: 0.6rem 1.1rem;
        color: white;
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        font-size: 1.15rem;
    }
    
    .topic-body {
        padding: 1rem 1.2rem;
        line-height: 1.7;
    }
    
    /* Theory and Example Blocks */
    .theory-block {
        background: rgba(200,131,26,0.05);
        border-left: 3px solid var(--amber);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 2px;
    }
    
    .example-block {
        background: #F0D5C4;
        border-left: 3px solid var(--sienna);
        padding: 0.8rem;
        font-style: italic;
        margin: 0.5rem 0;
        border-radius: 2px;
    }
    
    /* Keyword Pills */
    .keyword-pill {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        background: #F5DFA8;
        border: 1px solid rgba(200,131,26,0.3);
        border-radius: 3px;
        margin: 0.3rem;
        font-size: 0.85rem;
        color: var(--ink-soft);
    }
    
    /* Info Box */
    .info-box {
        background: var(--parchment);
        border: 1px solid var(--border);
        border-left: 4px solid var(--amber);
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: var(--ink-soft);
    }
    
    /* Success Box */
    .success-box {
        background: #E8F5E9;
        border: 1px solid rgba(76,175,80,0.3);
        border-left: 4px solid #4CAF50;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    
    /* Error Box */
    .error-box {
        background: #FFEBEE;
        border: 1px solid rgba(244,67,54,0.3);
        border-left: 4px solid #F44336;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721C24;
    }
    
    /* Flow Nodes */
    .flow-node {
        background: var(--parchment);
        border: 1.5px solid var(--border);
        padding: 1rem;
        text-align: center;
        margin: 0.5rem auto;
        width: 80%;
        border-radius: 4px;
        border-left: 5px solid var(--amber);
    }
    
    .flow-node strong {
        color: var(--ink);
        font-size: 1.05rem;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        font-family: 'Source Serif 4', serif;
        font-size: 0.95rem;
        color: var(--ink);
        background: var(--paper);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.6rem 1.5rem;
    }
    
    .stDownloadButton > button:hover {
        background: var(--parchment);
        border-color: var(--amber);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-color: var(--amber);
        height: 6px;
        border-radius: 3px;
    }
    
    /* Text Area (Transcript) */
    .stTextArea textarea {
        font-family: 'Source Serif 4', serif;
        background-color: white;
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--ink);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Source Serif 4', serif;
        color: var(--ink-soft);
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
        <div class="title-block">
            <h1>Lecture<em>AI</em></h1>
            <p>Intelligent, structured notes for Academic Lectures</p>
            <p class="subtitle-highlight">⭐ Now with Live Recording - Create notes from your voice instantly!</p>
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
    notes_tab, flowchart_tab = st.tabs(["📖 Notes", "⟳ Flowchart"])
    
    with notes_tab:
        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            # Parse notes content
            sections = extract_sections(st.session_state.notes)
            
            # Display Introduction
            if "introduction" in sections or "Introduction" in sections:
                intro_key = "introduction" if "introduction" in sections else "Introduction"
                st.markdown(f"### Introduction")
                st.markdown(sections[intro_key])
            
            # Display Topics
            topic_num = 1
            for section_title, section_content in sections.items():
                if "topic" in section_title.lower() or "technique" in section_title.lower():
                    st.markdown(f"""
                    <div class="topic-card">
                        <div class="topic-header">{section_title}</div>
                        <div class="topic-body">
                    """, unsafe_allow_html=True)
                    
                    # Parse theory and examples
                    if "Theory:" in section_content or "**Theory:**" in section_content:
                        parts = section_content.split("Example:")
                        theory_part = parts[0].replace("Theory:", "").replace("**Theory:**", "").strip()
                        
                        st.markdown(f'<div class="theory-block"><strong>Theory:</strong> {theory_part}</div>', 
                                  unsafe_allow_html=True)
                        
                        if len(parts) > 1:
                            example_part = parts[1].replace("**Example:**", "").strip()
                            st.markdown(f'<div class="example-block"><strong>Example:</strong> {example_part}</div>', 
                                      unsafe_allow_html=True)
                    else:
                        st.markdown(section_content)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    topic_num += 1
            
            # Display Conclusion
            if "conclusion" in sections or "Conclusion" in sections:
                conclusion_key = "conclusion" if "conclusion" in sections else "Conclusion"
                st.markdown(f"### Conclusion")
                st.markdown(sections[conclusion_key])
            else:
                st.markdown('<div class="info-box">💡 Lecture appears to be a segment; no final conclusion was detected.</div>', 
                          unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="↓ Download Text Notes",
                data=st.session_state.notes,
                file_name="lecture_notes.txt",
                mime="text/plain"
            )
        
        with col_side:
            st.markdown("### Key Concepts")
            if st.session_state.keywords:
                pills_html = "".join(f'<span class="keyword-pill">{kw}</span>' for kw in st.session_state.keywords)
                st.markdown(pills_html, unsafe_allow_html=True)
            
            # Scrollable transcript
            with st.expander("📄 Full Transcript", expanded=False):
                st.text_area(
                    label="Transcript Area",
                    value=st.session_state.transcript,
                    height=450,
                    label_visibility="collapsed"
                )
    
    with flowchart_tab:
        st.markdown("### Sequence Flow")
        
        # Create simple flow steps from content
        flow_steps = [
            {"step": "Start with a hook", "desc": "Grab the audience's attention with an interesting fact or story"},
            {"step": "Set the location", "desc": "Establish the setting and create a mental image"},
            {"step": "Introduce actions", "desc": "Bring forward momentum and create a sense of movement"},
            {"step": "Share thoughts and emotions", "desc": "Make the story more relatable and personal"},
            {"step": "Use dialogue", "desc": "Add depth and variety to the story"}
        ]
        
        for i, step in enumerate(flow_steps):
            st.markdown(f'''
                <div class="flow-node">
                    <strong>{step["step"]}</strong><br>
                    {step["desc"]}
                </div>
            ''', unsafe_allow_html=True)
            
            if i < len(flow_steps) - 1:
                st.markdown('<div style="text-align:center; color: var(--amber); font-size: 1.5rem; margin: 0.5rem 0;">↓</div>', 
                          unsafe_allow_html=True)

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
            **Create `.streamlit/secrets.toml`:**
            ```toml
            ASSEMBLYAI_API_KEY = "your_key_here"
            GROQ_API_KEY = "your_key_here"
            ```
            
            **Get API Keys:**
            - AssemblyAI: https://www.assemblyai.com/
            - Groq: https://console.groq.com/
            """)
    
    # Main tabs
    tabs = st.tabs(["🎵 Audio Upload", "🎙️ Live Recording ⭐"])
    
    # Info about YouTube
    st.markdown("""
        <div class="info-box">
            💡 <strong>For YouTube videos:</strong> Download the audio using a browser extension 
            or online tool (like y2mate.com), then upload it here.
        </div>
    """, unsafe_allow_html=True)
    
    # Tab 1: Upload Audio
    with tabs[0]:
        uploaded_file = st.file_uploader(
            "Upload English audio recording",
            type=['mp3', 'wav', 'm4a', 'mp4', 'flac', 'ogg'],
            help="Limit 200MB per file • MP3, WAV, M4A, MP4, FLAC, OGG"
        )
        
        if uploaded_file is not None:
            st.markdown('<div class="success-box">✓ File uploaded successfully</div>', 
                       unsafe_allow_html=True)
            
            if st.button("⚡ Generate Notes", disabled=st.session_state.processing or bool(missing_keys)):
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
    
    # Tab 2: Live Recording
    with tabs[1]:
        from audio_recorder import get_audio_recorder_html, get_recording_instructions
        
        # Display instructions
        st.markdown(get_recording_instructions())
        
        # Display audio recorder
        st.components.v1.html(get_audio_recorder_html(), height=400)
        
        st.markdown("""
            <div class="info-box">
                <strong>💡 How it works:</strong><br>
                1. Click record button → speak your lecture<br>
                2. Click stop → file downloads automatically<br>
                3. Upload the downloaded file above<br>
                4. Generate notes!
            </div>
        """, unsafe_allow_html=True)
    
    # Results section
    if st.session_state.notes or st.session_state.transcript:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<hr style="border: 1px solid var(--border); margin: 3rem 0;">', unsafe_allow_html=True)
        
        display_notes_section()

if __name__ == "__main__":
    main()
