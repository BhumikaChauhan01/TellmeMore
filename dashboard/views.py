import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dashboard.models import InterviewDetails, PresentationPractice, CommunicationPractice, CustomQuestionSet, CustomQuestion, UserProfile
import google.generativeai as genai

# ---------------- Dashboard Pages ---------------- #

@login_required
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")

@login_required
def my_sessions(request):
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

        if request.FILES.get("resume_file"):
            interview_instance.resume_file = request.FILES["resume_file"]

        interview_instance.save()
        return redirect("dashboard:ai_page")

    return render(request, "dashboard/interview_requirements.html")


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

#=======================================================================================================================



def ai_page_view(request):
    # Get user's interview details for context
    interview_details = None
    try:
        interview_details = InterviewDetails.objects.get(user=request.user)
    except InterviewDetails.DoesNotExist:
        pass
    
    return render(request, 'dashboard/ai_page.html', {
        'interview_details': interview_details
    })

# Configure Gemini API
try:
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY', 'your-api-key-here'))
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    model = None
    print(f"Gemini API configuration failed: {e}")

@require_http_methods(["POST"])
@login_required
def generate_question(request):
    try:
        data = json.loads(request.body)
        question_number = data.get('question_number', 1)
        context = data.get('context', {})
        previous_answers = data.get('previous_answers', [])
        
        if model:
            # Create detailed prompt for Gemini
            prompt = f"""
            You are an experienced interviewer conducting a {context.get('mode', 'technical')} interview for a {context.get('position', 'Software Developer')} position.
            
            Candidate Profile:
            - Position: {context.get('position', 'Software Developer')}
            - Skills: {context.get('skills', 'General')}
            - Difficulty Level: {context.get('difficulty', 'medium')}
            - Interview Type: {context.get('mode', 'technical')}
            
            Question Number: {question_number}
            
            {'Previous answers from candidate: ' + str(previous_answers) if previous_answers else 'This is the first question.'}
            
            Generate a thoughtful, relevant interview question that:
            1. Matches the {context.get('difficulty', 'medium')} difficulty level
            2. Is appropriate for the {context.get('mode', 'technical')} interview type
            3. Tests skills related to: {context.get('skills', 'problem-solving')}
            4. Builds naturally on previous responses if any
            5. Is professional and engaging
            
            Provide only the question text, no additional formatting or explanation.
            """
            
            response = model.generate_content(prompt)
            question = response.text.strip()
            
            return JsonResponse({
                'success': True,
                'question': question
            })
        else:
            # Fallback questions when API is not available
            fallback_questions = {
                'technical': [
                    f"Tell me about your experience with {context.get('skills', 'programming').split(',')[0].strip()}.",
                    "Walk me through your approach to debugging a complex issue in production.",
                    "Describe a time when you had to optimize code for performance. What was your process?",
                    "How do you ensure code quality in your projects?",
                    "Explain a challenging technical decision you made and its impact."
                ],
                'hr': [
                    "Tell me about yourself and why you're interested in this position.",
                    "Describe a time when you faced a significant challenge at work. How did you handle it?",
                    "Where do you see yourself in 5 years?",
                    "How do you handle stress and pressure in the workplace?",
                    "What motivates you to do your best work?"
                ],
                'gd': [
                    f"What are your thoughts on the future of {context.get('skills', 'technology').split(',')[0].strip()}?",
                    "How should companies approach remote work policies?",
                    "What role should AI play in the future of work?",
                    "Discuss the importance of work-life balance in today's workplace.",
                    "How can organizations better support diversity and inclusion?"
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
def evaluate_answer(request):
    try:
        data = json.loads(request.body)
        answer = data.get('answer', '')
        question_number = data.get('question_number', 1)
        context = data.get('context', {})
        
        if model and answer:
            prompt = f"""
            You are an experienced interviewer evaluating a candidate's response.
            
            Interview Context:
            - Position: {context.get('position', 'Software Developer')}
            - Skills: {context.get('skills', 'General')}
            - Difficulty: {context.get('difficulty', 'medium')}
            - Type: {context.get('mode', 'technical')}
            
            Question Number: {question_number}
            Candidate's Answer: "{answer}"
            
            Provide constructive feedback that:
            1. Acknowledges strengths in the response
            2. Suggests areas for improvement (if any)
            3. Is encouraging and professional
            4. Helps guide the candidate toward better responses
            5. Is brief but insightful (2-3 sentences max)
            
            Provide only the feedback text, no additional formatting.
            """
            
            response = model.generate_content(prompt)
            feedback = response.text.strip()
            
            return JsonResponse({
                'success': True,
                'feedback': feedback
            })
        else:
            return JsonResponse({
                'success': True,
                'feedback': "Thank you for your response. Let's continue to the next question."
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })