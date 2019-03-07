from django.forms import Form, BaseForm
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms import fields, widgets

from .models import Questionnaire, Question
from .widgets import CheckboxSelectMultiple, RadioSelect, TextInput, FileInput


def chooseField(question):
    """
    Choose a proper form field for the question.

    :param question: question to be allocated a field
    :type question: Question
    :return: the corresponding field
    :rtype: fields.Field
    """
    type = question.type
    if type == 1:
        choices = question.choice_set.values_list('order', 'description')
        return fields.ChoiceField(choices=choices,
                                  widget=RadioSelect(),
                                  label=question.description,
                                  label_suffix='',
                                  required=question.require)
    elif type == 2:
        choices = question.choice_set.values_list('order', 'description')
        return fields.MultipleChoiceField(choices=choices,
                                          widget=CheckboxSelectMultiple(),
                                          label=question.description,
                                          label_suffix='',
                                          required=question.require)
    elif type == 3:
        return fields.CharField(widget=TextInput(),
                                label=question.description,
                                label_suffix='',
                                required=question.require)
    elif type == 4:
        return fields.FileField(widget=FileInput(),
                                label=question.description,
                                label_suffix='',
                                required=question.require)
    else:
        return None


class DynamicFormMetaClass(DeclarativeFieldsMetaclass):
    def __new__(cls, name, bases, attrs):
        """
        Create a new form class according to the 'model' field in attrs.

        :param name: name of the new class
        :type name: str
        :param bases: parents of the new class
        :type bases: tuple
        :param attrs: fields and methods of the new class
        :type attrs: dict
        :return: a new class
        """
        if 'instance' in attrs:
            instance = attrs.pop('instance')  # type: Questionnaire
            attrs['field_order'] = ['question_%d' % id for id, order in
                                    sorted(instance.question_set.values_list('id', 'order'), key=lambda t: t[1])]
            all_fields = {}
            for question in instance.question_set.all():  # type: Question
                fieldName = 'question_%d' % question.id
                field = chooseField(question)
                if field:
                    all_fields[fieldName] = field
            attrs.update(all_fields)
        new_class = super().__new__(cls, name, bases, attrs)
        return new_class
