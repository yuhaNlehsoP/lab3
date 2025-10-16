from django import forms

class MovieForm(forms.Form):
    """Форма для добавления/редактирования фильма"""
    title = forms.CharField(
        max_length=200, 
        label="Название фильма",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    director = forms.CharField(
        max_length=100,
        label="Режиссер",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        label="Год выпуска",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1895,
        max_value=2030
    )
    genre = forms.CharField(
        max_length=100,
        label="Жанр", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    duration = forms.IntegerField(
        label="Продолжительность (мин)",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1
    )
    rating = forms.FloatField(
        label="Рейтинг",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        min_value=0,
        max_value=10
    )
    description = forms.CharField(
        label="Описание",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    cast = forms.CharField(
        label="Актерский состав",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    image_url = forms.URLField(
        label="Ссылка на постер",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

class JSONUploadForm(forms.Form):
    json_file = forms.FileField(
        label='Выберите JSON файл',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.json'})
    )