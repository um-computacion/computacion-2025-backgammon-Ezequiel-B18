# Justificaciones por fichero

## core/board.py

La responsabilidad del tablero se ha unificado: Board es la única fuente de verdad (SSoT) para puntos, barra y home. Se añadió `setup_starting_positions()` para inicializar la disposición estándar y `move_checker` devuelve eventos estructurados.

## core/checker.py

Checker mantiene la lógica propia de una ficha: estado, posición, validaciones y reglas elementales.

## core/dice.py

Dice gestiona la aleatoriedad y la semántica de la tirada (dobles, tirada inicial). Es para centralizar la lógica de dados para poder mockearla en tests y evitar mezclarla con reglas de movimiento.

## core/player.py

Player gestiona identidad, colección de checkers y estado del turno (is_turn, remaining_moves). `distribute_checkers` ahora sólo asigna posiciones a objetos Checker, no modifica el tablero.

## core/game.py

Game actúa como orquestador: inicializa Board/Dice/Player, ejecuta tiradas iniciales, arranca turnos, aplica movimientos y sincroniza los objetos Checker con el Board (sync_checkers).

## .github/workflows/ci.yml

Workflow actualizado para descubrir tests en `tests/` y ejecutar pylint sobre todos los archivos `.py`. Esto es para tener el CI y cumplir la consigna, es lo que nos genera los reportes de coverage y pylint en el repo.

## CHANGELOG.md

Se registraron los cambios principales para mantener trazabilidad. Esto es para tener una comunicación clara del historial de cambios y decisiones de diseño.

## prompts/prompts-desarrollo.md, prompts/prompts-testing.md, prompts/prompts-documentacion.md

Se usan para documentar prompts y decisiones de desarrollo/ pruebas/ documentación según la política del proyecto. Motivo: centralizar el historial de prompts y respuestas para trazabilidad y cumplimiento de TDD/SOLID en el proceso.
