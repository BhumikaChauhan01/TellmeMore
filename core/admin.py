
from django.contrib import admin
from core.models import InterviewDetails, PresentationPractice, CommunicationPractice, CustomQuestionSet, CustomQuestion , UserProfile

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
