# Backgammon

**Nombre:** Ezequiel Blajevitch

## Requiere:

- Docker instalado y andando

### 1) Construir la imagen del docker:

```bash
docker build -t backgammon .
```

### 2) Inicializar base de datos + server para jugar con la UI

```bash
docker compose up -d
```

### 3) Inicializar desde VS

```bash
# Para solo jugar al de la UI
python -m pygame_ui.ui

# Muestra el CLI y la UI desde la terminal de VS
python -m main
```

### 4) Jugar al CLI desde el docker

```bash
docker run -it backgammon cli
```

### 5) Correr los tests + coverage desde docker

```bash
docker run backgammon test
```
