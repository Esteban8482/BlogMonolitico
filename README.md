# Ejecución del proyecto localmente y ambiente de desarrollo

## Requerimientos

- Python 3.8+
- Pip

### Instalación y configuración manual

```bash
# Crear un entorno virtual
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

# Ejecución local

### Credenciales Firestore

Para ejecutar la aplicación localmente, se deben proporcionar las credenciales en formato json de Firestore. Estas credenciales se pueden obtener de la consola de Firebase.

```
# en /microservices/user/.env
FIREBASE_ADMIN_CREDENTIALS="ruta/al/credenciales.json"

# en /microservices/post/.env
FIREBASE_ADMIN_CREDENTIALS_POSTS="ruta/al/credenciales.json"
```

## Ejecución de la aplicación

```bash
python app.py
```

Por defecto, la aplicación se ejecuta en `http://localhost:5000`

## Ejecución micro-servicio

### Usuario

```bash
cd microservices/user
python app.py
```

Puerto por defecto: `5002`

### Post

```bash
cd microservices/post
python app.py
```

Puerto por defecto: `5003`

## Comentarios

```bash
cd microservices/comment
python app.py
```

Puerto por defecto: `8091`

## Tests

```bash
pip install pytest
pytest
```

## Formato de código (opcional)

Para formatear el código, se utiliza el linter `black`:

```bash
pip install black
```

Luego, se puede formatear el código con el siguiente comando:

```bash
black .
```

### Extensiones recomendadas

- [Black](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)

## prettier (opcional) para formato automático de CSS y JS

### Extensiones recomendadas

- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)

## Formato automático (opcional):

Commits:

```bash
pip install pre-commit
pre-commit install
```

VS Code tiene integrado el formateador `black` y se puede configurar en el archivo `.vscode/settings.json` usando la extensión `ms-python.black-formatter`.

## Commits (opcional)

Para crear un commit, se debe seguir el siguiente formato:

```
<tipo de cambio>: <descripción del cambio>

<descripción del cambio en más líneas>
```

Los tipos de cambio pueden ser:

- `feat`: nueva funcionalidad
- `fix`: corrección de un error
- `docs`: cambios en la documentación
- `style`: cambios en el formato de código
- `refactor`: cambios en el código que no afectan a la funcionalidad
- `test`: cambios en los tests
- `chore`: cambios en la configuración de la aplicación

Por ejemplo:

```
feat: agregar funcionalidad para crear nuevas publicaciones
```
