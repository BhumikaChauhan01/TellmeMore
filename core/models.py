
from django.db import models
from django.contrib.auth.models import User

class InterviewDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Resume (optional)
    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)

    # Basic Info (Form compulsory h)
    full_name = models.CharField(max_length=100)  
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)

    education = models.CharField(max_length=200)  # Example: "B.Tech Computer Science"
    branch = models.CharField(max_length=100, blank=True, null=True)  
    skills = models.TextField(help_text="List your key skills, separated by commas")  
    experience = models.TextField(blank=True, null=True, help_text="Mention work experience or write Fresher")  

    # Extra professional touch
    about_you = models.TextField(
        help_text="Briefly describe yourself, your interests and goals",
        blank=True,
        null=True
    )

    # Interview Info
    role = models.CharField(max_length=100, blank=True, null=True)  # e.g. Software Developer
    domain = models.CharField(max_length=100, blank=True, null=True)  # e.g. IT, Finance

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')

    MODE_CHOICES = [
        ('hr', 'HR'),
        ('technical', 'Technical'),
        ('gd', 'Group Discussion'),
    ]
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, blank=True, null=True)

    # Question Parameters
    time_per_question = models.IntegerField(default=60, help_text="Time in seconds (default 60s, max 180s)")  
    num_questions = models.IntegerField(choices=[(5, '5'), (10, '10'), (20, '20')], default=5)

   

    custom_keywords = models.TextField(blank=True, null=True, help_text="Optional: Keywords for AI (e.g. DSA, DBMS, Communication)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview - {self.user.username} ({self.role if self.role else 'General'})"
    

    #============================================================================================================



class PresentationPractice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # PPT Upload (optional)
    ppt_file = models.FileField(upload_to="presentations/", blank=True, null=True)

    # Basic Info
    topic_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, help_text="Write about your topic")

    # Audience
    AUDIENCE_CHOICES = [
        ('employees', 'Employees'),
        ('students', 'Students'),
        ('teachers', 'Teachers'),
        ('general', 'General Audience'),
    ]
    audience_type = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='general')

    # Question Settings
    time_per_question = models.IntegerField(
        default=60,
        help_text="Time in seconds (default 60s, max 180s)"
    )
    num_questions = models.IntegerField(
        choices=[(5, '5'), (10, '10'), (15, '15'), (20, '20')],
        default=5
    )

    # Extra professional touch
    custom_keywords = models.TextField(
        blank=True,
        null=True,
        help_text="Optional: Keywords for AI (e.g. Confidence, Body Language, Communication)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Presentation - {self.user.username} ({self.topic_name})"
    
#==================================================================================



class CommunicationPractice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Basic Info
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Language selection
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('other', 'Other'),
    ]
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='english')

    # Language proficiency
    PROFICIENCY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('pro', 'Proficient'),
    ]
    language_proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='basic')

    # Mode / Level of roleplay
    MODE_CHOICES = [
        ('basic_intro', 'Basic Intro (Self Introduction, Simple Conversation)'),
        ('intermediate', 'Intermediate (Group Discussions, Peer Conversations)'),
        ('pro', 'Pro Level (Professional Scenario Roleplay)'),
    ]
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='basic_intro')

    # Reason for learning
    REASON_CHOICES = [
        ('office', 'Office / Workplace Communication'),
        ('travel', 'Travel / Tour Communication'),
        ('students', 'Classroom / Student Interaction'),
        ('presentation', 'Presentations / Public Speaking'),
        ('personal', 'Personal Growth / Confidence'),
        ('custom', 'Other (User defined)'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default='personal')
    custom_reason = models.CharField(max_length=200, blank=True, null=True, help_text="If you select 'Other', write your reason here")

    # Roleplay settings
    time_per_round = models.IntegerField(default=60, help_text="Time in seconds (default 60s, max 180s)")
    num_rounds = models.IntegerField(choices=[(3, '3'), (4, '4'), (5, '5')], default=3)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Communication Practice - {self.full_name} ({self.language})"
    
#===========================================================================================

class CustomQuestionSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Basic Info
    topic_name = models.CharField(max_length=200)
    short_description = models.TextField(blank=True, null=True, help_text="Optional short description")

    # Settings
    num_questions = models.IntegerField(choices=[(1, '1'), (5, '5'), (10, '10'), (15, '15'), (20, '20')], default=5)
    time_per_question = models.IntegerField(default=60, help_text="Time per question in seconds (default 60s, max 180s)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic_name} ({self.user.username})"

class CustomQuestion(models.Model):
    question_set = models.ForeignKey(CustomQuestionSet, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.user.username


















