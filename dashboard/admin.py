
from django.contrib import admin
from .models import InterviewDetails, PresentationPractice, CommunicationPractice, CustomQuestionSet, CustomQuestion , UserProfile , InterviewSession, SessionQuestion

# --- Simple models registration --- #
admin.site.register(InterviewDetails)
admin.site.register(PresentationPractice)
admin.site.register(CommunicationPractice)
admin.site.register(UserProfile)




# --- Inline setup for CustomQuestion --- #
class CustomQuestionInline(admin.TabularInline):
    model = CustomQuestion
    extra = 0  # Initially extra empty forms = 0
    # optional: readonly_fields = ('question_text',)  # agar read-only karna ho

# --- Admin for CustomQuestionSet --- #
@admin.register(CustomQuestionSet)
class CustomQuestionSetAdmin(admin.ModelAdmin):
    inlines = [CustomQuestionInline]  # Inline show kare questions
    list_display = ('topic_name', 'user', 'num_questions', 'time_per_question')
    list_filter = ('user',)
    search_fields = ('topic_name', 'user__username')

# --- Admin for CustomQuestion (optional) --- #
@admin.register(CustomQuestion)
class CustomQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_set')
    list_filter = ('question_set',)
    search_fields = ('question_text',)







# #==============================================================================
# # Inline view so you can see questions under each session in admin panel
# class SessionQuestionInline(admin.TabularInline):
#     model = SessionQuestion
#     extra = 0

# @admin.register(InterviewSession)
# class InterviewSessionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'status', 'started_at', 'ended_at')
#     list_filter = ('status', 'started_at')
#     search_fields = ('user__username',)
#     inlines = [SessionQuestionInline]

# @admin.register(SessionQuestion)
# class SessionQuestionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'session', 'question_number', 'question_text', 'user_answer')
#     search_fields = ('question_text', 'user_answer')
