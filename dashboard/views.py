import json
import os
import PyPDF2
import docx
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dashboard.models import InterviewDetails, PresentationPractice, CommunicationPractice, CustomQuestionSet, CustomQuestion, UserProfile, InterviewSession, SessionQuestion
import google.generativeai as genai
from django.utils import timezone
from datetime import timedelta

# ---------------- Dashboard Pages ---------------- #

@login_required
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")

@login_required
def my_sessions(request):
    # user_answers = AIInterviewAnswer.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "dashboard/my_sessions.html")

@login_required
def uploaded_items(request):
    return render(request, "dashboard/uploaded_items.html")

@login_required
def analytics(request):
    from dashboard.models import InterviewSession, SessionAnalytics
    from django.db.models import Avg, Count, Max
    
    # Get user's sessions
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-started_at')
    recent_sessions = sessions[:5]
    
    # Calculate analytics
    analytics_data = {
        'total_sessions': sessions.count(),
        'recent_sessions': recent_sessions,
    }
    
    if sessions.exists():
        # Calculate average scores
        avg_score = sessions.filter(overall_confidence_score__isnull=False).aggregate(
            avg_confidence=Avg('overall_confidence_score')
        )
        analytics_data['average_score'] = round(avg_score['avg_confidence'] or 0, 1)
        
        # Best score
        best_session = sessions.filter(overall_confidence_score__isnull=False).aggregate(
            best=Max('overall_confidence_score')
        )
        analytics_data['best_score'] = round(best_session['best'] or 0, 1)
        
        # Calculate total practice time (in hours)
        total_minutes = sum([s.duration_minutes for s in sessions if s.duration_minutes])
        analytics_data['total_practice_hours'] = round(total_minutes / 60, 1)
    else:
        analytics_data.update({
            'average_score': 0,
            'best_score': 0,
            'total_practice_hours': 0,
        })
    
    return render(request, "dashboard/analytics.html", analytics_data)

@login_required
def category_view(request):
    return render(request, "dashboard/category.html")

# ---------------- Interview Requirements ---------------- #
@login_required
def interview_requirements_view(request):
    try:
        interview = InterviewDetails.objects.get(user=request.user)
    except InterviewDetails.DoesNotExist:
        interview = None

    if request.method == "POST":
        if interview:
            interview_instance = interview
        else:
            interview_instance = InterviewDetails(user=request.user)

        interview_instance.full_name = request.POST.get("full_name")
        interview_instance.email = request.POST.get("email")
        interview_instance.phone = request.POST.get("phone")
        interview_instance.education = request.POST.get("education")
        interview_instance.branch = request.POST.get("branch")
        interview_instance.skills = request.POST.get("skills")
        interview_instance.experience = request.POST.get("experience")
        interview_instance.about_you = request.POST.get("about_you")
        interview_instance.role = request.POST.get("role")
        interview_instance.domain = request.POST.get("domain")
        interview_instance.difficulty = request.POST.get("difficulty")
        interview_instance.mode = request.POST.get("mode")
        interview_instance.time_per_question = int(request.POST.get("time_per_question", 60))
        interview_instance.num_questions = int(request.POST.get("num_questions", 5))
        interview_instance.custom_keywords = request.POST.get("custom_keywords")

        # Handle resume upload and parsing
        if request.FILES.get("resume_file"):
            resume_file = request.FILES["resume_file"]
            interview_instance.resume_file = resume_file
            
            # Parse resume content
            try:
                resume_text = parse_resume_text(resume_file)
                user_details = {
                    'full_name': interview_instance.full_name,
                    'education': interview_instance.education,
                    'skills': interview_instance.skills,
                    'experience': interview_instance.experience
                }
                
                # Generate AI analysis of resume
                ai_analysis = generate_user_profile_from_resume(resume_text, user_details)
                
                # Store the analysis in the about_you field or create a separate field
                if ai_analysis and not interview_instance.about_you:
                    interview_instance.about_you = f"AI Resume Analysis:\n{ai_analysis}"
                    
            except Exception as e:
                print(f"Resume parsing error: {e}")

        interview_instance.save()
        return redirect("dashboard:ai_page")

    return render(request, "dashboard/interview_requirements.html", {
        'interview': interview
    })


# ---------------- Presentation Requirements ---------------- #
@login_required
def presentation_requirements_view(request):
    if request.method == "POST":
        PresentationPractice.objects.create(
            user=request.user,
            topic_name=request.POST.get("topic_name"),
            description=request.POST.get("description"),
            audience_type=request.POST.get("audience_type"),
            ppt_file=request.FILES.get("ppt_file"),
            time_per_question=request.POST.get("time_per_question", 60),
            num_questions=request.POST.get("num_questions", 5),
            custom_keywords=request.POST.get("custom_keywords")
        )
        return redirect("dashboard:dashboard")

    return render(request, "dashboard/presentation_requirements.html")


# ---------------- Communication Requirements ---------------- #
@login_required
def communication_requirements_view(request):
    if request.method == "POST":
        CommunicationPractice.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            age=request.POST.get("age"),
            email=request.POST.get("email"),
            language=request.POST.get("language"),
            language_proficiency=request.POST.get("language_proficiency"),
            mode=request.POST.get("mode"),
            reason=request.POST.get("reason"),
            custom_reason=request.POST.get("custom_reason"),
            time_per_round=int(request.POST.get("time_per_round", 60)),
            num_rounds=int(request.POST.get("num_rounds", 3)),
        )
        return redirect("dashboard:dashboard")

    return render(request, "dashboard/communication_requirements.html")


# ---------------- Custom Questions ---------------- #
@login_required
def question_requirements_view(request):
    if request.method == "POST":
        question_set = CustomQuestionSet.objects.create(
            user=request.user,
            topic_name=request.POST.get("topic_name"),
            short_description=request.POST.get("short_description"),
            num_questions=int(request.POST.get("num_questions", 5)),
            time_per_question=int(request.POST.get("time_per_question", 60))
        )

        questions = []
        for key, value in request.POST.items():
            if key.startswith("question_") and value.strip():
                questions.append(CustomQuestion(question_set=question_set, question_text=value.strip()))
        CustomQuestion.objects.bulk_create(questions)

        return redirect("dashboard:dashboard")

    return render(request, "dashboard/question_requirements.html")


# ---------------- Profile ---------------- #
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "dashboard/profile.html", {"profile": profile, "user": request.user})

@login_required
def profile_edit_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        profile.gender = request.POST.get("gender")
        profile.dob = request.POST.get("dob")
        profile.bio = request.POST.get("bio")

        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()
        return redirect("dashboard:profile")

    return render(request, "dashboard/profile_edit.html", {
        "profile": profile,
        "user": request.user
    })

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyCPyL7RbHSf22xH4vPbk1UB7ETLJ4kq2Xg")
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    model = None
    print(f"Gemini API configuration failed: {e}")

# Resume parsing functionality
def parse_resume_text(file):
    """Extract text content from uploaded resume files (PDF or DOCX)"""
    try:
        if file.name.lower().endswith('.pdf'):
            reader = PyPDF2.PdfReader(BytesIO(file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.name.lower().endswith('.docx'):
            doc = docx.Document(BytesIO(file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return "Unsupported file format. Please upload PDF or DOCX files."
    except Exception as e:
        return f"Error parsing resume: {str(e)}"

def generate_user_profile_from_resume(resume_text, user_details):
    """Use Gemini to analyze resume and extract key information"""
    if not model:
        return "Unable to analyze resume - AI service not available"
    
    try:
        prompt = f"""
        Analyze this resume and extract key professional information:
        
        Resume Content:
        {resume_text}
        
        Additional User Info:
        - Name: {user_details.get('full_name', 'Not provided')}
        - Education: {user_details.get('education', 'Not provided')}
        - Skills: {user_details.get('skills', 'Not provided')}
        - Experience: {user_details.get('experience', 'Not provided')}
        
        Please provide a comprehensive professional summary in this format:
        
        PROFESSIONAL SUMMARY:
        [2-3 sentence summary of candidate's profile]
        
        KEY STRENGTHS:
        - [List 3-4 key strengths/skills]
        
        EXPERIENCE HIGHLIGHTS:
        - [List 2-3 key experiences or achievements]
        
        SUGGESTED INTERVIEW FOCUS AREAS:
        - [List 3-4 topics that should be covered based on their background]
        
        Keep the analysis professional and interview-focused.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

@require_http_methods(["POST"])
@login_required
def start_interview_session(request):
    """Create a new interview session"""
    try:
        interview_details = InterviewDetails.objects.get(user=request.user)
        
        # Create new session
        session = InterviewSession.objects.create(
            user=request.user,
            interview_details=interview_details,
            total_questions=interview_details.num_questions,
            status='active'
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'message': 'Interview session started successfully'
        })
        
    except InterviewDetails.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Please complete interview requirements first'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
@login_required
def generate_question(request):
    try:
        data = json.loads(request.body)
        question_number = data.get('question_number', 1)
        context = data.get('context', {})
        previous_answers = data.get('previous_answers', [])
        session_id = data.get('session_id')
        
        # Get interview details for better context
        try:
            interview_details = InterviewDetails.objects.get(user=request.user)
            context.update({
                'position': interview_details.role or 'Software Developer',
                'skills': interview_details.skills or 'General skills',
                'difficulty': interview_details.difficulty,
                'mode': interview_details.mode or 'technical',
                'experience': interview_details.experience,
                'about_you': interview_details.about_you
            })
        except InterviewDetails.DoesNotExist:
            pass
        
        # First question is always "Tell me about yourself"
        if question_number == 1:
            question = "Tell me something about yourself - your background, experience, and what interests you about this role."
            
            # Store question in session if session_id provided
            if session_id:
                try:
                    session = InterviewSession.objects.get(id=session_id, user=request.user)
                    SessionQuestion.objects.create(
                        session=session,
                        question_number=question_number,
                        question_text=question
                    )
                except InterviewSession.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'question': question
            })
        
        if model:
            # Create detailed prompt for Gemini 1.5 Flash
            prompt = f"""
            You are an experienced {context.get('mode', 'technical')} interviewer conducting an interview for a {context.get('position', 'Software Developer')} position.
            
            Candidate Profile:
            - Position: {context.get('position', 'Software Developer')}
            - Skills: {context.get('skills', 'General skills')}
            - Experience Level: {context.get('experience', 'Not specified')}
            - Difficulty Level: {context.get('difficulty', 'medium')}
            - Interview Type: {context.get('mode', 'technical')}
            
            Question Number: {question_number}
            Previous candidate responses: {previous_answers if previous_answers else 'None (first question was about themselves)'}
            
            Generate a relevant follow-up interview question that:
            1. Builds naturally on their self-introduction and previous responses
            2. Matches the {context.get('difficulty', 'medium')} difficulty level
            3. Is appropriate for a {context.get('mode', 'technical')} interview
            4. Tests relevant skills: {context.get('skills', 'problem-solving')}
            5. Is professional, clear, and engaging
            6. Helps evaluate their suitability for the {context.get('position', 'Software Developer')} role
            
            Provide ONLY the question text, no introductions or explanations.
            """
            
            response = model.generate_content(prompt)
            question = response.text.strip()
            
            # Store question in session if session_id provided
            if session_id:
                try:
                    session = InterviewSession.objects.get(id=session_id, user=request.user)
                    SessionQuestion.objects.create(
                        session=session,
                        question_number=question_number,
                        question_text=question
                    )
                except InterviewSession.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'question': question
            })
        else:
            # Fallback questions when API is not available
            fallback_questions = {
                'technical': [
                    "Tell me something about yourself.",
                    f"Walk me through your experience with {context.get('skills', 'programming').split(',')[0].strip()}.",
                    "Describe a challenging technical problem you solved recently.",
                    "How do you approach debugging when something isn't working as expected?",
                    "What technologies are you most excited to learn or work with?"
                ],
                'hr': [
                    "Tell me something about yourself.",
                    "Why are you interested in this position and our company?",
                    "Describe a time when you had to work under pressure. How did you handle it?",
                    "What do you consider your greatest professional achievement?",
                    "How do you handle feedback and criticism?"
                ],
                'gd': [
                    "Tell me something about yourself.",
                    f"What are your thoughts on current trends in {context.get('skills', 'technology').split(',')[0].strip()}?",
                    "How do you think remote work has changed the workplace?",
                    "What role should continuous learning play in a professional's career?",
                    "How can teams better collaborate in today's work environment?"
                ]
            }
            
            mode = context.get('mode', 'technical')
            questions = fallback_questions.get(mode, fallback_questions['technical'])
            question = questions[(question_number - 1) % len(questions)]
            
            return JsonResponse({
                'success': True,
                'question': question
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["POST"])
@login_required
def submit_answer(request):
    """Submit and evaluate user's answer"""
    try:
        data = json.loads(request.body)
        answer = data.get('answer', '')
        question_number = data.get('question_number', 1)
        session_id = data.get('session_id')
        time_taken = data.get('time_taken', 0)
        
        if not answer or not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Answer and session ID are required'
            })
        
        # Get session and update question with answer
        try:
            session = InterviewSession.objects.get(id=session_id, user=request.user)
            question_obj = SessionQuestion.objects.get(
                session=session, 
                question_number=question_number
            )
            
            # Update question with user's answer
            question_obj.user_answer = answer
            question_obj.answered_at = timezone.now()
            question_obj.time_taken_seconds = time_taken
            question_obj.save()
            
            # Update session progress
            session.questions_answered += 1
            session.save()
            
        except (InterviewSession.DoesNotExist, SessionQuestion.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'Session or question not found'
            })
        
        # Get context for evaluation
        context = {
            'position': session.interview_details.role or 'Software Developer',
            'skills': session.interview_details.skills or 'General skills',
            'difficulty': session.interview_details.difficulty,
            'mode': session.interview_details.mode or 'technical'
        }
        
        # Evaluate answer with Gemini
        feedback = await_evaluate_answer_with_gemini(answer, question_number, context, question_obj.question_text)
        
        # Store evaluation results
        if feedback:
            question_obj.ai_feedback = feedback
            question_obj.save()
        
        return JsonResponse({
            'success': True,
            'feedback': feedback,
            'session_progress': {
                'answered': session.questions_answered,
                'total': session.total_questions
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def await_evaluate_answer_with_gemini(answer, question_number, context, question_text):
    """Evaluate answer using Gemini and return feedback"""
    if not model or not answer:
        return "Thank you for your response. Let's continue to the next question."
    
    try:
        prompt = f"""
        You are an experienced {context.get('mode', 'technical')} interviewer evaluating a candidate's response.
        
        Interview Context:
        - Position: {context.get('position', 'Software Developer')}
        - Skills Focus: {context.get('skills', 'General skills')}
        - Difficulty Level: {context.get('difficulty', 'medium')}
        - Interview Type: {context.get('mode', 'technical')}
        
        Question #{question_number}: "{question_text}"
        Candidate's Answer: "{answer}"
        
        Provide constructive feedback that:
        1. Acknowledges specific strengths in their response
        2. Identifies areas for improvement (if any)
        3. Is encouraging and professional
        4. Offers actionable suggestions for better answers
        5. Is concise but insightful (2-3 sentences maximum)
        6. Helps them prepare for similar questions in real interviews
        
        Focus on content quality, communication clarity, and relevance to the role.
        Provide ONLY the feedback text, no formatting or introductions.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return "Thank you for your response. Let's continue to the next question."

@require_http_methods(["POST"])
@login_required
def evaluate_answer(request):
    """Legacy endpoint - redirect to submit_answer"""
    return submit_answer(request)

@require_http_methods(["POST"])
@login_required
def end_interview_session(request):
    """End the current interview session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID is required'
            })
        
        # Get and update session
        try:
            session = InterviewSession.objects.get(id=session_id, user=request.user)
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()
            
            # Calculate basic analytics
            questions = SessionQuestion.objects.filter(session=session)
            if questions.exists():
                # Calculate average scores (simplified for now)
                session.overall_confidence_score = 75.0  # Placeholder
                session.communication_score = 80.0      # Placeholder
                session.technical_score = 70.0          # Placeholder
                session.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Session completed successfully',
                'session_summary': {
                    'total_questions': session.total_questions,
                    'questions_answered': session.questions_answered,
                    'duration_minutes': round(session.duration_minutes, 1),
                    'overall_score': session.overall_confidence_score
                }
            })
            
        except InterviewSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def simple_interview_view(request):
    """Simple interview view with single question and AI feedback"""
    # Simple interview questions
    questions = [
        "Tell me about yourself and your professional background.",
        "Describe a challenging project you worked on and how you handled it.",
        "What are your greatest strengths and how do they apply to this role?",
        "Where do you see yourself in 5 years?",
        "Why are you interested in this position?",
        "How do you handle working under pressure?",
        "What is your biggest weakness and how are you working to improve it?",
        "Describe a time when you had to work with a difficult team member.",
        "What motivates you in your work?",
        "How do you stay updated with industry trends and technologies?"
    ]
    
    import random
    current_question = random.choice(questions)
    
    if request.method == 'POST':
        user_answer = request.POST.get('answer', '').strip()
        
        if user_answer:
            # Generate feedback using Gemini
            feedback = generate_simple_feedback(current_question, user_answer)
            
            return render(request, 'dashboard/simple_interview.html', {
                'submitted': True,
                'question': current_question,
                'user_answer': user_answer,
                'feedback': feedback.replace("**", "")
            })
    
    return render(request, 'dashboard/simple_interview.html', {
        'submitted': False,
        'question': current_question
    })

def generate_simple_feedback(question, answer):
    """Generate simple feedback using Gemini API"""
    if not model:
        return "AI feedback is currently unavailable. Please check your API configuration."
    
    try:
        prompt = f"""
        You are an experienced interview coach. Please provide constructive feedback on this interview response.

        Question: {question}

        Candidate's Answer: {answer}

        Please provide feedback that includes:
        1. What they did well
        2. Areas for improvement  
        3. Specific suggestions to make the answer stronger
        4. A rating out of 10

        Keep the feedback encouraging but honest, and limit to 150 words.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

@login_required
def ai_page_view(request):
    """Complex AI interview page - redirect to simple interview for now"""
    # For now, redirect to the simple interview since the complex one was causing issues
    return redirect('dashboard:simple_interview')


#==================================================================================================
# @login_required
# def my_sessions(request):
#     sessions = InterviewSession.objects.filter(user=request.user).order_by('-started_at')
#     selected_session = None
#     questions = []

#     session_id = request.GET.get("session_id")
#     if session_id:
#         try:
#             selected_session = InterviewSession.objects.get(id=session_id, user=request.user)
#             questions = SessionQuestion.objects.filter(session=selected_session).order_by('question_number')
#         except InterviewSession.DoesNotExist:
#             selected_session = None

#     return render(request, "dashboard/my_sessions.html", {
#         "sessions": sessions,
#         "selected_session": selected_session,
#         "questions": questions
#     })

