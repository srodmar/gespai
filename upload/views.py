from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponseRedirect
import pdb
from gestion import models

from . import forms
from .imports import import_csv_becarios, import_csv_emplazamientos_plazas, import_csv_plan_formacion

# Create your views here.


class UploadView(TemplateView):
    template_name = 'upload/upload.html'


def upload_becarios(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            errors = import_csv_becarios(request.FILES['csv_file_field'])
            if errors:
                print('Errores en Becarios')
                for error in errors:
                    error_message = 'Error en linea ' + str(error[0]) + ': '
                    for key, value in error[1].error_dict.iteritems():
                        error_message += key + ': ' + \
                            unicode(value[0].messages[0]) + ' '
                    messages.error(request, error_message)
                return HttpResponseRedirect('/upload/becarios')
            return HttpResponseRedirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})


def upload_emplazamientos_plazas(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            errors = import_csv_emplazamientos_plazas(
                request.FILES['csv_file_field'])
            if errors:
                print('errores en Plazas y Centros')
                for error in errors:
                    error_message = 'Error en linea ' + str(error[0]) + ': '
                    for key, value in error[1].error_dict.iteritems():
                        error_message += key + ': ' + \
                            unicode(value[0].messages[0]) + ' '
                    messages.error(request, error_message)
                return HttpResponseRedirect('/upload/plazas')
            return HttpResponseRedirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})


def upload_plan_formacion(request):
    if request.method == 'POST':
        form = forms.UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            errors = import_csv_plan_formacion(request.FILES['csv_file_field'])
            if errors:
                print('errores en PlanFormacion')
                for error in errors:
                    error_message = 'Error en linea ' + str(error[0]) + ': '
                    if isinstance(error[1], models.Becario.DoesNotExist) or isinstance(error[1], models.PlanFormacion.DoesNotExist):
                        error_message += error[1].message
                    else:
                        for key, value in error[1].error_dict.iteritems():
                            error_message += key + ': ' + \
                                unicode(value[0].messages[0]) + ' '
                    messages.error(request, error_message)
                return HttpResponseRedirect('/upload/formacion')
            return HttpResponseRedirect('/upload')
    else:
        form = forms.UploadCSVForm()
    return render(request, 'upload/upload_form.html', {'form': form})