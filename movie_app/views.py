import os
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import Movie
from .forms import MovieForm, JSONUploadForm
from .utils.json_validator import validate_movie_json

def movie_list(request):
    movies = Movie.objects.all()
    
    json_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    json_files = []
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(json_dir, filename)
                # Читаем содержимое файлов для отображения
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                except:
                    file_content = "Ошибка чтения файла"
                
                json_files.append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'content': file_content
                })
    
    context = {
        'movies': movies,
        'json_files': json_files,
        'has_json_files': len(json_files) > 0
    }
    return render(request, 'movie_app/movie_list.html', context)

def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = form.save()
            
            # Сохраняем в JSON файл
            json_data = [movie.to_dict()]
            filename = f"movie_{movie.id}_{uuid.uuid4().hex[:8]}.json"
            json_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
            os.makedirs(json_dir, exist_ok=True)
            
            file_path = os.path.join(json_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            messages.success(request, f'Фильм "{movie.title}" успешно добавлен и сохранен в JSON!')
            return redirect('movie_app:movie_list')
    else:
        form = MovieForm()
    return render(request, 'movie_app/add_movie.html', {'form': form})

def upload_json(request):
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['json_file']
            
            # Безопасное имя файла
            original_name = uploaded_file.name
            safe_name = f"{uuid.uuid4().hex}_{original_name}"
            
            # Сохраняем файл
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'json_files'))
            filename = fs.save(safe_name, uploaded_file)
            file_path = fs.path(filename)
            
            # Валидируем JSON
            is_valid, message = validate_movie_json(file_path)
            
            if not is_valid:
                # Удаляем невалидный файл
                fs.delete(filename)
                messages.error(request, f'Ошибка валидации: {message}')
            else:
                # Импортируем данные из JSON
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        movies_data = json.load(f)
                    
                    imported_count = 0
                    for movie_data in movies_data:
                        # Проверяем, существует ли уже такой фильм
                        if not Movie.objects.filter(
                            title=movie_data['title'],
                            director=movie_data['director'],
                            year=movie_data['year']
                        ).exists():
                            
                            Movie.objects.create(**movie_data)
                            imported_count += 1
                    
                    messages.success(request, f'Успешно импортировано {imported_count} фильмов из {len(movies_data)}')
                
                except Exception as e:
                    messages.error(request, f'Ошибка при импорте данных: {str(e)}')
            
            return redirect('movie_app:movie_list')
    
    else:
        form = JSONUploadForm()
    
    return render(request, 'movie_app/upload_json.html', {'form': form})

def export_all_movies(request):
    """Экспорт всех фильмов в JSON"""
    movies = Movie.objects.all()
    movies_data = [movie.to_dict() for movie in movies]
    
    response = HttpResponse(
        json.dumps(movies_data, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="all_movies.json"'
    return response

def view_json_file(request, filename):
    """Просмотр содержимого конкретного JSON файла"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'json_files', filename)
    
    if not os.path.exists(file_path):
        return HttpResponse("Файл не найден", status=404)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(f"<pre>{content}</pre><br><a href='/'>Назад</a>")
    except Exception as e:
        return HttpResponse(f"Ошибка при чтении файла: {str(e)}", status=500)

def delete_movie(request, movie_id):
    """Удаление фильма по ID"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        # Подтверждение удаления
        movie_title = movie.title
        movie.delete()
        messages.success(request, f'Фильм "{movie_title}" успешно удален!')
        return redirect('movie_app:movie_list')
    
    # GET запрос - показываем страницу подтверждения
    return render(request, 'movie_app/delete_movie.html', {'movie': movie})

# НОВАЯ ФУНКЦИЯ - РЕДАКТИРОВАНИЕ ФИЛЬМА
def edit_movie(request, movie_id):
    """Редактирование фильма по ID"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, f'Фильм "{movie.title}" успешно обновлен!')
            return redirect('movie_app:movie_list')
    else:
        form = MovieForm(instance=movie)
    
    return render(request, 'movie_app/edit_movie.html', {'form': form, 'movie': movie})