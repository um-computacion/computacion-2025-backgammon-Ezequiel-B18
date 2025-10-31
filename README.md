# Backgammon

**Nombre:** Ezequiel Blajevitch

## Requiere:

- Docker instalado y andando

### 1) Construir la imagen del docker:

```bash
docker build -t backgammon .
```

### 2) Inicializar base de datos para jugar con la UI (Redis)

```bash
docker compose up -d
```

Esto levanta **Redis** - una base de datos en memoria para persistir el estado del juego.
La UI de Pygame se conecta directamente a Redis (sin servidor Flask intermediario).

### 3) Instalar las librerías y dependencias (hacer en entorno virtual)

```bash
pip install -r requirements.txt
```

### 4) Inicializar desde VS

```bash
# Para jugar con la UI (requiere que docker compose esté corriendo)
python -m pygame_ui.ui

# Para jugar con CLI (no requiere servidor, funciona standalone)
python -m cli.cli

# Muestra menú para elegir entre CLI o UI
python -m main
```

### 5) Jugar al CLI desde el docker

```bash
docker run -it backgammon cli
```

### 6) Correr los tests + coverage desde docker

```bash
docker run backgammon test
```
