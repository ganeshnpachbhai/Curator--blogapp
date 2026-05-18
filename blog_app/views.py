from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import PostForm, UserRegisterForm, CommentForm, UserUpdateForm, ProfileUpdateForm
from .models import Post, Category, Comment, Profile
from django.db.models import Count


class HomeView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 4

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            page_obj = context.get('page_obj')
            html = render_to_string('blog_app/partials/post_list.html', {'posts': context['posts']}, request=request)
            return JsonResponse({
                'html': html,
                'has_next': page_obj.has_next() if page_obj else False,
                'next_page_number': page_obj.next_page_number() if (page_obj and page_obj.has_next()) else None,
            })
            
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PostListView(ListView):

    model = Post
    template_name = 'blog_app/list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.GET.get('category')
        query = self.request.GET.get('q')

        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(body__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.request.GET.get('category')
        context['query'] = self.request.GET.get('q')
        return context



class PostDetailView(DetailView):
    model = Post
    template_name = 'blog_app/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=self.object.pk)
        
        context = self.get_context_data(object=self.object)
        context['comment_form'] = form
        return self.render_to_response(context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/create.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog_app/update.html'
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('post_list')

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog_app/delete.html'
    success_url = reverse_lazy('post_list')
    context_object_name = 'post'


    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('post_list')

# Authentication views
class RegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'blog_app/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        return render(request, 'blog_app/register.html', {'form': form})

class LoginUserView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'blog_app/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        return render(request, 'blog_app/login.html', {'form': form})

class LogoutUserView(View):
    def post(self, request):
        logout(request)
        return redirect('login')
    
    def get(self, request):
        logout(request)
        return redirect('login')

class LikePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            post.dislikes.remove(request.user)
        return redirect('post_detail', pk=pk)

    def get(self, request, pk):
        return self.post(request, pk)

class DislikePostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)
            post.likes.remove(request.user)
        return redirect('post_detail', pk=pk)

    def get(self, request, pk):
        return self.post(request, pk)


class ProfileView(DetailView):
    model = Profile
    template_name = 'blog_app/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs.get('username'))

class UpdateProfileView(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, 'blog_app/update_profile.html', {
            'u_form': u_form,
            'p_form': p_form
        })

    def post(self, request):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            profile = p_form.save(commit=False)
            if p_form.cleaned_data.get('clear_image'):
                profile.image = None
            profile.save()
            return redirect('profile', username=request.user.username)
        return render(request, 'blog_app/update_profile.html', {
            'u_form': u_form,
            'p_form': p_form
        })
