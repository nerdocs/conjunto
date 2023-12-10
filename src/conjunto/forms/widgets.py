from django import forms


class DatePickerInput(forms.widgets.DateInput):
    """A DateInput that uses a date picker.

    It adds Litepicker.js for that input field.
    Additionally, you can specify another field with "end_field_name"
    that is used for date ranges by Litepicker then.
    """

    class Media:
        js = ("conjunto/js/datepicker.js",)

    template_name = "conjunto/widgets/datepicker_input.html"

    def __init__(self, attrs=None, end_field_name=None):
        if attrs is None:
            attrs = {}
        attrs.update({"autocomplete": "off"})
        if end_field_name:
            attrs.update({"data-end-field": end_field_name})
        super().__init__(attrs)
