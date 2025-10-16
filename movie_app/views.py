import os
import json
import uuid
import time
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from .forms import MovieForm, JSONUploadForm
from .utils.json_validator import validate_movie_json

def get_movies_from_json():
    """Получить все фильмы из JSON файлов"""
    movies = []
    json_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    
    if not os.path.exists(json_dir):
        return movies
    
    for filename in os.listdir(json_dir):
        if filename.endswith('.json') and filename.startswith('movie_'):
            file_path = os.path.join(json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    movie_data = json.load(f)
                    if isinstance(movie_data, list) and len(movie_data) > 0:
                        # Добавляем ID файла для редактирования/удаления
                        movie_data[0]['file_id'] = filename
                        movies.append(movie_data[0])
            except Exception as e:
                print(f"Ошибка чтения файла {filename}: {e}")
                continue
    
    # Сортируем по дате создания (новые сверху)
    movies.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return movies

def save_movie_to_json(movie_data):
    """Сохранить фильм в JSON файл"""
    json_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    os.makedirs(json_dir, exist_ok=True)
    
    filename = f"movie_{uuid.uuid4().hex[:12]}.json"
    file_path = os.path.join(json_dir, filename)
    
    # Добавляем временную метку если её нет
    if 'created_at' not in movie_data:
        movie_data['created_at'] = str(timezone.now())
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([movie_data], f, ensure_ascii=False, indent=2)
    
    return filename

def delete_movie_file(filename):
    """Удалить файл фильма"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'json_files', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def movie_list(request):
    """Главная страница со списком фильмов"""
    movies = get_movies_from_json()
    
    # Получаем список всех JSON файлов для отображения
    json_dir = os.path.join(settings.MEDIA_ROOT, 'json_files')
    json_files = []
    if os.path.exists(json_dir):
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(json_dir, filename)
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
        'has_json_files': len(json_files) > 0,
        'movies_count': len(movies)
    }
    return render(request, 'movie_app/movie_list.html', context)

def add_movie(request):
    """Добавление нового фильма"""
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            # Создаем словарь с данными фильма
            movie_data = {
                'title': form.cleaned_data['title'],
                'director': form.cleaned_data['director'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'duration': form.cleaned_data['duration'],
                'rating': form.cleaned_data['rating'],
                'description': form.cleaned_data['description'],
                'cast': form.cleaned_data['cast'],
                'image_url': form.cleaned_data['image_url'] or '',
                'created_at': str(timezone.now())
            }
            
            # Сохраняем в JSON
            filename = save_movie_to_json(movie_data)
            messages.success(request, f'Фильм "{movie_data["title"]}" успешно добавлен и сохранен в JSON!')
            return redirect('movie_app:movie_list')
    else:
        form = MovieForm()
    
    return render(request, 'movie_app/add_movie.html', {'form': form})

def edit_movie(request, file_id):
    """Редактирование фильма"""
    movies = get_movies_from_json()
    movie_to_edit = None
    
    # Находим фильм для редактирования
    for movie in movies:
        if movie.get('file_id') == file_id:
            movie_to_edit = movie
            break
    
    if not movie_to_edit:
        messages.error(request, 'Фильм не найден!')
        return redirect('movie_app:movie_list')
    
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            # Удаляем старый файл
            delete_movie_file(file_id)
            
            # Создаем новый с обновленными данными
            movie_data = {
                'title': form.cleaned_data['title'],
                'director': form.cleaned_data['director'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'duration': form.cleaned_data['duration'],
                'rating': form.cleaned_data['rating'],
                'description': form.cleaned_data['description'],
                'cast': form.cleaned_data['cast'],
                'image_url': form.cleaned_data['image_url'] or '',
                'created_at': movie_to_edit.get('created_at', str(timezone.now()))
            }
            
            # Сохраняем обновленный фильм
            save_movie_to_json(movie_data)
            messages.success(request, f'Фильм "{movie_data["title"]}" успешно обновлен!')
            return redirect('movie_app:movie_list')
    else:
        # Заполняем форму текущими данными
        form = MovieForm(initial={
            'title': movie_to_edit.get('title', ''),
            'director': movie_to_edit.get('director', ''),
            'year': movie_to_edit.get('year', ''),
            'genre': movie_to_edit.get('genre', ''),
            'duration': movie_to_edit.get('duration', ''),
            'rating': movie_to_edit.get('rating', ''),
            'description': movie_to_edit.get('description', ''),
            'cast': movie_to_edit.get('cast', ''),
            'image_url': movie_to_edit.get('image_url', ''),
        })
    
    return render(request, 'movie_app/edit_movie.html', {
        'form': form, 
        'movie': movie_to_edit,
        'file_id': file_id
    })

def delete_movie(request, file_id):
    """Удаление фильма"""
    movies = get_movies_from_json()
    movie_to_delete = None
    
    # Находим фильм для удаления
    for movie in movies:
        if movie.get('file_id') == file_id:
            movie_to_delete = movie
            break
    
    if not movie_to_delete:
        messages.error(request, 'Фильм не найден!')
        return redirect('movie_app:movie_list')
    
    if request.method == 'POST':
        # Удаляем файл
        if delete_movie_file(file_id):
            messages.success(request, f'Фильм "{movie_to_delete["title"]}" успешно удален!')
        else:
            messages.error(request, 'Ошибка при удалении фильма!')
        return redirect('movie_app:movie_list')
    
    return render(request, 'movie_app/delete_movie.html', {
        'movie': movie_to_delete,
        'file_id': file_id
    })

def upload_json(request):
    """Загрузка JSON файлов с импортом фильмов"""
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['json_file']
            
            # Генерируем безопасное имя файла
            original_name = uploaded_file.name
            safe_name = f"uploaded_{uuid.uuid4().hex[:8]}_{original_name}"
            
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
                try:
                    # Читаем данные из файла
                    with open(file_path, 'r', encoding='utf-8') as f:
                        movies_data = json.load(f)
                    
                    # Импортируем фильмы
                    imported_count = 0
                    for movie_data in movies_data:
                        # Проверяем, нет ли уже такого фильма
                        existing_movies = get_movies_from_json()
                        is_duplicate = False
                        
                        for existing_movie in existing_movies:
                            if (existing_movie['title'] == movie_data['title'] and 
                                existing_movie['director'] == movie_data['director'] and 
                                existing_movie['year'] == movie_data['year']):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            # Сохраняем как отдельный файл фильма
                            movie_filename = save_movie_to_json(movie_data)
                            imported_count += 1
                    
                    if imported_count > 0:
                        messages.success(request, f'Успешно импортировано {imported_count} фильмов из {len(movies_data)}!')
                    else:
                        messages.warning(request, 'Все фильмы из файла уже существуют в базе')
                    
                except Exception as e:
                    messages.error(request, f'Ошибка при импорте данных: {str(e)}')
            
            return redirect('movie_app:movie_list')
    
    else:
        form = JSONUploadForm()
    
    return render(request, 'movie_app/upload_json.html', {'form': form})

def export_all_movies(request):
    """Экспорт всех фильмов в один JSON файл"""
    movies = get_movies_from_json()
    
    # Убираем служебные поля
    for movie in movies:
        movie.pop('file_id', None)
    
    response = HttpResponse(
        json.dumps(movies, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = 'attachment; filename="all_movies.json"'
    return response

def view_json_file(request, filename):
    """Просмотр содержимого JSON файла"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'json_files', filename)
    
    if not os.path.exists(file_path):
        return HttpResponse("Файл не найден", status=404)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(f"<pre>{content}</pre><br><a href='/'>Назад</a>")
    except Exception as e:
        return HttpResponse(f"Ошибка при чтении файла: {str(e)}", status=500)