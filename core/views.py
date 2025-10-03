from django.shortcuts import render ,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import InterviewDetails , PresentationPractice, CommunicationPractice ,  CustomQuestionSet, CustomQuestion
from .models import UserProfile


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")  # Home pe redirect after register
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

def home_view(request):
    return render(request, "home.html")

def about_view(request):
    return render(request, "about.html")

def how_to_view(request):
    return render(request, "how_to.html")


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, "dashboard.html")

@login_required
def profile_view(request):
    return render(request, "profile.html")

@login_required
def category_view(request):
    return render(request, "category.html")

@login_required
def interview_requirements_view(request):
    """
    Manual form handling view for InterviewDetails.
    Saves new entry or updates existing entry for logged-in user.
    """
    try:
        # Agar user ne pehle se form fill kiya ho to update karenge
        interview = InterviewDetails.objects.get(user=request.user)
    except InterviewDetails.DoesNotExist:
        interview = None

    if request.method == "POST":
        # Get or create InterviewDetails instance
        if interview:
            interview_instance = interview
        else:
            interview_instance = InterviewDetails(user=request.user)

        # Assign all form fields
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

        # Handle file upload
        if request.FILES.get("resume_file"):
            interview_instance.resume_file = request.FILES["resume_file"]

        # Save to DB
        interview_instance.save()

        return redirect("dashboard")  # Success ke baad dashboard

    return render(request, "interview_requirements.html")



@login_required
def presentation_requirements_view(request):
    if request.method == "POST":
        topic = request.POST.get("topic_name")
        desc = request.POST.get("description")
        audience = request.POST.get("audience_type")
        ppt = request.FILES.get("ppt_file")
        time = request.POST.get("time_per_question", 60)   # default 60s
        num_qs = request.POST.get("num_questions", 5)      # default 5
        keywords = request.POST.get("custom_keywords")

        # Save data
        PresentationPractice.objects.create(
            user=request.user,
            topic_name=topic,
            description=desc,
            audience_type=audience,
            ppt_file=ppt,
            time_per_question=time,
            num_questions=num_qs,
            custom_keywords=keywords
        )

        # Filhal redirect to dashboard (tu later change kar sakti hai)
        return redirect("dashboard")  

    return render(request, "presentation_requirements.html")



@login_required
def communication_requirements_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        age = request.POST.get("age")
        email = request.POST.get("email")
        language = request.POST.get("language", "english")
        language_proficiency = request.POST.get("language_proficiency", "basic")
        mode = request.POST.get("mode", "basic_intro")
        reason = request.POST.get("reason", "personal")
        custom_reason = request.POST.get("custom_reason")
        time_per_round = int(request.POST.get("time_per_round", 60))
        num_rounds = int(request.POST.get("num_rounds", 3))


        # Save to DB
        CommunicationPractice.objects.create(
            user=request.user,
            full_name=full_name,
            age=age if age else None,
            email=email if email else None,
            language=language,
            language_proficiency=language_proficiency,
            mode=mode,
            reason=reason,
            custom_reason=custom_reason,
            time_per_round=time_per_round,
            num_rounds=num_rounds
        )

        # Redirect after submission (filhal dashboard)
        return redirect("dashboard")

    return render(request, "communication_requirements.html")


@login_required
def question_requirements_view(request):
    if request.method == "POST":
        topic_name = request.POST.get("topic_name")
        short_description = request.POST.get("short_description")
        num_questions = int(request.POST.get("num_questions", 5))
        time_per_question = int(request.POST.get("time_per_question", 60))

        # Save the question set
        question_set = CustomQuestionSet.objects.create(
            user=request.user,
            topic_name=topic_name,
            short_description=short_description,
            num_questions=num_questions,
            time_per_question=time_per_question
        )

        # Loop through all questions from POST
        questions = []
        for key, value in request.POST.items():
            if key.startswith("question_") and value.strip():
                questions.append(CustomQuestion(question_set=question_set, question_text=value.strip()))

        # Bulk create all questions
        CustomQuestion.objects.bulk_create(questions)

        return redirect("dashboard")  # redirect to dashboard or uploaded items

    return render(request, "question_requirements.html")



# Profile Page (show details)
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile , "user": request.user})


# Profile Edit Page
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
        return redirect("profile")

    return render(request, "profile_edit.html", {
        "profile": profile,
        "user": request.user  # for username, email, password read-only
    })
