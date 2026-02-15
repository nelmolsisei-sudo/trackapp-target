from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Layout, Submit, Div
from crispy_forms.helper import FormHelper

from django import forms

from .models import *

class UploadForm(forms.Form):
    file = forms.FileField()
    team = forms.ModelChoiceField(queryset=Team.objects.all().order_by('name'))
    season = forms.ModelChoiceField(queryset=Season.objects.all().order_by('name'))
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female')
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

class QualifyingUploadForm(forms.Form):
    file = forms.FileField()
    season = forms.ModelChoiceField(queryset=Season.objects.all().order_by('name'))

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender']


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        exclude = [
            'id', 'athlete', 
            'qualifications', 'milestones', 'personal_rank']

    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)

        self.fields["meet"].queryset = Meet.objects.all().prefetch_related(
            'team'
        ).order_by('-date')

class MergeAthleteForm(forms.Form):

    user = forms.ModelChoiceField(queryset=User.objects.all().order_by('username'))

class SeasonGoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        exclude = ['user', 'creator', 'meet']


class MergeMeetForm(forms.Form):

    meet = forms.ModelChoiceField(
        queryset=Meet.objects.all().order_by('-date').prefetch_related('team')
    )

    def __init__(self, *args, **kwargs):
        meet = kwargs.pop('meet')
        super(MergeMeetForm, self).__init__(*args, **kwargs)

        self.fields["meet"].queryset = Meet.objects.filter(
            team=meet.team
        ).exclude(
            id=meet.id
        ).prefetch_related(
            'team'
        ).order_by('-date')


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class CoachForm(forms.ModelForm):
    class Meta:
        model=Team
        exclude = ['name', 'athletes']

class AthleteTeamForm(forms.ModelForm):
    class Meta:
        model=Team
        exclude = ['coaches', 'name']

class MergeEventForm(forms.Form):

    event = forms.ModelChoiceField(queryset=Event.objects.all().order_by('name'))


class QualifyingLevelForm(forms.ModelForm):
    class Meta:
        model = QualifyingLevel
        exclude = ['id']


class QualifyingFilterForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all().order_by('name'),
        required=False,
        empty_label="All events")

    season = forms.ModelChoiceField(
        queryset=Season.objects.all().order_by('name'),
        required=False,
        empty_label="All seasons")

    GENDER_CHOICES = [
        ('', 'Male and Female'),
        ('male', 'Male'),
        ('female', 'Female')
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)



