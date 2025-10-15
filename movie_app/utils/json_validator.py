import json

def validate_movie_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if not isinstance(data, list):
            return False, "JSON должен содержать массив объектов"
        
        required_fields = ['title', 'director', 'year', 'genre', 'duration', 'rating']
        
        for movie in data:
            for field in required_fields:
                if field not in movie:
                    return False, f"Отсутствует поле: {field}"
        
        return True, "Файл валиден"
    
    except json.JSONDecodeError:
        return False, "Невалидный JSON формат"