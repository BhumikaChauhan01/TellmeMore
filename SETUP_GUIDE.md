# TellmeMore Setup Guide

## Quick Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Gemini API Key
1. Update the `.env` file with your actual Gemini API key:
```bash
# Replace with your actual API key
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3. Run Migrations (if needed)
```bash
python3 manage.py migrate
```

### 4. Start the Server
```bash
python3 manage.py runserver
```

### 5. Access the Application
- Open your browser and go to `http://127.0.0.1:8000`
- Create an account or login
- Navigate to Dashboard → Interview Requirements
- Upload your resume and fill in the details
- Start your AI interview session!

## Features Implemented

### ✅ Complete Backend Integration
- **Gemini 1.5 Flash API**: Latest model for intelligent question generation
- **Resume Parsing**: Upload PDF/DOCX resumes for AI analysis
- **Session Management**: Full database tracking of interview sessions
- **Voice Recognition**: Web Speech API for speaking your answers
- **Real-time Feedback**: AI evaluates answers and provides constructive feedback

### ✅ Interview Flow
1. **Resume Upload**: System parses and analyzes your resume
2. **Session Start**: Begin with "Tell me about yourself"
3. **Voice/Text Input**: Respond via microphone or typing
4. **AI Feedback**: Get real-time evaluation and suggestions
5. **Follow-up Questions**: AI generates contextual questions based on your profile
6. **Session Analytics**: Complete with scores and recommendations

### 🎤 Voice Features
- Click the microphone button to speak your answers
- Automatic speech-to-text conversion
- Fallback to text input if voice isn't supported

### 📄 Resume Analysis
- Upload PDF or DOCX files
- AI extracts key information and suggests interview focus areas
- Personalized questions based on your background

## Troubleshooting

### API Key Issues
- Make sure your `.env` file is in the root directory
- Verify your Gemini API key is valid and has credits
- Check the Django console for API error messages

### Voice Recognition
- Voice features work best in Chrome/Edge browsers
- Allow microphone permissions when prompted
- Use text input as fallback if voice doesn't work

### Database Issues
If you encounter database errors:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## System Requirements
- Python 3.8+
- Modern web browser (Chrome recommended for voice features)
- Active Gemini API key with credits
- Microphone access for voice input (optional)

## Next Steps
Your interview system is now ready! The AI will:
- Parse your resume automatically
- Generate personalized questions
- Provide real-time feedback
- Track your progress and improvement areas

Good luck with your mock interviews! 🚀
