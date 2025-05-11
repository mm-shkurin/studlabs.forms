from django.contrib import admin
from .models import Form, Question, Option, Response, Answer

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    fields = ('text',)
    readonly_fields = ('id',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('text', 'type', 'required')
    readonly_fields = ('id',)
    inlines = [OptionInline]

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('question', 'text', 'selected_options_display')
    readonly_fields = ('question', 'selected_options_display')
    
    def selected_options_display(self, obj):
        return ", ".join([option.text for option in obj.select.all()])
    selected_options_display.short_description = 'Выбранные варианты'

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'question_count', 'response_count')
    list_select_related = ('owner',)
    inlines = [QuestionInline]
    search_fields = ('title', 'owner__username')
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Вопросы'
    
    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = 'Ответы'

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'respondent', 'creat_time')
    list_select_related = ('form', 'respondent')
    inlines = [AnswerInline]
    search_fields = ('form__title', 'respondent__username')