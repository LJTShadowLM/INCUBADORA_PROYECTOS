# 🚀 Sistema de Gestión de Incubación de Proyectos Emprendedores

Sistema web desarrollado en Django para la gestión integral de proyectos emprendedores en una incubadora empresarial. Permite la administración de proyectos, sesiones de mentoría, tareas, mensajes internos, Forum de Innovación y banco de problemas tecnológicos.

---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Características Principales](#-características-principales)
3. [Requisitos Previos](#-requisitos-previos)
4. [Instalación](#-instalación)
5. [Configuración](#-configuración)
6. [Ejecución del Proyecto](#-ejecución-del-proyecto)
7. [Acceso al Sistema](#-acceso-al-sistema)
8. [Estructura del Proyecto](#-estructura-del-proyecto)
9. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
10. [Usuarios de Prueba](#-usuarios-de-prueba)
11. [Solución de Problemas](#-solución-de-problemas)
12. [Autor](#-autor)

---

## 📖 Descripción del Proyecto

El **Sistema de Gestión de Incubación de Proyectos Emprendedores** es una plataforma web que facilita la administración y seguimiento de proyectos tecnológicos en proceso de incubación. El sistema gestiona tres roles principales:

- **Administrador**: Gestiona usuarios, asigna gestores a emprendedores, supervisa todos los proyectos.
- **Gestor de Ciencias**: Tutoriza proyectos asignados, agenda sesiones de mentoría, crea tareas, envía mensajes.
- **Emprendedor**: Registra proyectos, solicita sesiones de mentoría, completa tareas, participa en el Forum de Innovación.

El sistema implementa el patrón arquitectónico **Modelo-Template-Vista (MTV)** de Django y utiliza **PostgreSQL** como gestor de base de datos.

---

## ✨ Características Principales

### 🔐 Autenticación y Roles
- Sistema de autenticación basado en Django Auth
- Tres roles diferenciados con permisos específicos
- Paneles personalizados según el rol del usuario
- Registro automático de emprendedores (sin intervención del admin)

### 📊 Gestión de Proyectos
- Registro de proyectos con documentación adjunta
- Estados del proyecto: Pendiente → En Revisión → Aceptado → Asignado → Finalizado
- Asignación de gestores de ciencias a emprendedores
- Filtrado de proyectos por estado
- Barra de progreso visual del proyecto

### 🗓️ Sesiones de Mentoría
- Creación y gestión de sesiones de mentoría
- Sesiones virtuales (con enlace) o presenciales (con dirección)
- Estados: Propuesta → Confirmada → Realizada / Cancelada
- Máximo 1 reprogramación por sesión
- Validación de fechas futuras
- Registro de auditoría (quién, cuándo, qué)
- Subida de archivos adjuntos a sesiones

### ✅ Gestión de Tareas
- Creación automática de tareas al asignar proyecto
- Tareas manuales creadas por gestores
- Marcado de tareas como completadas
- Fechas límite y prioridades

### 💬 Mensajería Interna
- Comunicación entre emprendedores y gestores
- Archivos adjuntos en mensajes
- Notificaciones de mensajes no leídos
- Bandeja de entrada por usuario

### 🎯 Forum de Innovación
- Gestión de convocatorias
- Categorías de participación
- Registro de participantes
- Comisión científica
- Programa de actividades
- Trabajos de innovación
- Resúmenes de ponencias

### 🏦 Banco de Problemas
- Catálogo de problemas tecnológicos
- Filtrado por sector y prioridad
- Soluciones propuestas
- Estado: Abierto / En Proceso / Resuelto

### 🪟 Ventanilla Única Digital
- Solicitudes de trámites
- Gestión de estado de solicitudes
- Notificaciones de respuesta

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

### Software Requerido

| Software | Versión Mínima | Versión Recomendada | Enlace de Descarga |
|----------|----------------|---------------------|---------------------|
| **Python** | 3.10 | 3.11 o 3.12 | [python.org](https://www.python.org/downloads/) |
| **PostgreSQL** | 13 | 15 o 16 | [postgresql.org](https://www.postgresql.org/download/) |
| **Git** | 2.30 | Última versión | [git-scm.com](https://git-scm.com/downloads) |

### Verificar Instalaciones

Abre una terminal (CMD, PowerShell o Git Bash) y ejecuta:

```bash
# Verificar Python
python --version
# Salida esperada: Python 3.11.x o superior

# Verificar pip (gestor de paquetes de Python)
pip --version

# Verificar PostgreSQL
psql --version
# Salida esperada: psql (PostgreSQL) 15.x o superior
```

---

## 📥 Instalación

### Paso 1: Obtener el Proyecto

**Opción A: Clonar el repositorio (si está en Git)**
```bash
git clone https://github.com/tu-usuario/incubadora-proyectos.git
cd incubadora-proyectos
```

**Opción B: Descomprimir el archivo (si recibes un ZIP)**
1. Descomprime el archivo `incubadora-proyectos.zip`
2. Abre una terminal en la carpeta descomprimida

---

### Paso 2: Crear y Activar Entorno Virtual

**En Windows:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verás (venv) al inicio de la línea de comandos
```

**En Linux/macOS:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verás (venv) al inicio de la línea de comandos
```

---

### Paso 3: Instalar Dependencias

Con el entorno virtual activado, instala los paquetes necesarios:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Paquetes principales que se instalarán:**
- Django 5.2.2
- psycopg2-binary (driver PostgreSQL)
- Pillow (manejo de imágenes)
- django-crispy-forms (formularios)
- python-dateutil

---

## ⚙️ Configuración

### Paso 1: Configurar PostgreSQL

#### 1.1 Crear la Base de Datos

**Usando pgAdmin (interfaz gráfica):**
1. Abre **pgAdmin 4**
2. Conecta al servidor PostgreSQL (localhost)
3. Clic derecho en "Databases" → "Create" → "Database"
4. Nombre de la base de datos: `incubadora_db`
5. Owner: `postgres` (o tu usuario)
6. Click en "Save"

**Usando terminal psql:**
```bash
# Conectar a PostgreSQL
psql -U postgres

# Dentro de psql, crear la base de datos
CREATE DATABASE incubadora_db;

# Verificar que se creó
\l

# Salir de psql
\q
```

#### 1.2 Crear Usuario (Opcional pero Recomendado)

Si quieres un usuario específico para el proyecto:

```sql
-- En psql
CREATE USER incubadora_user WITH PASSWORD 'tu_password_seguro';
ALTER ROLE incubadora_user SET client_encoding TO 'utf8';
ALTER ROLE incubadora_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE incubadora_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE incubadora_db TO incubadora_user;
```

---

### Paso 2: Configurar settings.py

Abre el archivo `incubadora/settings.py` y verifica/modifica la configuración de la base de datos:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'incubadora_db',           # Nombre de tu BD
        'USER': 'postgres',                # Tu usuario de PostgreSQL
        'PASSWORD': '5432',                # Tu contraseña (CÁMBIALA)
        'HOST': 'localhost',               # O 127.0.0.1
        'PORT': '5432',                    # Puerto por defecto
    }
}
```

**⚠️ IMPORTANTE:** Cambia la contraseña `'5432'` por la contraseña real de tu usuario PostgreSQL.

#### Otras Configuraciones Importantes

```python
# Seguridad (settings.py)
SECRET_KEY = 'django-insecure--r@f!#q@ww*84eu3-p0!2nn%^w4_a1-=w7b91kysx)3%cdu-g_'
DEBUG = True  # Cambiar a False en producción
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Agregar dominio en producción

# Zona horaria
TIME_ZONE = 'America/Havana'  # O tu zona horaria
USE_TZ = True

# Idioma
LANGUAGE_CODE = 'es-es'

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Configuración de sesiones (30 minutos de inactividad)
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

---

### Paso 3: Crear las Carpetas de Archivos Multimedia

Asegúrate de que existen estas carpetas en la raíz del proyecto:

```bash
mkdir proyectos
mkdir ponencias
mkdir presentaciones
mkdir fichas_tecnicas
mkdir avales
mkdir static
```

**En Windows (CMD):**
```cmd
md proyectos ponencias presentaciones fichas_tecnicas avales static
```

---

### Paso 4: Aplicar Migraciones a la Base de Datos

Las migraciones crean las tablas en PostgreSQL basándose en los modelos de Django:

```bash
# Crear archivos de migración (si no existen)
python manage.py makemigrations

# Aplicar migraciones a la base de datos
python manage.py migrate
```

**Salida esperada:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, emprendedores, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying emprendedores.0001_initial... OK
  ...
```

---

### Paso 5: Crear Superusuario (Administrador)

```bash
python manage.py createsuperuser
```

**Se te pedirá:**
```
Username: admin
Email address: admin@incubadora.cu
Password: ********
Password (again): ********
Superuser created successfully.
```

**⚠️ IMPORTANTE:** Guarda estas credenciales, las necesitarás para acceder al sistema.

---

### Paso 6: Recolectar Archivos Estáticos (Opcional)

Si usas archivos estáticos (CSS, JS, imágenes):

```bash
python manage.py collectstatic
```

---

## ▶️ Ejecución del Proyecto

### Iniciar el Servidor de Desarrollo

Con el entorno virtual activado:

```bash
python manage.py runserver
```

**Salida esperada:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 12, 2026 - 10:30:00
Django version 5.2.2, using settings 'incubadora.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Acceder a la Aplicación

Abre tu navegador web y ve a:

```
http://localhost:8000/
```

o

```
http://127.0.0.1:8000/
```

---

## 🔑 Acceso al Sistema

### Página de Inicio

Al abrir `http://localhost:8000/`, verás la página principal con:
- Descripción de la incubadora
- Botón "Iniciar Sesión"
- Botón "Registrarse como Emprendedor"
- Botón "Ventanilla Única Digital"

### Iniciar Sesión

Click en **"Iniciar Sesión"** y usa las credenciales según tu rol:

#### Como Administrador
```
Usuario: admin
Contraseña: [la que creaste con createsuperuser]
```
→ Te redirigirá a `/panel/admin/`

#### Como Gestor de Ciencias
(Primero debe ser creado por el administrador)
```
Usuario: [username del gestor]
Contraseña: [contraseña asignada]
```
→ Te redirigirá a `/panel/gestor/`

#### Como Emprendedor
(Puede auto-registrarse desde la página principal)
```
Usuario: [username del emprendedor]
Contraseña: [contraseña creada al registrarse]
```
→ Te redirigirá a `/panel/emprendedor/`

---

### Registro de Nuevo Emprendedor

1. Desde la página principal, click en **"Regístrate como emprendedor"**
2. Completa el formulario:
   - Username (único)
   - Email
   - Nombre completo
   - Contraseña (mínimo 12 caracteres)
   - Confirmar contraseña
3. Click en "Registrarse"
4. Inicia sesión con tus credenciales

---

## 📁 Estructura del Proyecto

```
incubadora/
│
├── 📂 emprendedores/              # Aplicación principal
│   ├── 📂 migrations/             # Migraciones de BD
│   ├── 📂 templates/              # Plantillas HTML
│   │   └── emprendedores/
│   │       ├── base.html          # Template base
│   │       ├── login.html         # Página de login
│   │       ├── admin.html         # Panel administrador
│   │       ├── gestor.html        # Panel gestor
│   │       ├── emprendedor.html   # Panel emprendedor
│   │       └── ...
│   ├── admin.py                   # Configuración admin Django
│   ├── apps.py                    # Configuración app
│   ├── forms.py                   # Formularios y validaciones
│   ├── models.py                  # Modelos de datos (13 clases)
│   ├── urls.py                    # Rutas de la app (120+ URLs)
│   ├── views.py                   # Lógica de negocio (100+ funciones)
│   └── enviar_recordatorio.py     # Script de notificaciones
│
├── 📂 incubadora/                 # Configuración del proyecto
│   ├── settings.py                # Configuración principal ⚙️
│   ├── urls.py                    # Rutas principales
│   ├── wsgi.py                    # Punto de entrada WSGI
│   └── asgi.py                    # Punto de entrada ASGI
│
├── 📂 static/                     # Archivos estáticos
│   ├── css/
│   │   ├── desoft-theme.css       # Tema corporativo DESOFT
│   │   └── custom.css
│   ├── js/
│   └── images/
│
├── 📂 proyectos/                  # Documentos de proyectos
├── 📂 ponencias/                  # Archivos de ponencias
├── 📂 presentaciones/             # Presentaciones
├── 📂 fichas_tecnicas/            # Fichas técnicas
├── 📂 avales/                     # Documentos de avales
│
├── manage.py                      # Script principal Django
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.2** - Framework web Python
- **PostgreSQL 15+** - Sistema de gestión de base de datos
- **Python 3.11+** - Lenguaje de programación

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (tema corporativo DESOFT)
- **Bootstrap 5.3** - Framework CSS responsivo
- **Bootstrap Icons** - Iconografía
- **JavaScript (Vanilla)** - Interactividad del cliente

### Librerías Python
- **psycopg2-binary** - Adaptador PostgreSQL
- **Pillow** - Procesamiento de imágenes
- **django-crispy-forms** - Renderizado de formularios
- **python-dateutil** - Manejo de fechas

### Patrón Arquitectónico
- **MTV (Modelo-Template-Vista)** - Patrón de Django
- **ORM de Django** - Mapeo objeto-relacional
- **Sistema de autenticación de Django** - Gestión de usuarios

---

## 👥 Usuarios de Prueba

### Administrador
```
Username: admin
Password: admin12345678
```
**Permisos:**
- Gestionar todos los proyectos
- Crear/editar/eliminar gestores
- Asignar gestores a emprendedores
- Ver estadísticas globales
- Gestionar Forum de Innovación
- Administrar banco de problemas

### Gestor de Ciencias (Ejemplo)
```
Username: gestor_prueba
Password: gestor123456
```
**Permisos:**
- Ver proyectos asignados
- Agendar sesiones de mentoría
- Crear tareas para emprendedores
- Enviar mensajes a emprendedores
- Cambiar estado de proyectos

### Emprendedor (Ejemplo)
```
Username: emprendedor_test
Password: emprendedor123
```
**Permisos:**
- Registrar proyectos
- Solicitar sesiones de mentoría
- Ver/completar tareas asignadas
- Enviar mensajes a su gestor
- Participar en Forum de Innovación
- Consultar banco de problemas

**Nota:** Estos usuarios deben ser creados manualmente desde el panel de administrador o mediante el registro de emprendedores.

---

## 🚨 Solución de Problemas

### Error: "No module named 'psycopg2'"
**Solución:**
```bash
pip install psycopg2-binary
```

---

### Error: "FATAL: password authentication failed for user 'postgres'"
**Solución:**
1. Verifica la contraseña en `settings.py`
2. Asegúrate de que PostgreSQL esté en ejecución
3. Verifica el usuario y contraseña en pgAdmin

---

### Error: "django.db.utils.OperationalError: could not connect to server"
**Solución:**
1. Inicia el servicio de PostgreSQL:
   - Windows: Servicios → PostgreSQL → Iniciar
   - Linux: `sudo systemctl start postgresql`
2. Verifica que el puerto 5432 esté disponible

---

### Error: "Port 8000 is already in use"
**Solución:**
```bash
# Usa un puerto diferente
python manage.py runserver 8080

# O encuentra y mata el proceso en el puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID [número_del_proceso] /F

# Linux:
lsof -i :8000
kill -9 [PID]
```

---

### Error: "Template does not exist"
**Solución:**
1. Verifica que la carpeta `templates` exista en `emprendedores/`
2. Verifica la configuración en `settings.py`:
```python
TEMPLATES = [
    {
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        ...
    },
]
```

---

### Error: "Static files not loading"
**Solución:**
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Verificar configuración en settings.py
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

---

### Las sesiones se quedan abiertas indefinidamente
**Solución:**
Agrega en `settings.py`:
```python
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

---

### Error: "CSRF verification failed"
**Solución:**
Asegúrate de incluir `{% csrf_token %}` en todos los formularios HTML:
```html
<form method="post">
    {% csrf_token %}
    ...
</form>
```

---

## 📚 Documentación Adicional

### Comandos Útiles de Django

```bash
# Ver todas las rutas disponibles
python manage.py show_urls

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Abrir shell interactivo de Django
python manage.py shell

# Ejecutar pruebas
python manage.py test

# Limpiar sesiones expiradas
python manage.py clearsessions

# Ver versión de Django
python manage.py version
```

### Acceso al Admin de Django

Aunque el sistema usa paneles personalizados, el admin de Django sigue disponible:

```
http://localhost:8000/admin/
```

Login con las credenciales del superusuario.

---

## 🔒 Consideraciones de Seguridad

### Para Desarrollo
- ✅ `DEBUG = True` está bien
- ✅ `SECRET_KEY` simple está bien
- ✅ `ALLOWED_HOSTS = []` está bien

### Para Producción (IMPORTANTE)
- ⚠️ Cambiar `DEBUG = False`
- ⚠️ Generar nueva `SECRET_KEY` segura
- ⚠️ Agregar dominio a `ALLOWED_HOSTS`
- ⚠️ Configurar `SECURE_SSL_REDIRECT = True`
- ⚠️ Usar servidor WSGI (Gunicorn/Waitress)
- ⚠️ Configurar servidor web (Nginx/Apache)
- ⚠️ Cambiar contraseñas por defecto
- ⚠️ Configurar backups de BD

---

## 📞 Soporte y Contacto

**Desarrollador:** [Tu Nombre]  
**Email:** [tu_email@ejemplo.com]  
**Universidad:** [Nombre de tu Universidad]  
**Proyecto:** Trabajo de Diploma - Ingeniería en Ciencias Informáticas  
**Año:** 2026  

---

## 📄 Licencia

Este proyecto fue desarrollado como Trabajo de Diploma para [Nombre de tu Universidad]. 

---

## 🙏 Agradecimientos

- A DESOFT por proporcionar el contexto y requerimientos del sistema
- A los tutores y profesores por su guía durante el desarrollo
- A la comunidad de Django por la documentación y recursos

---

## 📝 Notas Finales

- Este es un entorno de **desarrollo**. Para producción, sigue las consideraciones de seguridad.
- Realiza backups regulares de la base de datos.
- Mantén actualizadas las dependencias: `pip list --outdated`
- Consulta la documentación oficial de Django: https://docs.djangoproject.com/

---

**¡El sistema está listo para usar! 🚀**

Si encuentras algún problema, revisa la sección de Solución de Problemas o contacta al desarrollador.LJ