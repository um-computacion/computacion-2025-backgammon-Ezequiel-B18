# Backgammon

**Nombre:** Ezequiel Blajevitch

## Command to run coverage and generate the report

---

coverage run -m unittest discover tests && coverage report -m && coverage xml

Docker solo corre los tests y el CLI, Pygame UI no se puede usar con docker.

Crear imagen del docker
docker build -t backgammon .

Tests
docker run backgammon

CLI
docker run -it backgammon cli

---

Jugar con el CLI o Pygame UI
python main.py

---