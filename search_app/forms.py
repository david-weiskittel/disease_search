from django import forms

# Create a basic form class with a field for searching
class SymptomSearchForm(forms.Form):
    search = forms.CharField(max_length=300, label='')
