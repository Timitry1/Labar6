from django.shortcuts import render, redirect
from .models import Article
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def archive(request):
    return render(request, 'archive.html', {"posts": Article.objects.all()})


def get_article(request, article_id):
    try:
        post = Article.objects.get(id=article_id)
        return render(request, 'article.html', {"post": post})
    except Article.DoesNotExist:
        raise Http404


def create_post(request):
    if not request.user.is_anonymous:
        if request.method == "POST":
            form = {
                'text': request.POST["text"], 'title': request.POST["title"]
            }
            if form["text"] and form["title"]:
                if Article.objects.filter(title=form["title"]).exists():
                    form['errors'] = u"Статья с таким названием уже существует"
                    return render(request, 'newPost.html', {'form': form})
                else:
                    article = Article.objects.create(text=form["text"], title=form["title"], author=request.user)
                    return redirect('get_article', article_id=article.id)
            else:
                form['errors'] = u"Не все поля заполнены"
                return render(request, 'newPost.html', {'form': form})
        else:
            return render(request, 'newPost.html', {})
    else:
        raise Http404


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        if password != confirm_password:
            context = {'error': 'Пароли не совпадают.'}
            return render(request, 'createAcc.html', context)

        if User.objects.filter(username=username).exists():
            context = {'error': 'Это имя уже занято.'}
            return render(request, 'createAcc.html', context)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user = authenticate(request, username=username, password=password)
        login(request, user)

        return redirect('archive')
    else:
        return render(request, 'createAcc.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('archive')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
    else:
        return render(request, 'login.html')
