# coding=utf-8
import csv
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from gestion import models
import re


def import_csv_becarios(csv_file):
    reader = csv.reader(csv_file)
    errors = []

    for index, row in enumerate(reader):

        if is_codigo_tit(row[10]):
            new_titulacion, c = models.Titulacion.objects.get_or_create(codigo=row[10])
            new_titulacion.nombre = row[11].decode('utf-8')
            try:
                new_titulacion.full_clean()
                new_titulacion.save()
            except ValidationError as e:
                errors.append((index + 1, e))

        new_becario = models.Becario(orden=row[1],estado=row[2][:1], dni=row[3], apellido1=row[4].decode('utf-8'),
                         apellido2=row[5].decode('utf-8'), nombre=row[6].decode('utf-8'), email=row[7],
                         telefono=row[8] or None, titulacion=new_titulacion, permisos=has_permisos(row[9]))
        try:
            new_becario.full_clean()
            new_becario.save()
        except ValidationError as e:
            errors.append((index + 1, e))
    if errors:
        return errors


def import_csv_emplazamientos_plazas(csv_file):
    reader = list(csv.reader(csv_file))
    errors = []

    for index, row in enumerate(reader):

        nombre = find_nombre(reader, index)
        # Se comprueba si existe ya un Emplazamiento con el mismo nombre. Si no existe,
        # se crea. No se utiliza get_or_create ya que es necesario hacer validación
        # de los campos mediante full_clean.
        try:
            new_emplazamiento = models.Emplazamiento.objects.get(nombre=nombre)
        except ObjectDoesNotExist:
            new_emplazamiento = models.Emplazamiento(nombre=nombre.decode('utf-8'))
        
        try:
            new_emplazamiento.full_clean()
            new_emplazamiento.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                          unicode(index + 1) + ": " + unicode(e.error_dict))
        new_plaza = models.Plaza(pk=row[0], horario=row[1], emplazamiento=new_emplazamiento)

        try:
            new_plaza.full_clean()
            new_plaza.save()
        except ValidationError as e:
            errors.append((index + 1, e))

        if is_dni(row[6]):
            # De nuevo se omite usar get_or_create ya que hay que hacer
            # validación
            try:
                becario = models.Becario.objects.get(dni=row[6])
                becario.plaza_asignada = new_plaza
                becario.save()
            except ObjectDoesNotExist:
                if is_codigo_tit(row[14]):
                    try:
                        new_titulacion = models.Titulacion.objects.get(codigo=row[14])
                    except ObjectDoesNotExist:
                        new_titulacion = models.Titulacion(codigo=row[14], nombre='Titulación desconocida')
                        new_titulacion.save()
                becario = models.Becario(orden=row[5], dni=row[6], apellido1=row[7].decode('utf-8'),
                                         apellido2=row[8].decode('utf-8'), nombre=row[9].decode('utf-8'),
                                         email=row[11], telefono=row[12] or None, permisos=has_permisos(row[13]),
                                         titulacion=new_titulacion)
                try:
                    # Se asigna la plaza tras la creación del objeto para que se disparen
                    # las verificaciones del método save()
                    becario.plaza_asignada = new_plaza
                    becario.full_clean()
                    becario.save()
                except ValidationError as e:
                    errors.append((index + 1, e))

    if errors:
        return errors

def import_csv_plan_formacion(csv_file):
    reader = list(csv.reader(csv_file))
    errors = []

    # Se recorre todo el fichero CSV para crear los cursos
    for index, row in enumerate(reader):
        if is_codigo_actividad(row[1]):
            try:
                # Se busca la fecha de impartición del curso
                match = re.search('(\d{2})/(\d{2})/(\d{4})', row[2])
                # Se elimina la fecha para quedarnos solo con el nombre
                nombre = re.sub('\(\d{2}/\d{2}/\d{4}\)', '', row[2])
                dia = match.group(1)
                mes = match.group(2)
                anyo = match.group(3)
                # Se forma una fecha apta para el campo DateTimeField
                fecha = anyo + '-' + mes + '-' + dia
                # Se crea un objeto PlanFormacion
                new_plan_formacion = models.PlanFormacion(codigo=row[1], nombre_curso=nombre,
                fecha_imparticion=fecha)
            except AttributeError:
                # Si no se encuentra una fecha en el nombre, se crea un curso sin fecha
                new_plan_formacion = models.PlanFormacion(codigo=row[1], nombre_curso=row[2])

            try:
                new_plan_formacion.full_clean()
                new_plan_formacion.save()
            except ValidationError as e:
                errors.append((index + 1, e))

    # Una vez creados los cursos se comprueba qué becarios han asistido
    for index, row in enumerate(reader):
        if is_dni(row[3]):
            try:
                # Se busca el becario antes de entrar al bucle para reducir el número
                # de accesos a la BD
                becario = models.Becario.objects.get(dni=row[3])
                # Necesito saber el índice de la columna del CSV en la que me encuentro
                # para poder buscar el código de curso asociado a esa columna en la primera línea
                for ind, item in enumerate(row):
                    # Se busca el código del curso en la primera línea del CSV
                    if is_codigo_actividad(reader[0][ind]):
                        curso = models.PlanFormacion.objects.get(codigo=reader[0][ind])
                        new_asistencia = models.AsistenciaFormacion(becario=becario, curso=curso)
                        try:
                            # Si el becario ha asistido
                            if item == 'Sí':
                                new_asistencia.asistencia = True
                            new_asistencia.full_clean()
                            new_asistencia.save()
                        except ValidationError as e:
                            errors.append((index + 1, e))
            except ObjectDoesNotExist as e:
                errors.append((index + 1, e))

    if errors:
        return errors


# Método recursivo para encontrar el nombre de Emplazamiento en campos vacíos (porque
# los nombres repetidos aparecen como campos vacíos en el CSV)
def find_nombre(rows, ind):
    if rows[ind][2]:
        return rows[ind][2]
    else:
        return find_nombre(rows, (ind - 1))

# Métodos para comprobar si los campos del CSV son válidos

def is_dni(dni):
    if len(dni) == 8:
        if (dni[0].isalpha() and dni[1:].isdigit()) or dni.isdigit():
            return True
    return False


def is_codigo_tit(cod):
    if len(cod) == 4:
        if cod[0].isalpha and cod[1:].isdigit():
            return True
    return False


def has_permisos(perm):
    if perm == 'Sí':
        return True
    else:
        return False

def is_codigo_actividad(cod):
    if len(cod) > 0 and len(cod) <= 3:
        if cod[0] == 'A':
            return True
    return False
