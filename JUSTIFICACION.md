# Justificación del Proyecto Backgammon

**Alumno:** Ezequiel Blajevitch  
**Fecha:** Octubre 2025  
**Repositorio:** computacion-2025-backgammon-Ezequiel-B18

---

## Tabla de Contenidos

1. [Resumen del Diseño General](#resumen-del-diseño-general)
2. [Arquitectura y Principios SOLID](#arquitectura-y-principios-solid)
3. [Módulo Core - Lógica de Negocio](#módulo-core---lógica-de-negocio)
4. [Interfaces de Usuario](#interfaces-de-usuario)
5. [Sistema de Excepciones](#sistema-de-excepciones)

---

## Resumen del Diseño General

El proyecto implementa el juego de Backgammon siguiendo una arquitectura de capas que separa completamente la lógica de negocio de las interfaces de usuario. Esta separación permite:

- **Reutilización:** La misma lógica sirve para CLI y Pygame UI
- **Testabilidad:** El core puede ser testeado independientemente de la UI
- **Mantenibilidad:** Los cambios en las reglas no afectan las interfaces
- **Extensibilidad:** Agregar nuevas interfaces (web, mobile) es directo

### Estructura del Proyecto

```
backgammon/
├── core/              # Lógica de negocio (SOLID, independiente)
│   ├── game.py        # Orquestador principal
│   ├── board.py       # Estado del tablero (SSoT)
│   ├── dice.py        # Generación y gestión de dados
│   ├── player.py      # Estado y acciones del jugador
│   ├── checker.py     # Representación de fichas
│   └── exceptions.py  # Jerarquía de excepciones custom
├── cli/               # Interfaz de línea de comandos
│   └── cli.py         # BackgammonCLI
├── pygame_ui/         # Interfaz gráfica con Pygame
│   └── ui.py          # BackgammonUI
└── tests/             # Suite de pruebas (95% coverage)
    ├── tests_game.py
    ├── tests_board.py
    ├── tests_dice.py
    ├── tests_player.py
    ├── tests_checker.py
    └── tests_cli.py
```

---

## Arquitectura y Principios SOLID

### Single Responsibility Principle (SRP)

Cada clase tiene una única razón para cambiar:

- **Board:** Gestiona el estado físico del tablero
- **Dice:** Genera números aleatorios y determina movimientos
- **Player:** Maneja identidad y turnos del jugador
- **Checker:** Representa una ficha individual
- **Game:** Orquesta el flujo del juego
- **CLI/UI:** Presentan la información y capturan input

### Open/Closed Principle (OCP)

- Las clases core están abiertas a extensión (herencia, composición) pero cerradas a modificación
- Ejemplo: Se pueden agregar nuevos tipos de excepciones sin modificar `BackgammonError`
- Las interfaces (CLI, Pygame) se pueden extender sin tocar el core

### Liskov Substitution Principle (LSP)

- Todas las excepciones custom heredan de `BackgammonError` y son intercambiables
- Los `CheckerColor` y `CheckerState` enums son substituibles donde se espera un enum

### Interface Segregation Principle (ISP)

- Los métodos públicos de cada clase son cohesivos y focalizados
- No hay métodos "gordos" que fuercen a los clientes a depender de funcionalidad no usada
- Ejemplo: `Board` expone métodos específicos (`move_checker`, `bear_off`, `enter_from_bar`) en vez de un método genérico `do_action`

### Dependency Inversion Principle (DIP)

- `Game` acepta inyección de dependencias (Board, Dice, Player) en el constructor
- Esto permite testing con mocks sin modificar el código de producción
- Las interfaces dependen de abstracciones (Game) no de implementaciones concretas

---

## Módulo Core - Lógica de Negocio

### core/board.py - Clase Board

**Propósito:** Mantiene la posición de todas las fichas, gestiona la barra y las fichas que han salido del tablero.

#### Atributos

- `__points__`: Lista de 24 tuplas `(player, count)` representando cada punto del tablero

  - `player`: 0 (vacío), 1 (blanco), 2 (negro)
  - `count`: número de fichas en ese punto
  - **Decisión:** Tuplas inmutables previenen modificaciones accidentales; se reemplaza toda la tupla al actualizar

- `__bar__`: Dict `{1: count, 2: count}` de fichas en la barra por jugador

  - **Decisión:** Dict permite acceso O(1) por player_id

- `__home__`: Dict `{1: count, 2: count}` de fichas sacadas del tablero
  - **Decisión:** Separar bar/home facilita validaciones

#### Métodos

##### `__init__(self, test_bearing_off=False)`

- Inicializa el tablero vacío o con posición de test
- **Parámetro test_bearing_off:** Permite testing de bearing off sin jugar partida completa
- **Decisión:** Constructor con parámetro opcional es más simple que factory methods

##### `setup_starting_positions(self)`

- Configura la disposición estándar de backgammon:
  - Blanco (player 1): puntos 23(2), 12(5), 7(3), 5(5)
  - Negro (player 2): puntos 0(2), 11(5), 16(3), 18(5)
- **Decisión:** Método separado, no en el constructor que permite resetear tablero sin crear nueva instancia

##### `is_valid_move(self, player, from_point, to_point) -> bool`

- Valida si un movimiento es legal según reglas de backgammon:
  1. Rangos de puntos válidos (0-23)
  2. No hay fichas en la barra (deben entrar primero)
  3. El punto origen tiene fichas del jugador
  4. Dirección correcta (blanco: 23→0, negro: 0→23)
  5. Punto destino no bloqueado (≥2 fichas oponente)
- **Retorna:** `True` si válido, `False` si inválido
- **Excepciones:** `InvalidPointError` si los índices estan fuera de rango
- **Decisión:** Validación centralizada evita código duplicado en Game/Player

##### `move_checker(self, player, from_point, to_point) -> dict`

- Ejecuta un movimiento y retorna evento estructurado:
  ```python
  {
      'moved': bool,      # Si se movió exitosamente
      'hit': bool,        # Si se capturó ficha enemiga
      'hit_player': int,  # Jugador capturado (None si no hit)
      'borne_off': bool   # Si se sacó del tablero
  }
  ```
- **Lógica:**
  1. Valida el movimiento
  2. Remueve ficha del origen
  3. Si destino tiene 1 ficha enemiga → captura (hit) y envía a barra
  4. Añade ficha al destino
- **Decisión:** Retornar dict en vez de múltiples bools permite extensión futura sin cambiar firma

##### `enter_from_bar(self, player, point) -> bool`

- Permite entrada desde la barra al tablero:
  - Blanco entra en puntos 18-23 (cuarto cuadrante del oponente)
  - Negro entra en puntos 0-5 (primer cuadrante del oponente)
- **Valida:** Punto no bloqueado (< 2 fichas enemigas)
- **Maneja:** Capturas si hay 1 ficha enemiga (blot)
- **Retorna:** `True` si exitoso, `False` si inválido
- **Decisión:** Entrada desde barra es suficientemente distinta a movimiento normal para merecer método propio

##### `all_checkers_in_home_board(self, player) -> bool`

- Verifica si todas las fichas del jugador están en su home board:
  - Blanco: puntos 0-5
  - Negro: puntos 18-23
- **Uso:** Prerequisito para bearing off
- **Decisión:** Query method separado mejora legibilidad en `bear_off` y `Game.get_valid_moves`

##### `bear_off(self, player, point) -> bool`

- Saca una ficha del tablero (bearing off):
  1. Valida punto en home board
  2. Verifica que todas las fichas estén en home
  3. Confirma ficha del jugador en ese punto
  4. Remueve del tablero y añade a `home`
- **Retorna:** `True` si exitoso, `False` si inválido
- **Decisión:** Validaciones dentro del método aseguran invariantes del juego

##### `check_winner(self) -> int`

- Determina si hay ganador:
  - Retorna `1` si blanco ganó (15 fichas en home)
  - Retorna `2` si negro ganó (15 fichas en home)
  - Retorna `0` si no hay ganador
- **Decisión:** Retornar int en vez de bool/None permite discriminar ganador en un solo call

---

### core/dice.py - Clase Dice

**Propósito:** Encapsula toda la lógica de dados: generación aleatoria, detección de dobles, y tirada inicial para determinar quién empieza.

#### Atributos

- `__values__`: Lista `[die1, die2]` con valores actuales (0,0 = no tirados)
- `initial_values`: Lista `[player1_roll, player2_roll]` para tirada inicial

#### Métodos

##### `roll(self) -> list`

- Tira ambos dados (random 1-6)
- Valida que valores estén en rango
- **Retorna:** Lista `[valor1, valor2]`
- **Excepciones:** `InvalidDiceValueError` si random falla
- **Decisión:** Validación post-random detecta bugs en `random.randint`

##### `is_doubles(self) -> bool`

- Verifica si ambos dados muestran el mismo valor
- **Uso:** En backgammon, dobles permiten 4 movimientos
- **Decisión:** Property dedicado mejora legibilidad vs comparación inline

##### `get_moves(self) -> list`

- Retorna lista de movimientos disponibles:
  - Dobles: `[valor] * 4` (ej: `[3,3,3,3]`)
  - Normal: `[valor1, valor2]`
- **Uso:** Player usa esto para `available_moves`
- **Decisión:** Generar lista completa para dobles simplifica lógica de consumo en Player

##### `initial_roll(self) -> tuple`

- Tira un dado por jugador para determinar quién empieza
- **Retorna:** `(roll1, roll2)`
- **Decisión:** Tuple inmutable evita modificaciones accidentales

##### `get_highest_roller(self) -> int`

- Determina ganador de tirada inicial:
  - `1` si player1 > player2
  - `2` si player2 > player1
  - `0` si empate
- **Decisión:** Método separado de `initial_roll` permite re-query sin re-tirar

---

### core/checker.py - Clase Checker

**Propósito:** Representa una ficha individual con su color, estado y posición. Maneja lógica de movimiento específica de la ficha.

#### Enums

##### `CheckerColor`

- `WHITE`: Fichas blancas (player 1)
- `BLACK`: Fichas negras (player 2)
- **Decisión:** Enum vs strings previene typos y permite type checking

##### `CheckerState`

- `ON_BOARD`: Ficha en el tablero
- `ON_BAR`: Ficha capturada (en barra)
- `BORNE_OFF`: Ficha sacada del juego
- **Decisión:** Estados explícitos evitan inferir estado de `position is None`

#### Atributos

- `color`: CheckerColor (inmutable después de construcción)
- `state`: CheckerState (mutable según acciones)
- `__position__`: int o None (0-23 cuando ON_BOARD)

#### Métodos

##### `set_position(self, position)`

- Establece posición inicial en el tablero
- Valida rango 0-23
- Setea estado a `ON_BOARD`
- **Uso:** Durante setup inicial del juego
- **Excepciones:** `InvalidCheckerPositionError` si fuera de rango

##### `move_to_position(self, new_position)`

- Mueve ficha a nueva posición en tablero
- Similar a `set_position` pero es un "movimiento" despues del inicio
- **Decisión:** Métodos separados clarifican intención (setup vs move)

##### `calculate_new_position(self, dice_value) -> int`

- Calcula posición destino basado en color y valor de dado:
  - Blanco: `position + dice_value` (mueve hacia números altos)
  - Negro: `position - dice_value` (mueve hacia números bajos)
- **Retorna:** Posición calculada (puede estar fuera de rango 0-23)
- **Uso:** Helper para validar si movimiento es posible
- **Excepciones:** ValueError si no ON_BOARD o position None

##### `send_to_bar(self)`

- Marca ficha como capturada:
  - Estado → `ON_BAR`
  - Posición → `None`
- **Decisión:** Método dedicado para claridad vs setear atributos manualmente

##### `enter_from_bar(self, position) -> bool`

- Reingresa ficha desde barra a posición específica:
  - Blanco: debe entrar en 0-5
  - Negro: debe entrar en 18-23
- Valida rangos según color
- **Retorna:** `True` si exitoso, `False` si inválido
- **Decisión:** Validación en Checker asegura consistencia con reglas de entrada

##### `bear_off(self)`

- Saca ficha del tablero a nivel de **objeto individual**:
  - Valida estado ON_BOARD
  - Valida posición en home board
  - Estado → `BORNE_OFF`
  - Posición → `None`
- **Excepciones:** ValueError si estado inválido o no en home
- **Ámbito:** Operación a nivel de Checker individual
- **Uso real:** Solo en tests unitarios para configurar escenarios
- **NO usado en producción:** El flujo del juego usa `Board.bear_off()` + `Game.sync_checkers()`

**⚠️ IMPORTANTE - Diferencia con Board.bear_off():**

Existen **dos métodos `bear_off`** que operan a diferentes niveles de abstracción:

| Aspecto                 | `Checker.bear_off()`                     | `Board.bear_off(player, point)`       |
| ----------------------- | ---------------------------------------- | ------------------------------------- |
| **Nivel**               | Objeto individual (micro)                | Estado del tablero (macro)            |
| **Conocimiento**        | Solo esta ficha                          | Toda la partida                       |
| **Valida**              | Estado de 1 checker                      | Reglas globales del juego             |
| **Actualiza**           | `checker.state` y `checker.__position__` | `board.__points__` y `board.__home__` |
| **Usado en producción** | ❌ No                                    | ✅ Sí (`Game.apply_bear_off_move`)    |
| **Usado en tests**      | ✅ Sí (setup de escenarios)              | ✅ Sí                                 |

**Justificación de mantener ambos:**

1. **Separación de responsabilidades:** Checker gestiona su propio estado; Board gestiona el tablero completo
2. **Testing:** `Checker.bear_off()` permite tests unitarios sin crear Board/Game completo
3. **API completa:** Checker tiene una interfaz completa para todas sus transiciones de estado
4. **Patrón SSoT:** Board es la fuente de verdad; después de `Board.bear_off()`, `Game.sync_checkers()` actualiza todos los Checker objects automáticamente

**Flujo de producción:**

```python
# Usuario intenta bearing off
Game.apply_bear_off_move(from_point=2)
  → Board.bear_off(player=1, point=2)  # ← Actualiza board.__home__ y board.__points__
  → Game.sync_checkers()                # ← Recorre todos los checkers y setea estados según Board
     → Para cada checker:
        if en board.home: checker.state = BORNE_OFF
```

**Conclusión:** `Checker.bear_off()` existe por completitud de API y testing, pero el juego real usa `Board.bear_off()` como fuente autoritativa, manteniendo el patrón "Board as Single Source of Truth".

##### `is_in_home_board(self) -> bool`

- Verifica si ficha está en su home board:
  - Blanco: 18-23
  - Negro: 0-5
- **Uso:** Prerequisito para `bear_off`

##### `can_bear_off_with_value(self, dice_value) -> bool`

- Verifica si ficha puede sacarse con un dado específico
- Calcula distancia requerida y compara con dice_value
- **Uso:** Validación en Game antes de llamar `bear_off`

---

### core/player.py - Clase Player

**Propósito:** Representa un jugador con su identidad, colección de fichas, y gestión de turnos/movimientos disponibles.

#### Enum

##### `PlayerColor`

- `WHITE` / `BLACK`: Colores del jugador
- **Decisión:** Enum separado de CheckerColor permite futura extensión (ej: equipos)

#### Atributos

- `name`: str - Nombre del jugador
- `color`: PlayerColor - Color asignado
- `player_id`: int - 1 (blanco) o 2 (negro) para interacción con Board
- `__checkers__`: Lista de 15 objetos Checker
- `is_turn`: bool - Si es el turno actual del jugador
- `remaining_moves`: int - Movimientos restantes en el turno
- `available_moves`: list - Valores de dados disponibles para usar

#### Métodos

##### `get_starting_positions(self) -> list`

- Retorna tuplas `[(point, count), ...]` con posiciones iniciales:
  - Blanco: `[(23,2), (12,5), (7,3), (5,5)]`
  - Negro: `[(0,2), (11,5), (16,3), (18,5)]`
- **Decisión:** Método dedicado permite testing y reuso

##### `distribute_checkers(self, board)`

- Asigna posiciones iniciales a los objetos Checker del jugador
- **Importante:** NO modifica `board.points` (eso es responsabilidad de Board)
- **Decisión:** Versión anterior violaba SRP; ahora solo configura Checkers

##### `start_turn(self, dice)`

- Inicia turno del jugador:
  1. `is_turn = True`
  2. `available_moves = dice.get_moves()`
  3. `remaining_moves = len(available_moves)`
- **Uso:** Llamado por Game después de tirar dados
- **Decisión:** Recibir Dice permite mockear en tests

##### `end_turn(self)`

- Finaliza turno:
  - `is_turn = False`
  - `remaining_moves = 0`
  - `available_moves = []`
- **Decisión:** Método explícito vs setear atributos mejora trazabilidad

##### `can_use_dice_for_move(self, move_distance) -> bool`

- Verifica si un movimiento de X espacios es posible con dados disponibles:
  1. Chequea valor exacto en `available_moves`
  2. Chequea combinaciones de 2 dados (ej: 1+2=3)
  3. Chequea combinaciones de 3 dados (solo dobles)
  4. Chequea combinación de 4 dados (solo dobles)
- **Retorna:** `True` si movimiento es factible
- **Decisión:** Lógica compleja pero necesaria para dobles; centralizada aquí vs duplicar en Game

##### `use_dice_for_move(self, move_distance) -> bool`

- Consume dados necesarios para un movimiento:
  - Remueve valores exactos de `available_moves`
  - Decrementa `remaining_moves`
- **Algoritmo:** Igual que `can_use_dice_for_move` pero muta lista
- **Retorna:** `True` si exitoso, `False` si falla
- **Decisión:** Método separado de validación permite dry-run antes de commit

##### `get_checkers_by_state(self, state) -> list`

- Filtra checkers por estado (ON_BOARD, ON_BAR, BORNE_OFF)
- **Uso:** Queries en tests y debugging
- **Decisión:** Helper method reduce código repetitivo

##### `count_checkers_by_state(self, state) -> int`

- Cuenta checkers en un estado específico
- **Equivalente a:** `len(get_checkers_by_state(state))`
- **Decisión:** Conveniencia para asserts y condiciones

##### `has_won(self) -> bool`

- Verifica victoria: 15 fichas en BORNE_OFF
- **Uso:** Condición de fin de juego
- **Decisión:** Delegado a Player permite lógica de victoria customizable

---

### core/game.py - Clase Game

**Propósito:** Orquestador principal. Coordina Board, Dice, Players y ejecuta el flujo del juego. No contiene reglas de movimiento (delegadas a Board/Player/Checker).

#### Atributos

- `__board__`: Instancia de Board
- `__dice__`: Instancia de Dice
- `__player1__` / `__player2__`: Instancias de Player
- `current_player` / `other_player`: Referencias al jugador activo
- `__game_initialized__`: bool - Verifica setup completo
- `turn_was_skipped`: bool - Flag para UI (mostrar "sin movimientos")

#### Métodos

##### `__init__(self, ...)`

- **Parámetros:**
  - `player1_name`, `player2_name`: Nombres (backcompat)
  - `test_bearing_off`: Crear tablero de test
  - `board`, `dice`, `player1`, `player2`: **Dependency Injection**
- **Decisión DIP:** Acepta dependencias permite testing con mocks; si None, crea defaults
- **Ejemplo:**

  ```python
  # Producción
  game = Game("Alice", "Bob")

  # Testing
  mock_board = Mock()
  game = Game(board=mock_board)
  ```

##### `setup_game(self)`

- Inicializa juego:
  1. `board.setup_starting_positions()`
  2. `player1.distribute_checkers(board)`
  3. `player2.distribute_checkers(board)`
  4. `sync_checkers()` - Reconcilia Checker objects con Board state
  5. `__game_initialized__ = True`
- **Decisión:** Método separado permite resetear juego sin recrear instancia

##### `sync_checkers(self)`

- **Problema:** Board es SSoT pero Players tienen objetos Checker - pueden desincronizar
- **Solución:** Recorre `board.points`, `bar`, `home` y actualiza estados/posiciones de Checker objects
- **Algoritmo determinístico:**
  1. Marca N checkers como BORNE_OFF (desde el final de la lista)
  2. Marca M checkers como ON_BAR (desde el inicio, saltando BORNE_OFF)
  3. Asigna posiciones ON_BOARD en orden creciente de puntos
- **Uso:** Llamado después de cada movimiento/captura
- **Decisión:** Proceso determinístico asegura tests reproducibles

##### `initial_roll_until_decided(self) -> int`

- Bucle que tira dados hasta obtener no-empate:
  ```python
  while True:
      dice.initial_roll()
      winner = dice.get_highest_roller()
      if winner != 0:
          self.current_player = player1 if winner == 1 else player2
          return winner
  ```
- **Retorna:** 1 o 2 (ganador de tirada inicial)
- **Decisión:** Bucle infinito es seguro (prob. empate = 1/6, esperanza < 2 iteraciones)

##### `start_turn(self)`

- Inicia turno del jugador actual:
  1. Valida juego inicializado
  2. Valida `current_player` seteado
  3. Valida juego no terminado
  4. `dice.roll()`
  5. `current_player.start_turn(dice)`
- **Excepciones:** `GameNotInitializedError`, `GameAlreadyOverError`
- **Decisión:** Validaciones exhaustivas previenen bugs sutiles

##### `roll_dice_for_turn(self)`

- Versión avanzada de `start_turn` que maneja skip automático:
  1. `start_turn()`
  2. Si `has_any_valid_moves()` → retorna
  3. Sino: `end_turn()`, `switch_players()`, repite hasta 10 veces
  4. Si 10 veces sin movimientos → warning de stalemate
- **Uso:** CLI/UI llaman esto en vez de `start_turn` para UX fluida
- **Decisión:** Lógica de skip en Game vs UI centraliza comportamiento

##### `apply_move(self, from_point, to_point) -> bool`

- Aplica movimiento regular:
  1. Validaciones (inicializado, current_player, no game over, remaining_moves > 0)
  2. Si `from_point == "bar"`: lógica de entrada desde barra
  3. Sino: movimiento normal en tablero
  4. Calcula distancia según dirección del jugador
  5. Valida dados disponibles (`can_use_dice_for_move`)
  6. Ejecuta en Board (`move_checker` o `enter_from_bar`)
  7. Consume dados (`use_dice_for_move`)
  8. `sync_checkers()`
  9. Si `remaining_moves == 0` o `!has_any_valid_moves()` → switch players
- **Retorna:** `True` si exitoso, `False` si inválido (dados no match)
- **Excepciones:** `InvalidMoveError` si Board rechaza movimiento
- **Decisión:** Retornar bool vs siempre exception permite UX más fluida (re-intentar sin crash)

##### `get_valid_moves(self, from_point) -> list`

- Calcula movimientos válidos para una ficha:
  - Si `from_point == "bar"`: puntos de entrada posibles
  - Sino: puntos alcanzables con dados disponibles
  - Incluye `"bear_off"` si condiciones cumplen
- **Retorna:** Lista de destinos válidos (int o "bear_off")
- **Algoritmo:**
  1. Para cada dado en `available_moves`:
  2. Calcula punto destino
  3. Valida con `board.is_valid_move`
  4. Si en home board, chequea bear_off
- **Uso:** UI muestra highlights de movimientos posibles
- **Decisión:** Retornar lista permite UI reactiva sin lógica duplicada

##### `apply_bear_off_move(self, from_point) -> bool`

- Aplica bearing off:
  1. Valida todas fichas en home (`board.all_checkers_in_home_board`)
  2. Calcula dado requerido
  3. Si no exacto, busca dado mayor + verifica checker es el más alto
  4. Ejecuta `board.bear_off`
  5. Consume dados
  6. `sync_checkers()`
  7. Switch players si necesario
- **Retorna:** `True` si exitoso
- **Excepciones:** `InvalidMoveError` si inválido
- **Decisión:** Método separado de `apply_move` por complejidad de validación bear-off

##### `has_any_valid_moves(self) -> bool`

- Verifica si jugador actual tiene algún movimiento legal:
  1. Si fichas en barra: chequea entradas posibles
  2. Sino: itera puntos del tablero, llama `get_valid_moves` y `is_valid_bear_off_move`
- **Retorna:** `True` si al menos 1 movimiento existe
- **Uso:** Determinar skip automático de turno
- **Decisión:** Query method separado evita lógica duplicada en CLI/UI

##### `is_valid_bear_off_move(self, from_point) -> bool`

- Chequea si bearing off es legal desde un punto específico:
  - Similar a lógica en `apply_bear_off_move` pero sin ejecutar
- **Retorna:** `True` si válido
- **Decisión:** Separar validación de ejecución permite dry-run

##### `switch_players(self)`

- Intercambia `current_player` ↔ `other_player`
- **Validaciones:** Juego debe estar inicializado
- **Decisión:** Método explícito vs intercambio manual mejora trazabilidad

##### `is_game_over(self) -> bool`

- Delega a `board.check_winner() != 0`
- **Decisión:** Wrapper para consistencia de API

##### `get_winner(self) -> Player`

- Retorna objeto Player ganador basado en `board.check_winner()`
- **Retorna:** `player1`, `player2`, o `None`
- **Decisión:** Retornar objeto vs int permite acceder a `.name` directamente

---

## Interfaces de Usuario

### cli/cli.py - Clase BackgammonCLI

**Propósito:** Interfaz de texto que permite jugar desde terminal. Organizada siguiendo SRP.

#### Secciones (Responsabilidades)

##### Game Flow Control

- `start_game()`: Orquesta inicio (welcome → nombres → setup → loop)
- `game_loop()`: Bucle principal hasta game over
- `_execute_player_turn()`: Ejecuta un turno completo (roll → moves → switch)

##### User Input Handling

- `_get_player_names()`: Captura nombres por input()
- `handle_player_move()`: Parsea y ejecuta movimiento del usuario
  - Soporta formatos: `"X Y"`, `"bar Y"`, `"X off"`
  - Validaciones y feedback de error
- `_parse_move_input(input_str)`: Convierte string a tupla (from, to)

##### Display Methods

- `display_welcome()`: Mensaje de bienvenida ASCII art
- `display_board()`: Renderiza tablero en texto con puntos/fichas
- `display_current_player_info()`: Muestra jugador actual y color
- `display_dice_roll()`: Muestra dados tirados
- `display_available_moves()`: Lista movimientos restantes
- `display_game_over()`: Pantalla de victoria
- `_display_game_instructions()`: Ayuda de comandos

##### Legal Move Validation

- `_has_legal_moves()`: Wrapper que chequea bar entries/regular/bear-off
- `_has_legal_bar_entries()`: Valida entradas desde barra posibles
- `_has_legal_regular_moves()`: Valida movimientos normales posibles
- `_has_legal_bear_offs()`: Valida bearing offs posibles

**Decisión de Diseño:** Agrupar métodos por responsabilidad (no por orden alfabético) facilita navegación y cumple SRP a nivel de grupos.

#### Integración con Game

```python
def game_loop(self):
    while not self.game.is_game_over():
        self.display_board()
        self.game.start_turn()
        self.display_dice_roll()

        while self.game.current_player.remaining_moves > 0:
            if not self._has_legal_moves():
                # Auto-skip
                break
            self.handle_player_move()

    self.display_game_over()
```

**Decisión:** CLI no contiene reglas de juego; delega TODO a `Game`. CLI solo presenta/captura datos.

---

### pygame_ui/ui.py - Clase BackgammonUI

**Propósito:** Interfaz gráfica con Pygame. Permite juego interactivo con mouse/teclado.

#### Estados de la Aplicación

- `START_SCREEN`: Pantalla de inicio con input de nombres
- `GAME_SCREEN`: Juego en curso
- `WINNER_SCREEN`: Pantalla de victoria con botón "Play Again"

#### Componentes Visuales

##### Tablero

- `draw_board()`: Dibuja triángulos alternados, barra, números de puntos
- Colores: TAN/DARK_BROWN para contraste
- Dimensiones calculadas en `calculate_point_rects()`

##### Fichas

- `draw_checkers()`: Dibuja círculos blancos/negros en posiciones
- `_get_point_checker_position()`: Calcula coordenadas x,y para N-ésima ficha en punto
- Stacking: Fichas apiladas verticalmente; si >5 muestra número

##### Panel de Información

- `draw_info_panel()`: Muestra jugador actual, dados, movimientos restantes
- Botón "Bear Off": Permite bearing off por click

##### Interacción

- `_get_point_at_position(x, y)`: Determina qué punto clickeó usuario (mapeo inverso)
- `_handle_click(pos)`: Maneja clicks en fichas/puntos/botones
  1. Click en ficha → seleccionar + highlight movimientos válidos (`game.get_valid_moves`)
  2. Click en destino válido → `game.apply_move`
  3. Click en "Bear Off" → `game.apply_bear_off_move`

**Decisión de Diseño:**

- Rendering separado de lógica (draw_X vs handle_X)
- Cálculo de geometría en métodos dedicados permite ajustar layout sin tocar lógica
- Pygame event loop simple: poll events → update state → draw

#### Mapeo CLI ↔ Pygame

| CLI Input  | Pygame Action                            |
| ---------- | ---------------------------------------- |
| `"23 20"`  | Click en punto 23, click en punto 20     |
| `"bar 21"` | Click en barra, click en punto 21        |
| `"5 off"`  | Click en punto 5, click botón "Bear Off" |

**Consistencia:** Ambas UIs usan misma `Game` API → comportamiento idéntico.

---

## Sistema de Excepciones

### core/exceptions.py

**Jerarquía:**

```
Exception
└── BackgammonError (base custom)
    ├── GameError
    │   ├── GameNotInitializedError
    │   ├── InvalidPlayerTurnError
    │   ├── GameAlreadyOverError
    │   └── InvalidMoveError
    ├── BoardError
    │   └── InvalidPointError
    ├── PlayerError
    │   ├── NoMovesRemainingError
    │   ├── InvalidCheckerCountError
    │   └── InvalidPlayerColorError
    ├── CheckerError
    │   ├── InvalidCheckerPositionError
    │   ├── InvalidCheckerStateError
    │   └── CheckerPositionError
    └── DiceError
        ├── DiceNotRolledError
        └── InvalidDiceValueError
```

**Decisiones:**

1. **Jerarquía clara:** Permite `try...except BoardError` para capturar TODAS las excepciones de Board
2. **Mensajes descriptivos:** Cada excepción incluye contexto (ej: InvalidPointError muestra punto inválido)
3. **Separación por módulo:** Facilita identificar origen del error
4. **GameQuitException separado:** Hereda de Exception (no BackgammonError) porque no es un "error" sino control de flujo

**Uso:**

```python
try:
    game.apply_move(from_point, to_point)
except GameNotInitializedError:
    print("Debes inicializar el juego primero")
except InvalidMoveError as e:
    print(f"Movimiento inválido: {e}")
except GameAlreadyOverError:
    print("El juego ya terminó")
```

---

## Anexos

### Diagrama UML (Simplificado)

Ver archivo `uml.puml` para diagrama completo generado con PlantUML.

**Relaciones principales:**

- Game _compone_ Board, Dice, Player (composición)
- Player _contiene_ 15 Checkers (composición)
- CLI/UI _dependen de_ Game (dependencia)

### Documentación Adicional

- **CHANGELOG.md:** Historial completo de cambios por fecha
- **prompts/prompts-desarrollo.md:** Registro de prompts usados para desarrollo (1547 líneas)
- **prompts/prompts-testing.md:** Registro de prompts para testing (853 líneas)
- **prompts/prompts-documentacion.md:** Registro de prompts para docs (104 líneas)
- **.github/workflows/ci.yml:** Configuración de CI con coverage y pylint

### Comandos Útiles

```bash
# Ejecutar tests
python -m unittest

# Coverage report
coverage run -m unittest
coverage report -m

# Jugar CLI
python -m cli.cli

# Jugar Pygame
python -m pygame_ui.ui

# Pylint
find . -name "*.py" | xargs pylint
```

---
