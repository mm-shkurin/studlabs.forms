from rest_framework import serializers
from .models import Form, Question, Option, Response, Answer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']
        read_only_fields = ['id']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'type', 'required', 'options']
        read_only_fields = ['id']

class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'owner', 'questions']
        read_only_fields = ['id', 'owner']

class FormCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    
    class Meta:
        model = Form
        fields = ['title', 'description', 'questions']
        extra_kwargs = {
            'owner': {'read_only': True}
        }
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        form = Form.objects.create(owner=self.context['request'].user, **validated_data)
        
        for question_data in questions_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(form=form, **question_data)
            
            for option_data in options_data:
                Option.objects.create(question=question, **option_data)
        
        return form

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'text', 'select']

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    
    class Meta:
        model = Response
        fields = ['id', 'form', 'respondent', 'answers']
        read_only_fields = ['id', 'respondent']
    
    def validate(self, data):
        """
        Дополнительная валидация ответов
        """
        form = data.get('form')
        answers = data.get('answers', [])
        
        required_questions = form.questions.filter(required=True)
        answered_questions = {a['question'].id for a in answers if 'question' in a}
        
        missing_questions = required_questions.exclude(id__in=answered_questions)
        if missing_questions.exists():
            raise serializers.ValidationError(
                f"Не заполнены обязательные вопросы: {', '.join(str(q.id) for q in missing_questions)}"
            )
        
        return data
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        request = self.context.get('request')
        
        response = Response.objects.create(
            form=validated_data['form'],
            respondent=request.user if request and request.user.is_authenticated else None
        )
        
        for answer_data in answers_data:
            selected_options = answer_data.pop('select', [])
            answer = Answer.objects.create(response=response, **answer_data)
            
            if selected_options:
                answer.select.set(selected_options)
        
        return response

class FormStatsSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = ['id', 'title', 'stats']
    
    def get_stats(self, obj):
        stats = []
        total_responses = obj.responses.count()
        
        for question in obj.questions.all():
            if question.type in ['radio', 'checkbox']:
                question_stats = {
                    'question_id': question.id,
                    'question_text': question.text,
                    'type': question.type,
                    'options': []
                }
                
                for option in question.options.all():
                    count = Answer.objects.filter(
                        question=question,
                        select=option.id,
                        response__form=obj
                    ).count()
                    
                    percentage = round((count / total_responses) * 100, 1) if total_responses > 0 else 0
                    
                    question_stats['options'].append({
                        'option_id': option.id,
                        'option_text': option.text,
                        'count': count,
                        'percentage': percentage
                    })
                
                stats.append(question_stats)
        
        return stats