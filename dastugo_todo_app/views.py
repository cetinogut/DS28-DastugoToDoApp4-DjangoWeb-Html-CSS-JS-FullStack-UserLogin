from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy # for redirecting user after edits

from django.contrib.auth.views import LoginView # bring the default login view
from django.contrib.auth.mixins import LoginRequiredMixin # login required restriction added by this mixin
from django.contrib.auth.forms import UserCreationForm # once we create user, we directly login the user with the line below
from django.contrib.auth import login

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm

# Create your views here.

# def taskList(request):
#     return HttpResponse('To Do List')

class CustomLoginView(LoginView):
    template_name = 'dastugo_todo_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True # if user already auth. redirect it from here

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'dastugo_todo_app/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): #override to auto login the new user
        user = form.save()
        if user is not None: #user created successfully
            login(self.request, user) # automatically login the new user after success above
        return super(RegisterPage, self).form_valid(form)

    """ def get(self, *args, **kwargs): # if the line redirect_authenticated_user = True above is working no need forthis code block
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs) """


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks' # otherwise we have to use object_list for default list name in the template

    def get_context_data(self, **kwargs): ## overriding this func to bring only user related tasks
        context = super().get_context_data(**kwargs) ## coming from original item
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(completed=False).count()

        search_input = self.request.GET.get('search-area') or '' ## search is a GEt method
        if search_input: # if there is a search tem do the filtering in title basd on search input
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task' # override object name, otherwise we need to use object in template 
    template_name = 'dastugo_todo_app/task.html' # override template name, without this overriding propery we need to use task_detail.html


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'completed']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): ##override this method to get logged in user info pass to the form
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'completed']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))