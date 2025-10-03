from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InterviewDetails , PresentationPractice , CommunicationPractice

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email' , 'password1' , 'password2']


class InterviewDetailsForm(forms.ModelForm):
    class Meta:
        model = InterviewDetails
        fields = [
            "resume_file", "full_name", "email", "phone",
            "education", "branch", "skills", "experience", "about_you",
            "role", "domain", "difficulty", "mode",
            "time_per_question", "num_questions",
            "custom_keywords"
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'education': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'branch': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'skills': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'experience': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'about_you': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'role': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'domain': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'difficulty': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'mode': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'time_per_question': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'num_questions': forms.Select(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'custom_keywords': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
            'resume_file': forms.ClearableFileInput(attrs={'class': 'w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-[#854F6C] glow'}),
        }

#===============================================================================================================================================================================



class PresentationForm(forms.ModelForm):
    class Meta:
        model = PresentationPractice
        fields = ["ppt_file", "topic_name", "description", "audience_type", "time_per_question", "num_questions", "custom_keywords"]


#==================================================================================================================================================================================


class CommunicationPracticeForm(forms.ModelForm):
    class Meta:
        model = CommunicationPractice
        fields = [
            "full_name",
            "age",
            "email",
            "language",
            "language_proficiency",
            "mode",
            "reason",
            "custom_reason",
            "time_per_round",
            "num_rounds",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "w-full p-3 rounded-xl bg-[#2B124C] border border-[#854F6C]",
                "placeholder": "Enter your full name"
            }),
            "age": forms.NumberInput(attrs={
                "class": "w-full p-3 rounded-xl bg-[#2B124C] border border-[#854F6C]",
                "placeholder": "Enter your age (optional)"
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full p-3 rounded-xl bg-[#2B124C] border border-[#854F6C]",
                "placeholder": "Enter your email (optional)"
            }),
            "custom_reason": forms.TextInput(attrs={
                "class": "w-full p-3 rounded-xl bg-[#2B124C] border border-[#854F6C]",
                "placeholder": "If 'Other', write your reason"
            }),
            "time_per_round": forms.NumberInput(attrs={
                "class": "w-full p-3 rounded-xl bg-[#2B124C] border border-[#854F6C]",
                "min": "60",
                "max": "180",
                "value": 60
            }),
        }

    def clean_custom_reason(self):
        reason = self.cleaned_data.get("reason")
        custom_reason = self.cleaned_data.get("custom_reason")

        if reason == "custom" and not custom_reason:
            raise forms.ValidationError("Please provide your custom reason")
        return custom_reason




