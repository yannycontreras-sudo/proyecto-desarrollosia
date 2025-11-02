# [Nombre de tu Proyecto, ej: Sistema de Gestión para estudiantes de kinesiología UCN]


## 📝 Descripción Breve

Este El proyecto es un sistema que busca funcionar como un Laboratorio Virtual de Casos Clínicos. Permite que los estudiantes de Kinesiología interactúen con material didáctico audiovisual (videos de casos y diagnósticos) de forma asincrónica. De esta manera, pueden practicar el razonamiento clínico, proponer planes de tratamiento y realizar ejercicios de entrevista, fortaleciendo sus habilidades antes de pasar a la práctica clínica real. Desarrollado en **Django**


##  Integrantes del Equipo

| Nombre del Integrante | Rol en el Proyecto | Usuario de GitHub |
| :--- | :--- | :--- |
| [Yanny Contreras] | Desarrollador Backend / Database Admin | @[yanny.contreras@alumnos.ucn.cl] |
| [Yanny Contreras] | Desarrollador Frontend / UI/UX | @[yanny.contreras@alumnos.ucn.cl] |
| [Yanny Contreras] | Documentación / Testing | @[yanny.contreras@alumnos.ucn.cl] |


---

## Guía de Instalación y Ejecución

Sigue estos pasos para configurar y ejecutar la aplicación en un entorno local:

### 1. Requisitos Previos

* **Python** (Versión recomendada, ej: 3.10 o superior)
* **PostgreSQL** (Servidor de base de datos)
* **Git**

### 2. Clonar el Repositorio

Abre tu terminal y clona el proyecto:

```bash
git clone [https://www.youtube.com/watch?v=eQMcIGVc8N0](https://www.youtube.com/watch?v=eQMcIGVc8N0)
cd proyecto-desarrolloia

3. Configuración del Entorno Virtual
Crea y activa un entorno virtual (esto asegura que las dependencias del proyecto no interfieran con tu sistema global):

Bash

# Crear entorno virtual (ej: 'entornoP')
python -m venv entornoP

# Activar en Windows (Símbolo del Sistema / PowerShell)
.\entornoP\Scripts\activate

# Activar en Linux/macOS
source entornoP/bin/activate

4. Instalar Dependencias
Instala todas las librerías de Python necesarias usando el archivo requirements.txt:

Bash

pip install -r requirements.txt

5. Configuración de la Base de Datos
Antes de continuar, configura una base de datos PostgreSQL según los parámetros indicados en la sección "Conexión a la Base de Datos" a continuación.

6. Migraciones y Superusuario
Aplica las migraciones de la base de datos para crear las tablas definidas por los modelos de Django, y luego crea un superusuario para acceder al panel de administración:

Bash

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

7. Ejecutar el Servidor
Inicia el servidor de desarrollo de Django:

Bash

python manage.py runserver

Conexión a la Base de Datos
El proyecto está configurado para conectarse a una base de datos PostgreSQL.

Para la ejecución local, el archivo settings.py espera la siguiente configuración de ejemplo. Por favor, reemplaza estos valores de ejemplo con los que hayas configurado en tu servidor PostgreSQL local:

ENGINE: django.db.backends.postgresql

NAME: db_kinesiologia (Ej)

USER: [Usuario_Ejemplo] (Ej: postgres)

PASSWORD: [Contraseña_Ejemplo]

HOST: 127.0.0.1 (o localhost)

PORT: 5432 (Puerto por defecto de PostgreSQL)

Las credenciales reales sensibles NO han sido expuestas en el código ni en este archivo por motivos de seguridad.