from datetime import datetime
from datetime import date
from calendar import monthrange

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render_to_response, get_object_or_404

from django.http import Http404
from django.http import HttpResponseRedirect

from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm


from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse, reverse_lazy

from django.conf import settings

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    TemplateView,
)

from meets.models import (
    Venue,
    BookMeeting,
)

from meets.forms import (
    MeetBookForm,
    VenueForm,
    PasswordChangeForm,
    UserCreationForm,
)

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
import json


# Create your views here.


now = datetime.now()


def logouts(request):
    logout(request)
    return redirect(reverse('bookapp-login'))

class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(request, *args, **kwargs)

class LoginView(FormView):

    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'registration/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('home-view')

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log him in.
        """
        username = form.cleaned_data["username"] 
        password = form.cleaned_data["password"]     
        user = authenticate(username=username, password=password) 
        if user: 
            login(self.request, user) 
        #login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False
 
    
    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(), but adds test cookie stuff
        """
        if request.user.is_authenticated():
            return redirect('home-view')
 
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.post(), but adds test cookie stuff
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)

class LogoutView(LoggedInMixin, TemplateView):
    
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect(reverse('bookapp-login'))
   
    def get_context_data(self, **kwargs):
        context = super(LogoutView, self).get_context_data(**kwargs)
        return context

class CreateUser(CreateView):

    model = User
    template_name = 'register.html' 
    form_class = UserCreationForm
    
    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log him in.
        """
        print ('0c')  
        form.save()
        """ 
        if self.request.is_ajax():
            to_json_responce = dict()
            to_json_responce['status'] = 0
            to_json_responce['form_errors'] = form.errors

            to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

            return HttpResponse(json.dumps(to_json_responce), content_type='application/json')
        """  
        username = form.cleaned_data["username"] 
        password2 = form.cleaned_data["password2"]    
        user = authenticate(username=username, password=password2)
        human = True 

        if user: 
            login(self.request, user)
            HttpResponseRedirect(self.get_success_url())

        return HttpResponseRedirect(reverse('bookapp-login'))

    def form_invalid(self, form):
        """
        form.save()
        if self.request.is_ajax():
            to_json_responce = dict()
            to_json_responce['status'] = 1

            to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
            to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

            return HttpResponse(json.dumps(to_json_responce), content_type='application/json')
        """

    def get(self, request, *args, **kwargs):
        print ('1c')
        if request.user.is_authenticated():
            return redirect('home-view')
        return super(CreateUser, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        print ('2c')   
        kwargs = super(CreateUser, self).get_form_kwargs()
        return kwargs

    def get_initial(self):
        print ('3c')
        initial = super(CreateUser, self).get_initial()
        return initial

    def get_success_url(self):
        print ('4c')
        return reverse('home-view')
        #return reverse('bookapp-login')

    def get_context_data(self, **kwargs):
        print ('5c')
        context = super(CreateUser, self).get_context_data(**kwargs)
        context['action'] = reverse('bookapp-register')
        return context

    def post(self, request, *args, **kwargs):
        print ('6c')
        return super(CreateUser, self).post(request, *args, **kwargs)



class PasswordResetView(LoggedInMixin, FormView):
    """
    Class based version of django.contrib.auth.views.password_reset
    """
    #form_class = PasswordResetForm
    form_class = PasswordChangeForm
    template_name = 'registration/password_change_form.html'
    
    def get_success_url(self):
        return reverse('home-view')

    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())

    def get_form_class(self):
        return self.form_class

    def get(self, request, *args, **kwargs):
        return super(PasswordResetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return super(PasswordResetView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordResetView, self).get_form_kwargs()
        kwargs['current_user'] = get_object_or_404(User, username__exact = self.request.user)
        return kwargs

    
    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        print ('1=')
        return context


    def form_valid(self, form):
        """
        User has entered an email address of a valid user (checked by PasswordResetForm)
        """
        form.save()
        return HttpResponseRedirect(self.get_success_url())



class ListMeetView(LoggedInMixin, ListView):

    model = BookMeeting
    template_name = 'meet_list.html'
    context_object_name = 'bookings'

    def get_success_url(self):
         
        if not request.user.is_active:
            return redirect('bookapp-login')

        return reverse('meets-list')

    def get_queryset(self):
        today = datetime.now()
        my_year = int(today.year)
        my_month = int(today.month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])

        return BookMeeting.objects.filter(book_date__gte=my_calendar_from_month).filter(book_date__lte=my_calendar_to_month)


    def get_context_data(self, **kwargs):
        context = super(ListMeetView, self).get_context_data(**kwargs)
        today = datetime.now()
        my_year = int(today.year)
        my_month = int(today.month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])
        my_previous_year = my_year
        my_previous_month = my_month - 1
        if my_previous_month == 0:
            my_previous_year = my_year - 1
            my_previous_month = 12
        my_next_year = my_year
        my_next_month = my_month + 1
        if my_next_month == 13:
            my_next_year = my_year + 1
            my_next_month = 1
        my_year_after_this = my_year + 1
        my_year_before_this = my_year - 1
        
        my_events = BookMeeting.objects.filter(book_date__gte=my_calendar_from_month).filter(book_date__lte=my_calendar_to_month)
          
        context['events_list'] = my_events
        context['month'] = my_month
        context['month_name'] = named_month(my_month)
        context['year'] = my_year
        context['previous_month'] = my_previous_month,
        context['previous_month_name'] = named_month(my_previous_month),
        context['previous_year'] = my_previous_year,
        context['next_month'] = my_next_month,
        context['next_month_name'] = named_month(my_next_month),
        context['next_year'] = my_next_year,
        context['year_before_this'] = my_year_before_this,
        context['year_after_this'] = my_year_after_this,
        context['prevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_month})
        context['nextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_month}) 
        context['nextMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_next_month}) 
        context['prevMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_previous_month}) 
        context['prevMonthprevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_previous_month})
        context['nextMonthnextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_next_month})
         
        return context


class MonthMeetView(LoggedInMixin, ListView):

    model = BookMeeting
    template_name = 'meet_list.html'
    context_object_name = 'bookings'

    def get_success_url(self):
        if not request.user.is_active:
            return redirect('bookapp-login')

        return reverse('meets-list')

    def get_queryset(self):
        
        year = self.kwargs.get('year', None)
        month = self.kwargs.get('month', None)
        my_year = int(year)
        my_month = int(month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])

        return BookMeeting.objects.filter(book_date__gte=my_calendar_from_month).filter(book_date__lte=my_calendar_to_month)

    def get_context_data(self, **kwargs):
        context = super(MonthMeetView, self).get_context_data(**kwargs)
        
        year = self.kwargs.get('year', None)
        month = self.kwargs.get('month', None)

        my_year = int(year)
        my_month = int(month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])
        my_previous_year = my_year
        my_previous_month = my_month - 1
        if my_previous_month == 0:
            my_previous_year = my_year - 1
            my_previous_month = 12
        my_next_year = my_year
        my_next_month = my_month + 1
        if my_next_month == 13:
            my_next_year = my_year + 1
            my_next_month = 1
        my_year_after_this = my_year + 1
        my_year_before_this = my_year - 1
        
        my_events = BookMeeting.objects.filter(book_date__gte=my_calendar_from_month).filter(book_date__lte=my_calendar_to_month)
          
        context['events_list'] = my_events
        context['month'] = my_month
        context['month_name'] = named_month(my_month)
        context['year'] = my_year
        context['previous_month'] = my_previous_month,
        context['previous_month_name'] = named_month(my_previous_month),
        context['previous_year'] = my_previous_year,
        context['next_month'] = my_next_month,
        context['next_month_name'] = named_month(my_next_month),
        context['next_year'] = my_next_year,
        context['year_before_this'] = my_year_before_this,
        context['year_after_this'] = my_year_after_this,
        context['prevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_month})
        context['nextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_month}) 
        context['nextMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_next_month}) 
        context['prevMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_previous_month}) 
        context['prevMonthprevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_previous_month})
        context['nextMonthnextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_next_month})
         
        return context
        

class DayMonthMeetView(LoggedInMixin, ListView):

    model = BookMeeting
    template_name = 'meet_list.html'
    context_object_name = 'bookings'
    date_field = 'book_date'

    def get_success_url(self):
        if not request.user.is_active:
            return redirect('bookapp-login')

        return reverse('meets-list')

    def get_queryset(self):
        qs = BookMeeting.objects
        if 'day' in self.kwargs:
            qs = qs.filter(book_date__day=self.kwargs['day'])
        if 'month' in self.kwargs:
            qs = qs.filter(book_date__month=self.kwargs['month'])
        if 'year' in self.kwargs:
            qs = qs.filter(book_date__year=self.kwargs['year'])
        return qs 
        
    def get_context_data(self, **kwargs):
        context = super(DayMonthMeetView, self).get_context_data(**kwargs)
        
        year = self.kwargs.get('year', None)
        month = self.kwargs.get('month', None)
        
        my_year = int(year)
        my_month = int(month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])
        my_previous_year = my_year
        my_previous_month = my_month - 1
        if my_previous_month == 0:
            my_previous_year = my_year - 1
            my_previous_month = 12
        my_next_year = my_year
        my_next_month = my_month + 1
        if my_next_month == 13:
            my_next_year = my_year + 1
            my_next_month = 1
        my_year_after_this = my_year + 1
        my_year_before_this = my_year - 1
        
        my_events = BookMeeting.objects.filter(book_date__gte=my_calendar_from_month).filter(book_date__lte=my_calendar_to_month)
          
        context['events_list'] = my_events
        context['month'] = my_month
        context['month_name'] = named_month(my_month)
        context['year'] = my_year
        context['previous_month'] = my_previous_month,
        context['previous_month_name'] = named_month(my_previous_month),
        context['previous_year'] = my_previous_year,
        context['next_month'] = my_next_month,
        context['next_month_name'] = named_month(my_next_month),
        context['next_year'] = my_next_year,
        context['year_before_this'] = my_year_before_this,
        context['year_after_this'] = my_year_after_this,
        context['prevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_month})
        context['nextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_month}) 
        context['nextMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_next_month}) 
        context['prevMonthYear']  = reverse('meets-month', kwargs={'year': my_year, 'month': '%02d' % my_previous_month}) 
        context['prevMonthprevYear']  = reverse('meets-month', kwargs={'year': my_year_before_this, 'month': '%02d' % my_previous_month})
        context['nextMonthnextYear']  = reverse('meets-month', kwargs={'year': my_year_after_this, 'month': '%02d' % my_next_month})
         
        return context


class MeetView(LoggedInMixin, DetailView):

    model = BookMeeting
    template_name = 'meet.html'
    context_object_name = 'booking'
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.request.user.id == self.object.user.id:
                raise Http404()
        except Http404:
            # redirect here
            return redirect('meets-list')
        except ObjectDoesNotExist:
            return redirect('meets-list')  
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(BookMeeting, pk=pk)

    def get_context_data(self, **kwargs):
        context = super(MeetView, self).get_context_data(**kwargs)
        context['edit']  = reverse('meets-edit', kwargs={'pk': self.get_object().id}) 

        return context


class CreateMeetView(LoggedInMixin, CreateView):

    model = BookMeeting
    template_name = 'meet_create.html'
    form_class = MeetBookForm
    
    def get_success_url(self):
        return reverse('meets-list')

    def get_initial(self):
        initial = super(CreateMeetView, self).get_initial()
            
        initial['book_date'] = now.date()
        initial['from_time'] = '08:00:00'
        initial['to_time'] = '10:00:00' 
        
        return initial


    def get(self, request, *args, **kwargs):
        return super(CreateMeetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(CreateMeetView, self).post(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs = super(CreateMeetView, self).get_form_kwargs()
        kwargs['usera'] = get_object_or_404(User, id__exact = self.request.user.id)
        kwargs['initial']['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateMeetView, self).get_context_data(**kwargs)
        context['action'] = reverse('meets-new')

        return context


class UpdateMeetView(LoggedInMixin, UpdateView):

    model = BookMeeting
    template_name = 'meet_edit.html'
    form_class = MeetBookForm

    def get_form_kwargs(self):
        kwargs = super(UpdateMeetView, self).get_form_kwargs()
        kwargs['usera'] = get_object_or_404(User, id__exact = kwargs['instance'].user.id)
        print ('bva4=') 
        return kwargs

    def post(self, request, *args, **kwargs):
        return super(UpdateMeetView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print ('bva3=')
        try:
            self.object = self.get_object()
            if not self.request.user.id == self.object.user.id:
                raise Http404()
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        except Http404:
            return redirect('meets-list')
        except ObjectDoesNotExist:
            return redirect('meets-list')  
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)


    def get_success_url(self):
        return reverse('meets-list')

    def form_valid(self, form):
        """
        User has entered an email address of a valid user (checked by PasswordResetForm)
        """
        form.save()
        return HttpResponseRedirect(self.get_success_url())
 
    def get_object(self, queryset=None):
        print ('bva0=') 
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(BookMeeting, pk=pk)

    def get_context_data(self, **kwargs):
        print ('a1=') 
        context = super(UpdateMeetView, self).get_context_data(**kwargs)
        context['delet']  = reverse('meets-delete', kwargs={'pk': self.get_object().id})
        context['action'] = reverse('meets-edit', kwargs={'pk': self.get_object().id})
        return context

class DeleteMeetView(LoggedInMixin, DeleteView):

    model = BookMeeting
    template_name = 'meet_delete.html'
    context_object_name = 'booking'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.request.user.id == self.object.user.id:
                raise Http404()
        except Http404:
            return redirect('meets-list')
        except ObjectDoesNotExist:
            return redirect('meets-list')  
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(BookMeeting, pk=pk)

    def get_success_url(self):
        return reverse('meets-list')

    def get_context_data(self, **kwargs):

        context = super(DeleteMeetView, self).get_context_data(**kwargs)
        context['action']  = reverse('meets-delete', kwargs={'pk': self.get_object().id})
        return context

class HomeView(LoggedInMixin, TemplateView):   # ListView
     
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context

class VenueViewList(LoggedInMixin, ListView):

    model = Venue
    template_name = 'venue_list.html'
    context_object_name = 'venues'

    def get(self, request, *args, **kwargs):
        try:
            self.object_list = self.get_queryset()
            if not self.request.user.is_superuser:
                raise Http404()
        except Http404:
            return redirect('home-view')
        except ObjectDoesNotExist:
            return redirect('home-view')  
        
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def get_queryset(self):
        return Venue.objects.all

    def get_context_data(self, **kwargs):
        context = super(VenueViewList, self).get_context_data(**kwargs)
        return context

class VenueView(LoggedInMixin, DetailView):

    model = Venue
    template_name = 'venue.html'
    context_object_name = 'venue'
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.request.user.is_superuser:
                raise Http404()
        except Http404:
            return redirect('home-view')
        except ObjectDoesNotExist:
            return redirect('home-view')  
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        code = self.kwargs.get('code', None)
        return get_object_or_404(Venue, code=code)


    def get_context_data(self, **kwargs):
        context = super(VenueView, self).get_context_data(**kwargs)
        context['edit']  = reverse('venue-edit', kwargs={'code': self.get_object().code}) 

        return context


class VenueViewUpdate(LoggedInMixin, UpdateView):

    model = Venue
    template_name = 'venue_edit.html'
    form_class = VenueForm
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.request.user.is_superuser:
                raise Http404()
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        except Http404:
            return redirect('venue-list')
        except ObjectDoesNotExist:
            return redirect('venue-list')  
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('venue-list')

    def get_object(self, queryset=None):
        code = self.kwargs.get('code', None)
        return get_object_or_404(Venue, code=code)

    def get_context_data(self, **kwargs):
        context = super(VenueViewUpdate, self).get_context_data(**kwargs)
        context['delet']  = reverse('venue-delete', kwargs={'code': self.get_object().code})
        context['action'] = reverse('venue-edit', kwargs={'code': self.get_object().code})
        return context


class VenueViewDelete(LoggedInMixin, DeleteView):

    model = Venue
    template_name = 'venue_delete.html'
    context_object_name = 'venue'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if not self.request.user.is_superuser:
                raise Http404()
        except Http404:
            return redirect('home-view')
        except ObjectDoesNotExist:
            return redirect('home-view')  
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        code = self.kwargs.get('code', None)
        return get_object_or_404(Venue, code=code)

    def get_success_url(self):
        return reverse('venue-list')

    def get_context_data(self, **kwargs):

        context = super(VenueViewDelete, self).get_context_data(**kwargs)
        context['action']  = reverse('venue-delete', kwargs={'code': self.get_object().code})
        return context


class VenueViewCreate(LoggedInMixin, CreateView):
    
    model = Venue
    template_name = 'venue_create.html'
    form_class = VenueForm
    context_object_name = 'venue'
    
    def get_success_url(self):
        return reverse('venue-list')

    def get(self, request, *args, **kwargs):
        try:
            self.object = None
            if not self.request.user.is_superuser:
                raise Http404()
        except Http404:
            return redirect('home-view')
        
        return super(VenueViewCreate, self).get(request, *args, **kwargs)
    

    def get_object(self, queryset=None):
        code = self.kwargs.get('code', None)
        return get_object_or_404(Venue, code=code)

    def get_initial(self):
        initial = super(VenueViewCreate, self).get_initial()
        initial['venue_name'] = 'SIC101'
        initial['venue_capacity'] = '25'
        
        return initial

    def get_form(self, form_class):
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(VenueViewCreate, self).get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(VenueViewCreate, self).get_context_data(**kwargs)
        context['action'] = reverse('venue-new')

        return context

##

##### Here's code for the view to look up the event objects for to put in 
# the context for the template. It goes in your app's views.py file (or 
# wherever you put your views).
#####

def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    return date(1900, month_number, 1).strftime("%B")


