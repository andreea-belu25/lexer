# Lexical Analyzer Implementation
Implementation of a lexical analyzer with DFA/NFA construction, regex parsing, and tokenization capabilities.

## 1. Data Structures Used

### DFA (Deterministic Finite Automaton)
- **S**: Alphabet (set of input symbols)
- **K**: Set of states
- **q0**: Initial state
- **d**: Transition function (dictionary mapping state-symbol pairs to next state)
- **F**: Set of final/accepting states

### NFA (Non-deterministic Finite Automaton)
- **S**: Alphabet (set of input symbols)
- **K**: Set of states
- **q0**: Initial state
- **d**: Transition function (dictionary mapping state-symbol pairs to set of next states)
- **F**: Set of final/accepting states
- Supports epsilon transitions (represented as empty string)

### Regex Classes
- **Symbol**: Represents a single character
- **Union**: Represents alternation (a|b)
- **Concat**: Represents concatenation (ab)
- **Star**: Represents Kleene star (a*)
- **Plus**: Represents one or more repetitions (a+)
- **Question**: Represents optional (a?)
- **Uppercase/Lowercase/Digit**: Character classes [A-Z], [a-z], [0-9]
- **Epsilon**: Represents empty string

## 2. Implementation Logic

### DFA.py
**Accepting words** (`accept()`):
- Starts from initial state
- Consumes input symbol by symbol using transition function
- Returns true if final state is reached after consuming entire word

**Minimizing DFA** (`minimize()`):
- Uses BFS to find all reachable states
- Initial partition: separates final states from non-final states
- Iteratively refines partitions based on transition behavior
- Groups states that cannot be distinguished
- Constructs minimized DFA with merged equivalent states

### NFA.py
**Epsilon closure** (`epsilon_closure()`):
- Uses BFS to find all states reachable via epsilon transitions
- Returns set of all reachable states from a given state

**Subset construction** (`subset_construction()`):
- Converts NFA to equivalent DFA
- Each DFA state represents a set of NFA states (frozenset)
- Computes epsilon closure for each reachable configuration
- Creates sink state for undefined transitions
- Final states are those containing at least one NFA final state

**State remapping** (`remap_states()`):
- Applies a function to rename all states
- Preserves automaton structure and transitions
- Used to avoid state conflicts when combining NFAs

### Regex.py
**Parsing** (`parse_regex()`):
- Uses stack-based approach to parse regex string
- Handles operators: `|`, `*`, `+`, `?`, `()`, `\`, `[]`
- Processes parentheses to build nested expressions
- Returns constructed Regex object tree

**Thompson's construction** (`thompson()`):
- Each Regex class implements Thompson's algorithm
- **Symbol**: Creates 2-state NFA with single transition
- **Union**: Creates new initial/final states with epsilon transitions to/from component NFAs
- **Concat**: Connects final states of first NFA to initial state of second via epsilon transitions
- **Star**: Adds epsilon transitions for zero repetitions and loops
- **Plus**: Implements as AA* (concatenation of regex with its star)
- **Question**: Implements as (ε|A) (union with epsilon)

### Lexer.py
**Initialization** (`__init__()`):
- Processes list of (token_name, regex_pattern) specifications
- Builds NFA for each regex pattern using Thompson's construction
- Remaps states to avoid conflicts between NFAs
- Combines all NFAs with epsilon transitions from new initial state
- Converts combined NFA to DFA using subset construction

**Tokenization** (`lex()`):
- Simulates DFA on input string
- Implements maximal munch: longest match wins
- Implements first-match-wins: first rule in specification has priority
- Tracks last accepting state and position
- On sink state: backtracks to last match and emits token
- Returns list of (token_name, matched_string) pairs
- Provides detailed error messages with line and column numbers

**Finding tokens** (`findMatchingToken()`):
- Checks if current DFA state contains final states from any NFA
- Returns first matching token according to specification order
- Used to determine which token pattern matched
