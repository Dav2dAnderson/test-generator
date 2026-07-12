from django.contrib import admin

from .models import Question, Test, Passage, Choice
# Register your models here.


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'passage']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test']