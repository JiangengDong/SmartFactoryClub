import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.forms import BaseForm
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import cache_control, patch_cache_control
from .models import Questionnaire, AnswerSheet, TextAnswer, FileAnswer
from .forms import DynamicFormMetaClass


def indexView(request):
    # get the questionnaire
    t = timezone.now()
    queryset = Questionnaire.objects.filter(timePublish__lte=t, deadLine__isnull=True) | \
               Questionnaire.objects.filter(timePublish__lte=t, deadLine__gte=t)
    questionnaire = get_object_or_404(queryset, status=True)
    SurveyForm = DynamicFormMetaClass('SurveyForm', (BaseForm,), {'instance': questionnaire})
    # GET method
    if request.method == 'GET':
        response = render(request, 'enroll/form.html',
                          context={'form': SurveyForm(),
                                   'resources': questionnaire.resource_set,
                                   'title': questionnaire.name})
    # POST method
    elif request.method == 'POST':
        email = request.POST.get('candidateEmail')
        password = hash(request.POST.get('token'))
        form = SurveyForm(request.POST, request.FILES)
        if not form.is_valid():
            response = render(request, 'enroll/form.html',
                              context={'form': form,
                                       'resources': questionnaire.resource_set,
                                       'title': questionnaire.name,
                                       'verify': {'email': email}})
        else:
            answerSheet, created = AnswerSheet.objects.get_or_create(email=email)
            if answerSheet.password and answerSheet.password != password:
                # wrong password!!!
                helpText = '''密码错误。如果您忘记了密码，请从您的邮箱向<a href="mailto:%s">%s</a>发送主题为“重置密码”的邮件，我们的工作人员会为您手动重置密码。
                              手动重置需要花费一定时间，请耐心等候。''' % (questionnaire.email, questionnaire.email)
                response = render(request, 'enroll/form.html',
                                  context={'form': form,
                                           'resources': questionnaire.resource_set,
                                           'title': questionnaire.name,
                                           'verify': {'email': email, 'helpText': helpText}})

            else:
                # right password
                answerSheet.password = password
                answerSheet.questionnaire = questionnaire
                answerSheet.timeSubmit = timezone.now()
                answerSheet.save()
                for key, value in form.cleaned_data.items():
                    if value is not None:
                        question = questionnaire.question_set.get(id=key.split('_')[-1])
                        if question.type == 4:
                            answer, created = answerSheet.fileanswer_set.get_or_create(answerSheet=answerSheet,
                                                                                       question=question)
                            path = os.path.join(settings.MEDIA_ROOT, answer.answer.name)
                            if not created and os.path.exists(path):
                                os.remove(path)
                            answer.answer = value
                            answer.save()
                        elif question.type in [1, 2, 3]:
                            answer, created = answerSheet.textanswer_set.get_or_create(answerSheet=answerSheet,
                                                                                       question=question)
                            answer.answer = value
                            answer.save()
                response = render(request, 'enroll/check_page.html',
                                  context={'form': form,
                                           'title': questionnaire.name,
                                           'verify': {'email': email}})
    patch_cache_control(response, no_cache=True, no_store=True)
    return response
