from django import forms
from apps.spreadsheets.models import Spreadsheet, Cell, Structure


class SpreadsheetForm(forms.ModelForm):
    class Meta:
        model = Spreadsheet
        exclude = ()


class StructureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        qs = Cell.objects.filter(spreadsheet=self.instance.spreadsheet, row__lte=20).exclude(content='')

        self.fields['email'].queryset = qs
        self.fields['first_name'].queryset = qs
        self.fields['last_name'].queryset = qs
        self.fields['company_name'].queryset = qs
        self.fields['snippet_1'].queryset = qs
        self.fields['snippet_2'].queryset = qs
        self.fields['snippet_3'].queryset = qs

    class Meta:
        model = Structure
        exclude = ()
