ComfyArte
ComfyArte es una plataforma web que he desarrollado como parte de mi Trabajo Fin de Grado en Ingeniería Informática en la Universidad Autónoma de Madrid. Su objetivo es facilitar la publicación, gestión y consulta de obras digitales, reuniendo en un mismo entorno a autores y consumidores.

Demostración: https://comfy-arte.vercel.app/

Funcionalidades y guía de uso
Para comenzar, accede a la demostración, selecciona el tipo de cuenta y regístrate o inicia sesión.

Autores: pueden registrarse, publicar obras de distintas categorías (libros, música, vídeo, software, pintura y escultura), seleccionar una licencia Creative Commons y consultar sus publicaciones. Si la moderación automática rechaza una obra, pueden solicitar una revisión manual.
Consumidores: pueden explorar el catálogo, consultar autores, seguirlos, guardar obras y gestionar suscripciones mediante puntos virtuales.
Administración: permite gestionar usuarios, planes de suscripción y solicitudes de revisión de contenidos.
La plataforma incorpora recomendaciones, notificaciones y un sistema de verificación de integridad de archivos mediante SHA-256.

Tecnologías
El backend utiliza Python, Django y Django REST Framework, con una API REST y una base de datos relacional. El frontend está desarrollado con Vue.js, Vite y Pinia. La moderación de contenidos utiliza servicios de OpenAI (gpt-4o-mini y whisper-1 para audio). Se incluyen pruebas con Django y Cypress.

Ejecución local
Se necesitan Python 3.12 o posterior, Node.js y npm. Se recomienda utilizar un entorno virtual de Python.

En una terminal:

git clone https://github.com/vickkky3/comfyArte.git
cd comfyArte/authorship
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
En otra terminal, desde authorship/authorship-frontend:

npm install
npm run dev
Para utilizar la moderación automática, es necesario configurar OPENAI_API_KEY en un archivo .env situado en la raíz del repositorio. El frontend utiliza http://localhost:8000 como dirección del backend por defecto; puede modificarse mediante VITE_API_URL.

Alcance
ComfyArte es un prototipo académico, no un servicio preparado para uso en producción. Las suscripciones utilizan puntos virtuales y no incluyen pagos bancarios. La huella SHA-256 permite comprobar la integridad de un archivo, pero no certifica su autoría. Algunos contenidos se envían a servicios externos para su moderación: no deben utilizarse obras confidenciales sin revisar previamente las condiciones de privacidad y seguridad.

Autora: Victoria Victorero Lomas · Trabajo Fin de Grado, Universidad Autónoma de Madrid (2026).
