from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название фильма")
    director = models.CharField(max_length=100, verbose_name="Режиссер")
    year = models.IntegerField(verbose_name="Год выпуска")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    duration = models.IntegerField(verbose_name="Продолжительность (мин)")
    rating = models.FloatField(verbose_name="Рейтинг")
    description = models.TextField(verbose_name="Описание")
    cast = models.TextField(verbose_name="Актерский состав")
    image_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на постер")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.year})"

    def to_dict(self):
        return {
            'title': self.title,
            'director': self.director,
            'year': self.year,
            'genre': self.genre,
            'duration': self.duration,
            'rating': self.rating,
            'description': self.description,
            'cast': self.cast,
            'image_url': self.image_url
        }