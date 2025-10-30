# Automated Reports

## Coverage Report
```text
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
cli/__init__.py          0      0   100%
cli/cli.py             272      3    99%   96-97, 309
core/__init__.py         0      0   100%
core/board.py          150     12    92%   135, 214, 219, 228, 293, 302-309
core/checker.py         91      9    90%   138, 149, 159, 177, 186-190
core/dice.py            53      7    87%   28, 46, 91, 99-102
core/exceptions.py     100      0   100%
core/game.py           367     52    86%   164, 196-198, 256, 285, 301, 322, 391, 421, 466-467, 487-489, 513, 529, 565, 581-585, 612, 618, 630, 641-644, 650-656, 669-689
core/player.py         140     10    93%   306, 318-326
--------------------------------------------------
TOTAL                 1173     93    92%

```

## Pylint Report
```text
************* Module pygame_ui.ui
pygame_ui/ui.py:71:15: W0718: Catching too general exception Exception (broad-exception-caught)
pygame_ui/ui.py:84:15: W0718: Catching too general exception Exception (broad-exception-caught)
pygame_ui/ui.py:94:15: W0718: Catching too general exception Exception (broad-exception-caught)
pygame_ui/ui.py:98:0: R0902: Too many instance attributes (21/7) (too-many-instance-attributes)
pygame_ui/ui.py:107:8: E1101: Module 'pygame' has no 'init' member (no-member)
pygame_ui/ui.py:379:20: E1101: Module 'pygame' has no 'SRCALPHA' member (no-member)
pygame_ui/ui.py:393:20: E1101: Module 'pygame' has no 'SRCALPHA' member (no-member)
pygame_ui/ui.py:398:4: R0914: Too many local variables (27/15) (too-many-locals)
pygame_ui/ui.py:567:66: E1101: Module 'pygame' has no 'SRCALPHA' member (no-member)
pygame_ui/ui.py:642:33: E1101: Module 'pygame' has no 'QUIT' member (no-member)
pygame_ui/ui.py:647:37: E1101: Module 'pygame' has no 'MOUSEBUTTONDOWN' member (no-member)
pygame_ui/ui.py:656:37: E1101: Module 'pygame' has no 'MOUSEBUTTONDOWN' member (no-member)
pygame_ui/ui.py:640:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
pygame_ui/ui.py:670:37: E1101: Module 'pygame' has no 'KEYDOWN' member (no-member)
pygame_ui/ui.py:672:44: E1101: Module 'pygame' has no 'K_BACKSPACE' member (no-member)
pygame_ui/ui.py:640:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
pygame_ui/ui.py:677:44: E1101: Module 'pygame' has no 'K_BACKSPACE' member (no-member)
pygame_ui/ui.py:640:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
pygame_ui/ui.py:690:41: E1101: Module 'pygame' has no 'MOUSEBUTTONDOWN' member (no-member)
pygame_ui/ui.py:697:37: E1101: Module 'pygame' has no 'MOUSEBUTTONDOWN' member (no-member)
pygame_ui/ui.py:721:8: E1101: Module 'pygame' has no 'quit' member (no-member)
pygame_ui/ui.py:631:4: R0912: Too many branches (34/12) (too-many-branches)
pygame_ui/ui.py:631:4: R0915: Too many statements (72/50) (too-many-statements)
pygame_ui/ui.py:13:0: C0411: standard import "sys" should be placed before third party import "pygame" (wrong-import-order)
pygame_ui/ui.py:15:0: C0411: standard import "json" should be placed before third party imports "pygame", "redis" (wrong-import-order)
************* Module cli.cli
cli/cli.py:267:16: R1723: Unnecessary "else" after "break", remove the "else" and de-indent the code inside it (no-else-break)
************* Module main
main.py:1:0: C0114: Missing module docstring (missing-module-docstring)
************* Module core.game
core/game.py:431:0: C0325: Unnecessary parens after 'not' keyword (superfluous-parens)
core/game.py:15:0: R0902: Too many instance attributes (11/7) (too-many-instance-attributes)
core/game.py:22:4: R0913: Too many arguments (8/5) (too-many-arguments)
core/game.py:258:4: R0912: Too many branches (18/12) (too-many-branches)
core/game.py:550:16: W0612: Unused variable 'dice_value' (unused-variable)
core/game.py:591:4: R0912: Too many branches (13/12) (too-many-branches)
core/game.py:15:0: R0904: Too many public methods (22/20) (too-many-public-methods)
************* Module tests.tests_cli
tests/tests_cli.py:7:0: W0611: Unused InvalidMoveError imported from core.exceptions (unused-import)
************* Module tests.tests_game
tests/tests_game.py:5:0: W0611: Unused Dice imported from core.dice (unused-import)

-----------------------------------
Your code has been rated at 9.74/10


```
