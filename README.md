## Ejecución del proyecto localmente y ambiente de desarrollo

### Requerimientos

- Python 3.8+
- Pip

### Instalación

```bash
# Crear un entorno virtual
virtualenv -p python3 venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución local

```bash
python app.py
```

Por defecto, la aplicación se ejecuta en `http://localhost:5000`

## Formato de código

Para formatear el código, se utiliza el linter `black`. Para instalarlo, instalar el requirements.txt o ejecutar:

```bash
pip install black
```

Luego, se puede formatear el código con el siguiente comando:

```bash
black .
```

## Formato automático:

Commits:

```bash
pre-commit install
```

VS Code tiene integrado el formateador `black` y se puede configurar en el archivo `.vscode/settings.json` usando la extensión `ms-python.black-formatter`.

## Commits

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
