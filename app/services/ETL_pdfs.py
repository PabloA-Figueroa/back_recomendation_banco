# -*- coding: utf-8 -*-
# Extraer información de los pdfs
import pdfplumber
import pandas as pd
import re

def extract_personal_map_data(pdf_path):
    """
    Extracts data from the Personal Map PDF.
    """
    data = {}

    with pdfplumber.open(pdf_path) as pdf:
        # Page 1 Extraction
        page1 = pdf.pages[0]
        text_page1 = page1.extract_text()

        # Helper function to handle regex safely
        def safe_search(pattern, text, group=1, default=None):
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            return match.group(group).strip() if match else default

        # Datos Personales
        data['nombre_completo'] = safe_search(r'IMPRESY APELLIDOS\s+(.+)', text_page1)
        data['numero_cedula'] = safe_search(r'NÚMERO DE CÉDULA\s+(\d+)', text_page1)
        data['telefono'] = safe_search(r'TELÉFONO\s+(\d+)', text_page1)
        data['correo'] = safe_search(r'CORREO ELECTRÓNICO\s+([\w\.-]+@[\w\.-]+)', text_page1)
        data['linkedin'] = safe_search(r'LINKEDIN\s+([\w\.\/\:]+)', text_page1)
        data['estado_civil'] = safe_search(r'ESTADO CIVIL\s+(\w+)', text_page1)
        data['fecha_nacimiento'] = safe_search(r'FECHA DE NACIMIENTO\s+(\d{2} de \w+ de \d{4})', text_page1)
        data['edad'] = safe_search(r'EDAD\s+(\d+ años)', text_page1)
        data['aspiracion_salarial'] = safe_search(r'ASPIRACIÓN SALARIAL\s+([\$\s\d\.]+)', text_page1)
        data['tipo_sangre'] = safe_search(r'TIPO DE SANGRE\s+(\w+\+?)', text_page1)
        data['direccion'] = safe_search(r'DIRECCIÓN \(BARRIO\)\s+(.+)', text_page1)

        # Datos Académicos
        table_academic = page1.extract_table()
        if table_academic:
            df_academic = pd.DataFrame(table_academic[1:], columns=table_academic[0])
            data['datos_academicos'] = df_academic.to_dict(orient="records")
        else:
            data['datos_academicos'] = []

        # Datos Laborales
        table_laboral = page1.extract_table()
        if table_laboral:
            df_laboral = pd.DataFrame(table_laboral[1:], columns=table_laboral[0])
            data['datos_laborales'] = df_laboral.to_dict(orient="records")
        else:
            data['datos_laborales'] = []

        # Conocimientos
        conocimientos_match = re.search(r'CONOCIMIENTOS\s+(.*?)\s+AFICIONES', text_page1, re.DOTALL)
        if conocimientos_match:
            conocimientos_text = conocimientos_match.group(1).strip()
            conocimientos_list = conocimientos_text.split('%')
            conocimientos = []
            for item in conocimientos_list:
                item = item.strip()
                if item:
                    match = re.match(r'(.+)\s*([\d]+)$', item)
                    if match:
                        texto, porcentaje = match.groups()
                        conocimientos.append({'texto': texto.strip(), 'porcentaje': porcentaje.strip()})
                    else:
                        conocimientos.append({'texto': item, 'porcentaje': 'Desconocido'})
            data['conocimientos'] = conocimientos
        else:
            data['conocimientos'] = []

        # Aficiones
        data['aficiones'] = safe_search(r'AFICIONES\s+(.*?)\s+OBJETIVOS PERSONALES', text_page1, default=None)

        # Objetivos Personales
        data['objetivos_personales'] = safe_search(r'OBJETIVOS PERSONALES\s+(.*?)\s+FAMILIA', text_page1, default=None)

        # Datos Familiares
        table_familia = page1.extract_table()
        if table_familia:
            df_familia = pd.DataFrame(table_familia[1:], columns=table_familia[0])
            data['datos_familia'] = df_familia.to_dict(orient="records")
        else:
            data['datos_familia'] = []

        # Page 2 Extraction
        if len(pdf.pages) > 1:
            page2 = pdf.pages[1]
            text_page2 = page2.extract_text()

            # Antecedentes
            antecedentes_keys = ['judicatura1', 'judicatura2', 'buro', 'fiscalia', 'sri', 'base_observados']
            antecedentes_values = re.findall(
                r'JUDICATURA 1\s*([\w\s]+)\s*JUDICATURA 2\s*([\w\s]+)\s*BURÓ\s*([\w\s]+)\s*FISCALÍA\s*([\w\s]+)\s*SRI\s*([\w\s]+)\s*BASE DE OBSERVADOS\s*([\w\s]+)',
                text_page2)

            if antecedentes_values:
                antecedentes_values = antecedentes_values[0]
                data['antecedentes'] = dict(zip(antecedentes_keys, [val.strip() for val in antecedentes_values]))
            else:
                data['antecedentes'] = {}

            # Referencias Laborales
            table_referencias = page2.extract_table()
            if table_referencias:
                df_referencias = pd.DataFrame(table_referencias[1:], columns=table_referencias[0])
                data['referencias_laborales'] = df_referencias.to_dict(orient="records")
            else:
                data['referencias_laborales'] = []

            # Recomendación Contratación
            recommendation_match = re.search(r'RECOMIENDA CONTRATACIÓN:\s*SI\s*(\w+)\s*NO\s*(\w+)', text_page2)
            if recommendation_match:
                data['recomendacion_si'] = True if '☑' in recommendation_match.group(1) else False
                data['recomendacion_no'] = True if '☑' in recommendation_match.group(2) else False
            else:
                data['recomendacion_si'] = False
                data['recomendacion_no'] = False

            # Registro Información SENECYT
            senecyt_match = re.search(r'SENECYT\s*SI\s*(\w+)\s*NO\s*(\w+)', text_page2)
            if senecyt_match:
                data['senecyt_si'] = True if '☑' in senecyt_match.group(1) else False
                data['senecyt_no'] = True if '☑' in senecyt_match.group(2) else False
            else:
                data['senecyt_si'] = False
                data['senecyt_no'] = False

            # Antecedentes penales
            penales_match = re.search(r'ANTECEDENTES PENALES\s*SI\s*(\w+)\s*NO\s*(\w+)', text_page2)
            if penales_match:
                data['penales_si'] = True if '☑' in penales_match.group(1) else False
                data['penales_no'] = True if '☑' in penales_match.group(2) else False
            else:
                data['penales_si'] = False
                data['penales_no'] = False

            # Encontró observaciones
            observaciones_match = re.search(r'SE ENCONTRO OBSERVACIONES:\s*SI\s*(\w+)\s*NO\s*(\w+)', text_page2)
            if observaciones_match:
                data['observaciones_si'] = True if '☑' in observaciones_match.group(1) else False
                data['observaciones_no'] = True if '☑' in observaciones_match.group(2) else False
            else:
                data['observaciones_si'] = False
                data['observaciones_no'] = False

            # Observaciones
            observaciones_text = re.search(r'OBSERVACIONES\s*(.*)\s*ELABORADOR', text_page2, re.DOTALL)
            data['observaciones'] = observaciones_text.group(1).strip() if observaciones_text else ""

            # Elaborador Por, Fecha y Revisado Por
            elaborador_match = re.search(
                r'ELABORADOR POR:\s*([\w\s]+)\s*FECHA:\s*([\d\/\s]+)\s*REVISADO POR:\s*([\w\s]*)', text_page2)
            if elaborador_match:
                data['elaborador'] = elaborador_match.group(1).strip()
                data['fecha_revision'] = elaborador_match.group(2).strip()
                data['revisado'] = elaborador_match.group(3).strip()

    return data