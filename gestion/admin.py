from django.contrib import admin

# Register your models here.

from .models import Becario, Plaza, Centro, PrelacionBecario, PlanFormacion, AsistenciaFormacion

class BecarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono',
    'plaza_asignada', 'estado')
    list_filter = ['plaza_asignada', 'titulacion', 'horario_asignado', 'estado']
    search_fields = ['nombre', 'apellido1', 'apellido2', 'dni', 'email', 'telefono']

class BecarioInline(admin.StackedInline):
    model = Becario
    extra = 0

class PlazaInline(admin.StackedInline):
    model = Plaza
    extra = 0

class PlazaAdmin(admin.ModelAdmin):
    inlines = [BecarioInline]

class CentroAdmin(admin.ModelAdmin):
    inlines = [PlazaInline]

admin.site.register(Becario, BecarioAdmin)
admin.site.register(Plaza, PlazaAdmin)
admin.site.register(Centro, CentroAdmin)
admin.site.register(PrelacionBecario)
admin.site.register(PlanFormacion)
admin.site.register(AsistenciaFormacion)
