import json
import os

def validate_movie_json(file_path):
    """
    Валидация JSON файла с данными о фильмах
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Проверяем, является ли data списком
        if not isinstance(data, list):
            return False, "JSON должен содержать массив объектов"
        
        if len(data) == 0:
            return False, "JSON файл пуст"
        
        required_fields = ['title', 'director', 'year', 'genre', 'duration', 'rating']
        
        for i, movie in enumerate(data):
            # Проверяем, что каждый элемент - словарь
            if not isinstance(movie, dict):
                return False, f"Элемент {i} должен быть объектом"
            
            # Проверяем наличие обязательных полей
            for field in required_fields:
                if field not in movie:
                    return False, f"Отсутствует обязательное поле: '{field}' в фильме {i+1}"
            
            # Проверяем типы данных
            if not isinstance(movie['title'], str) or not movie['title'].strip():
                return False, f"Название фильма {i+1} должно быть непустой строкой"
            
            if not isinstance(movie['director'], str) or not movie['director'].strip():
                return False, f"Режиссер фильма {i+1} должен быть непустой строкой"
            
            if not isinstance(movie['year'], int) or movie['year'] < 1895 or movie['year'] > 2030:
                return False, f"Год фильма {i+1} должен быть целым числом между 1895 и 2030"
            
            if not isinstance(movie['genre'], str) or not movie['genre'].strip():
                return False, f"Жанр фильма {i+1} должен быть непустой строкой"
            
            if not isinstance(movie['duration'], int) or movie['duration'] <= 0:
                return False, f"Продолжительность фильма {i+1} должна быть положительным целым числом"
            
            if not isinstance(movie['rating'], (int, float)) or movie['rating'] < 0 or movie['rating'] > 10:
                return False, f"Рейтинг фильма {i+1} должен быть числом между 0 и 10"
        
        return True, "Файл валиден"
    
    except json.JSONDecodeError as e:
        return False, f"Невалидный JSON формат: {str(e)}"
    except Exception as e:
        return False, f"Ошибка при чтении файла: {str(e)}"