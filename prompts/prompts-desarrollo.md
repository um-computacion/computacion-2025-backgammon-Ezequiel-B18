# Development Prompts Documentation

## Dice Implementation for Backgammon

### Prompt
```
This is a Backgammon project, we'll first start by implementing the dice class so that we have a logic for the randomness, remember to follow a TDD logic, that would mean tests first, logic later. 

Try to cover all the possible cases for the dice in the backgammon game, that would mean double dices, the first throw, etc.
```

### Response
Created a comprehensive implementation of the Dice class for a Backgammon game following Test-Driven Development principles:

1. First, designed and implemented test cases covering:
   - Dice initialization
   - Ensuring dice values are within the proper range (1-6)
   - Verifying that rolls use randomness (with mocking)
   - Detecting doubles (when both dice show the same value)
   - Handling the special case of doubles (returning four moves instead of two)
   - Managing the initial roll to determine the first player
   - Identifying ties in the initial roll
   - Determining which player rolled higher

2. Then implemented the Dice class with:
   - Methods for rolling the dice
   - Logic to detect doubles
   - Functionality to get available moves (accounting for doubles)
   - Special handling for the initial roll
   - Method to determine which player rolled higher

The implementation follows SOLID principles:
- **Single Responsibility**: The Dice class only handles dice-related logic
- **Open/Closed**: The design allows for extension without modification
- **Liskov Substitution**: No inheritance in this implementation yet
- **Interface Segregation**: Methods have clear, focused responsibilities
- **Dependency Inversion**: No hard-coded dependencies on concrete implementations
