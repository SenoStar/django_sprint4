from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.views.generic import (
    DetailView, UpdateView, CreateView, DeleteView)
from .models import Comment, Category, Post
from .forms import (PostForm, UpdateProfileModelForm,
                    CommentForm, UpdateCommentModelForm)


# Количество постов на одной странице.
NUMBER_OF_POSTS = 10


def paginator_settings(request,
                       number_of_posts: int = 10,
                       category: str = '',
                       author: str = ''):
    """Настройка пагинатора."""
    if category != '':
        post_list = Post.objects.annotate(
            comment_count=Count("comments")
        ).filter(
            is_published=True, category__is_published=True,
            pub_date__lte=timezone.now(), category=category
        ).order_by('-pub_date')
    elif author != '':
        if author != request.user:
            post_list = Post.objects.annotate(
                comment_count=Count("comments")
            ).filter(
                author=author, is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')
        else:
            post_list = Post.objects.annotate(
                comment_count=Count("comments")
            ).filter(
                author=author
            ).order_by('-pub_date')
    else:
        post_list = Post.objects.annotate(
            comment_count=Count("comments")
        ).filter(
            is_published=True, category__is_published=True,
            pub_date__lte=timezone.now()).order_by('-pub_date')
    paginator = Paginator(post_list, number_of_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Главная с постами."""
    template = 'blog/index.html'
    page_obj = paginator_settings(request, NUMBER_OF_POSTS)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    """Пост."""
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        id=post_id
    )
    # Тут не CBV, поэтому отдельную функцию не буду делать))) лень.
    if request.user != post.author:
        post = get_object_or_404(
            Post,
            id=post_id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    form = CommentForm()
    comments = Comment.objects.filter(post_id=post_id)
    context = {'post': post,
               'form': form,
               'comments': comments
               }
    return render(request, template, context)


def category_posts(request, category_slug):
    """Посты по заданой категории."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug, is_published=True
    )
    page_obj = paginator_settings(request, NUMBER_OF_POSTS, category)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


class AuthorVerificationMixin(UserPassesTestMixin):
    """Проверка пользователя."""

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Ссылка после создания поста."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, AuthorVerificationMixin,
                     UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Ссылка после редактирования поста."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def get_object(self):
        """Получаем пост."""
        return get_object_or_404(Post,
                                 id=self.kwargs['post_id'])

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем другого пользователя на страницу поста."""
        if not self.test_func():
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, AuthorVerificationMixin,
                     DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        """Ссылка после удаления поста."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        """Получаем пост."""
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем другого пользователя на страницу поста."""
        if not self.test_func():
            return redirect(reverse('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']}))
        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(DetailView):
    """Информация профиля."""

    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        """Получаем пользователя из БД."""
        return get_object_or_404(User,
                                 username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        """Функция для передачи данных о профиле и его постов."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        user = self.request.user
        page_obj = paginator_settings(self.request,
                                      NUMBER_OF_POSTS,
                                      author=self.object)
        context['page_obj'] = page_obj
        context['user'] = user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление данных пользователя."""

    model = User
    template_name = 'blog/user.html'
    form_class = UpdateProfileModelForm

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.object.username})

    def get_object(self):
        return get_object_or_404(User,
                                 username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.post_obj.id})


class CommentUpdateView(LoginRequiredMixin, AuthorVerificationMixin,
                        UpdateView):
    """Редактирование комментариев."""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = UpdateCommentModelForm

    def get_object(self):
        return get_object_or_404(Comment,
                                 id=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем другого пользователя на страницу поста."""
        if not self.test_func():
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, AuthorVerificationMixin,
                        DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment,
                                 id=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляем другого пользователя на страницу поста."""
        if not self.test_func():
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
