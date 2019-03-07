import os
import shutil

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


class CommonInfo(models.Model):
    # not editable (used to record)
    timeModify = models.DateTimeField(default=timezone.now,
                                      editable=False,
                                      verbose_name='修改时间')
    userModify = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   editable=False,
                                   related_name='%(app_label)s_%(class)s_modified',
                                   verbose_name='修改者')
    timeCreate = models.DateTimeField(default=timezone.now,
                                      editable=False,
                                      verbose_name='创建时间')
    userCreate = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   editable=False,
                                   related_name='%(app_label)s_%(class)s_created',
                                   verbose_name='创建者')

    class Meta:
        abstract = True
        db_table = '%(app_label)s_%(class)s'


class Questionnaire(CommonInfo):
    # editable
    name = models.CharField(max_length=25,
                            blank=False,
                            verbose_name='名称',
                            help_text='不允许与其他条目重复。')
    status = models.BooleanField(default=False,
                                 verbose_name='发布状态')
    timePublish = models.DateTimeField(null=True,
                                       verbose_name='发布时间')
    deadLine = models.DateTimeField(null=True,
                                    verbose_name='截止时间')
    email = models.EmailField(verbose_name='客服邮箱')

    def numQuestion(self):
        return self.question_set.count()

    numQuestion.short_description = '问题数量'

    def numAnswerSheet(self):
        return self.answersheet_set.count()

    numAnswerSheet.short_description = '答卷数量'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        path = os.path.join(settings.MEDIA_ROOT,
                            'enroll',
                            '%d' % self.id)
        if os.path.exists(path):
            shutil.rmtree(path)
        super().delete(using, keep_parents)

    class Meta:
        verbose_name = '问卷'
        verbose_name_plural = '问卷'


def resource_redirect(instance, name):
    if instance.name:
        name = instance.name + '.' + name.split('.')[-1]
    else:
        _, instance.name = os.path.split(name)
    return os.path.join('enroll',
                        '%d' % instance.questionnaire_id,
                        'resources',
                        name)


class Resource(CommonInfo):
    name = models.CharField(max_length=256,
                            blank=True,
                            verbose_name='名称')
    file = models.FileField(upload_to=resource_redirect,
                            verbose_name='文件')
    questionnaire = models.ForeignKey(to=Questionnaire,
                                      on_delete=models.CASCADE,
                                      verbose_name='问卷')
    url = models.CharField(max_length=64,
                           blank=True,
                           editable=False,
                           verbose_name='访问路径')

    def __str__(self):
        return str(self.questionnaire) + '/' + self.name

    def get_absolute_url(self):
        return self.url

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.url = self.file.url
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        if os.path.exists(path):
            os.remove(path)
        return super().delete(using, keep_parents)

    class Meta:
        verbose_name_plural = '资源'
        verbose_name = '资源'


class Question(CommonInfo):
    questionnaire = models.ForeignKey(to=Questionnaire,
                                      on_delete=models.CASCADE,
                                      verbose_name='问卷')
    order = models.IntegerField(default=3,
                                verbose_name='题号')
    type = models.IntegerField(choices=[[1, '单选题'],
                                        [2, '多选题'],
                                        [3, '填空题'],
                                        [4, '文件题']],
                               default=1,
                               verbose_name='题型')
    require = models.BooleanField(default=False,
                                  verbose_name='必答')
    description = models.TextField(blank=True,
                                   verbose_name='题目')

    def __str__(self):
        return '问题 %d' % self.order

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = '问题'
        ordering = ['order']


class Choice(models.Model):
    question = models.ForeignKey(to=Question,
                                 on_delete=models.CASCADE,
                                 verbose_name='题目')
    order = models.IntegerField(default=1,
                                verbose_name='选项')
    description = models.CharField(max_length=256,
                                   verbose_name='选项内容')

    def __str__(self):
        return '选项%d. %s' % (self.order, self.description)

    class Meta:
        verbose_name = '选项'
        verbose_name_plural = '选项'
        ordering = ['order']


class AnswerSheet(models.Model):
    timeSubmit = models.DateTimeField(default=timezone.now,
                                      verbose_name='提交时间')
    email = models.EmailField(verbose_name='邮箱')
    password = models.IntegerField(null=True,
                                   editable=False,
                                   verbose_name='密码')
    questionnaire = models.ForeignKey(to=Questionnaire,
                                      on_delete=models.CASCADE,
                                      null=True,
                                      verbose_name='问卷')

    def __str__(self):
        return '%s %s答卷' % (self.questionnaire.name, self.email)

    def delete(self, using=None, keep_parents=False):
        path = os.path.join(settings.MEDIA_ROOT,
                            'enroll',
                            '%d' % self.questionnaire_id,
                            'answersheets',
                            self.email)
        if os.path.exists(path):
            shutil.rmtree(path)
        super().delete(using, keep_parents)

    class Meta:
        verbose_name = '答卷'
        verbose_name_plural = '答卷'


class TextAnswer(models.Model):
    answerSheet = models.ForeignKey(to=AnswerSheet,
                                    on_delete=models.CASCADE,
                                    verbose_name='答卷')
    question = models.ForeignKey(to=Question,
                                 on_delete=models.CASCADE,
                                 verbose_name='问题')
    answer = models.TextField(verbose_name='答案')

    def __str__(self):
        return "问题%d答案" % self.question.order

    class Meta:
        verbose_name = '答案'
        verbose_name_plural = '答案'


def answer_redirect(instance, filename):
    """
    :type instance: FileAnswer
    :type filename: str
    """
    return os.path.join('enroll',
                        '%d' % instance.answerSheet.questionnaire_id,
                        'answersheets',
                        instance.answerSheet.email,
                        '%d' % instance.question.order,
                        filename)


class FileAnswer(models.Model):
    answerSheet = models.ForeignKey(to=AnswerSheet,
                                    on_delete=models.CASCADE,
                                    verbose_name='答卷')
    question = models.ForeignKey(to=Question,
                                 on_delete=models.CASCADE,
                                 verbose_name='问题')
    answer = models.FileField(upload_to=answer_redirect,
                              verbose_name='附件')

    def __str__(self):
        return "问题%d答案" % self.question.order

    class Meta:
        verbose_name = '附件'
        verbose_name_plural = '附件'
