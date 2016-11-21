# coding=utf-8
import csv
from django.core.exceptions import ValidationError

from gestion import models


def import_csv_becarios(csv_file):
    reader = csv.reader(csv_file)
    new_becarios = []

    for index, row in enumerate(reader):
        if not row[8]:
            row[8] = None
        if row[9] == 'Sí':
            bool_permisos = True
        else:
            bool_permisos = False

        new_becario = models.Becario(estado=row[2][:1], dni=row[3], apellido1=row[4], apellido2=row[5],
                                     nombre=row[6], email=row[7], telefono=row[8], titulacion=row[11], permisos=bool_permisos)
        try:
            new_becario.full_clean()
            new_becario.save()
        except ValidationError as e:
            new_becarios.append("Error en linea " +
                                unicode(index + 1) + ": " + unicode(e.error_dict))
    if new_becarios:
        raise ValidationError(new_becarios)

def import_csv_centros_plazas(csv_file):
    reader = list(csv.reader(csv_file))
    errors = []

    for index, row in enumerate(reader):
        '''if not row[2]:
            nombre = reader[index - 1][2]
        else:
            nombre = row[2]'''
        nombre = find_nombre(reader, index)
        print('nombre magico de línea: ' + str(index) + ': ' + str(nombre))
        new_centro = models.Centro(nombre=nombre)

        try:
            new_centro.full_clean()
            new_centro.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                                unicode(index + 1) + ": " + unicode(e.error_dict))
        new_plaza = models.Plaza(pk=row[0], horario=row[1], centro=new_centro)

        try:
            new_plaza.full_clean()
            new_plaza.save()
        except ValidationError as e:
            errors.append("Error en linea " +
                                unicode(index + 1) + ": " + unicode(e.error_dict))

    if errors:
        raise ValidationError(errors)

def find_nombre(rows, index):
    if not rows[index][2]:
        find_nombre(rows, index - 1)
    else:
        return rows[index][2]