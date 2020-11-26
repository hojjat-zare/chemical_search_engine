from django import forms


class SearchForm(forms.Form):
    searched_phrase = forms.CharField(label='what do you want to search', max_length=300)
