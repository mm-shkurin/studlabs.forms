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
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'questions']
        extra_kwargs = {
            'owner': {'read_only': True},
            'id': {'read_only': True}
        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if 'questions' in validated_data:
            questions_data = validated_data.pop('questions')
            self.update_questions(instance, questions_data)

        return instance

    def update_questions(self, form, questions_data):
        current_questions = {q.id: q for q in form.questions.all()}
        new_ids = []

        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id and question_id in current_questions:
                question = current_questions[question_id]
                question.text = question_data.get('text', question.text)
                question.type = question_data.get('type', question.type)
                question.required = question_data.get('required', question.required)
                question.save()
                self.update_options(question, question_data.get('options', []))
                new_ids.append(question_id)
            else:
                new_q = self.create_question(form, question_data)
                new_ids.append(new_q.id)

        for q in form.questions.exclude(id__in=new_ids):
            q.delete()

    def update_options(self, question, options_data):
        current_options = {o.id: o for o in question.options.all()}
        new_ids = []

        for option_data in options_data:
            option_id = option_data.get('id')
            if option_id and option_id in current_options:
                option = current_options[option_id]
                option.text = option_data.get('text', option.text)
                option.save()
                new_ids.append(option_id)
            else:
                new_opt = Option.objects.create(question=question, **option_data)
                new_ids.append(new_opt.id)

        for o in question.options.exclude(id__in=new_ids):
            o.delete()

    def create_question(self, form, question_data):
        options_data = question_data.pop('options', [])
        question = Question.objects.create(form=form, **question_data)
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        return question 

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
        form = Form.objects.create(
            owner=self.context['request'].user,
            **validated_data
        )
        
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