# Automated Reports

## Coverage Report
```text
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
cli/__init__.py          0      0   100%
cli/cli.py             350     10    97%   66-67, 165, 349-350, 357, 441-442, 449, 494
core/__init__.py         0      0   100%
core/board.py          141      7    95%   123, 162, 199-200, 214, 254, 263
core/checker.py         73      3    96%   123, 134, 144
core/dice.py            36      1    97%   31
core/exceptions.py      58      0   100%
core/game.py           138     10    93%   133, 165-167, 219, 229-231, 234, 239, 274
core/player.py         101      0   100%
--------------------------------------------------
TOTAL                  897     31    97%

```

## Pylint Report
```text
************* Module cli.cli
cli/cli.py:260:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
cli/cli.py:260:8: R1702: Too many nested blocks (7/5) (too-many-nested-blocks)
cli/cli.py:260:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
************* Module core.game
core/game.py:22:4: R0913: Too many arguments (8/5) (too-many-arguments)
************* Module tests.tests_cli
tests/tests_cli.py:505:17: W0212: Access to a protected member _has_legal_moves of a client class (protected-access)
tests/tests_cli.py:517:32: W0212: Access to a protected member _execute_player_turn of a client class (protected-access)
tests/tests_cli.py:631:17: W0212: Access to a protected member _has_legal_bar_entries of a client class (protected-access)
tests/tests_cli.py:652:17: W0212: Access to a protected member _has_legal_bar_entries of a client class (protected-access)
tests/tests_cli.py:673:17: W0212: Access to a protected member _has_legal_bar_entries of a client class (protected-access)
tests/tests_cli.py:694:17: W0212: Access to a protected member _has_legal_regular_moves of a client class (protected-access)
tests/tests_cli.py:715:17: W0212: Access to a protected member _has_legal_regular_moves of a client class (protected-access)
tests/tests_cli.py:737:17: W0212: Access to a protected member _has_legal_bear_offs of a client class (protected-access)
tests/tests_cli.py:759:17: W0212: Access to a protected member _has_legal_bear_offs of a client class (protected-access)
tests/tests_cli.py:776:17: W0212: Access to a protected member _has_legal_bear_offs of a client class (protected-access)
tests/tests_cli.py:1492:21: W0212: Access to a protected member _has_legal_moves of a client class (protected-access)
tests/tests_cli.py:1511:25: W0212: Access to a protected member _has_legal_moves of a client class (protected-access)

-----------------------------------
Your code has been rated at 9.94/10


```
