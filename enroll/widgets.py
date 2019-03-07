from django.forms import widgets


class RadioSelect(widgets.ChoiceWidget):
    input_type = 'radio'
    template_name = 'enroll/widgets/radio.html'


class CheckboxSelectMultiple(widgets.ChoiceWidget):
    allow_multiple_selected = True
    input_type = 'checkbox'
    template_name = 'enroll/widgets/checkbox_select.html'

    def use_required_attribute(self, initial):
        # Don't use the 'required' attribute because browser validation would
        # require all checkboxes to be checked instead of at least one.
        return False

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False

    def id_for_label(self, id_, index=None):
        """"
        Don't include for="field_0" in <label> because clicking such a label
        would toggle the first checkbox.
        """
        if index is None:
            return ''
        return super().id_for_label(id_, index)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context


class TextInput(widgets.Input):
    input_type = 'text'
    template_name = 'enroll/widgets/text.html'


class FileInput(widgets.Input):
    input_type = 'file'
    needs_multipart_form = True
    template_name = 'enroll/widgets/file.html'

    def format_value(self, value):
        """File input never renders a value."""
        return

    def value_from_datadict(self, data, files, name):
        "File widgets take data from FILES, not POST"
        return files.get(name)

    def value_omitted_from_data(self, data, files, name):
        return name not in files