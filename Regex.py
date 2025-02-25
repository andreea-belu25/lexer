from typing import Any, List
from .NFA import NFA

EPSILON = ''

#  bass class for Regex ADT
class Regex:
    #  returns the string representation of the regular expression
    def __str__(self) -> str:
        pass

    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

#  represents a symbol in the regular expression
class Symbol(Regex):
    def __init__(self, char: str):
        self.char = char
    
    def __str__(self) -> str:
        return self.char

    def thompson(self) -> NFA[int]:
        return NFA(S={self.char}, K={1, 2}, q0=1, d={(1, self.char): {2}}, F={2})
        
#  represents the union of two regular expressions
class Union(Regex):
    def __init__(self, *arg: [Regex]):
        self.components = arg
    
    def __str__(self) -> str:
        return "Union(" + ",".join(str(component) for component in self.components) + ")"

    def thompson(self) -> NFA[int]:
        #  first NFA
        previous_nfa = self.components[0].thompson()
        previous_nfa = previous_nfa.remap_states(lambda x: x + 1)
        aux = 1 + len(previous_nfa.K)
        
        initial_states = [previous_nfa.q0]
        final_states = set(previous_nfa.F)

        for index in range(1, len(self.components)):
            #  second NFA
            next_nfa = self.components[index].thompson()
            next_nfa = next_nfa.remap_states(lambda x: x + aux)
            aux += len(next_nfa.K)

            #  update initial and final states
            initial_states.append(next_nfa.q0)
            final_states.update(next_nfa.F)

            #  combine all the elements of the two NFAs
            combined_S = previous_nfa.S | next_nfa.S
            combined_K = previous_nfa.K | next_nfa.K
            combined_d = dict(previous_nfa.d)
            combined_d.update(next_nfa.d)
            combined_F = next_nfa.F

            #  update the previous NFA
            previous_nfa = NFA(S=combined_S, K=combined_K, q0=previous_nfa.q0, d=combined_d, F=combined_F)

        #  update initial and final states
        new_initial_state = 1
        new_final_state = aux + 1
        previous_nfa.K.add(new_initial_state)
        previous_nfa.K.add(new_final_state)

        #  update transitions considering initial and final states
        new_d = dict(previous_nfa.d)
        new_d[(new_initial_state, EPSILON)] = set(initial_states)

        for state in final_states:
            if (state, EPSILON) in new_d:
                new_d[(state, EPSILON)].add(new_final_state)
            else:
                new_d[(state, EPSILON)] = {new_final_state}

        #  return the union NFA
        return NFA(S=previous_nfa.S, K=previous_nfa.K, q0=new_initial_state, d=new_d, F={new_final_state})

#  represents the concatenation of two regular expressions
class Concat(Regex):
    def __init__(self, *arg: [Regex]):
        self.components = arg

    def __str__(self) -> str:
        return "Concat(" + ",".join(str(component) for component in self.components) + ")"

    def thompson(self) -> NFA[int]:
        previous_nfa = self.components[0].thompson()
        
        for index in range(1, len(self.components)):
            next_nfa = self.components[index].thompson()
            next_nfa = next_nfa.remap_states(lambda x: x + len(previous_nfa.K))

            #  add epsilon transitions from the final states of the first NFA to the initial state of the next NFA
            for final_state in previous_nfa.F:
                if (final_state, EPSILON) not in previous_nfa.d:
                    previous_nfa.d[(final_state, EPSILON)] = set()
                previous_nfa.d[(final_state, EPSILON)].add(next_nfa.q0)

            #  combine all the elements of the two NFAs
            combined_S = previous_nfa.S | next_nfa.S
            combined_K = previous_nfa.K | next_nfa.K
            combined_d = dict(previous_nfa.d)
            combined_d.update(next_nfa.d)
            combined_F = next_nfa.F

            #  update the previous NFA
            previous_nfa = NFA(S=combined_S, K=combined_K, q0=previous_nfa.q0, d=combined_d, F=combined_F)

        return previous_nfa

#  represents the Kleene star (zero or more repetitions) of a regular expression
class Star(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def __str__(self) -> str:
        return f"Star({self.regex})"

    def thompson(self) -> NFA[int]:
        inner_nfa = self.regex.thompson()
        #  update the states from the inner_dfa
        inner_nfa = inner_nfa.remap_states(lambda x: x + 1)

        #  update intial and final states
        new_initial_state = 1
        new_final_state = len(inner_nfa.K) + 2

        inner_nfa.K.add(new_initial_state)
        inner_nfa.K.add(new_final_state)

        #  update transitions by making epsilon transitions like in Thompson construction
        new_d = dict(inner_nfa.d)

        new_d[(new_initial_state, EPSILON)] = set()
        new_d[(new_initial_state, EPSILON)].add(inner_nfa.q0)
        new_d[(new_initial_state, EPSILON)].add(new_final_state)

        for state in inner_nfa.F:
            if (state, EPSILON) not in new_d:
                new_d[(state, EPSILON)] = set()
            new_d[(state, EPSILON)].add(inner_nfa.q0)
            new_d[(state, EPSILON)].add(new_final_state)

        return NFA(S=inner_nfa.S.copy(), K=inner_nfa.K, q0=new_initial_state, d=new_d, F={new_final_state})

#  represents [A-Z] regular expression
class Uppercase(Regex):
    def __str__(self) -> str:
        return f"[A-Z]"

    def thompson(self) -> NFA[int]:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        elements = [Symbol(letter) for letter in alphabet]
        regex = Union(*elements)
        return regex.thompson()

#  represents [a-z] regular expression
class Lowercase(Regex):
    def __str__(self) -> str:
        return f"[a-z]"

    def thompson(self) -> NFA[int]:
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        elements = [Symbol(letter) for letter in alphabet]
        regex = Union(*elements)
        return regex.thompson()

#  represents [0-9] regular expression
class Digit(Regex):
    def __str__(self) -> str:
        return f"[0-9]"

    def thompson(self) -> NFA[int]:
        alphabet = "0123456789"
        elements = [Symbol(digit) for digit in alphabet]
        regex = Union(*elements)
        return regex.thompson()

#  represents Epsilon regular expression
class Epsilon(Regex):
    def __str__ (self) -> str:
        return EPSILON

    def thompson(self) -> NFA[int]:
        return NFA(S=set(), K={1, 2}, q0=1, d={(1, EPSILON): {2}}, F={2})

#  represents the plus (one or more repetitions) of a regular expression
class Plus(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex
    
    def __str__(self) -> str:
        return f"Plus({str(self.regex)})"

    def thompson(self) -> NFA[int]:
        #  A+ = AA*
        regex = Concat(self.regex, Star(self.regex))
        return regex.thompson()

#  represents the question (zero or one repetition) of a regular expression
class Question(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def __str__(self) -> str:
        return f"Question({str(self.regex)})"

    def thompson(self) -> NFA[int]:
        #  A? = (EPSILON | A)
        regex = Union(Epsilon(), self.regex)
        return regex.thompson()

stack = []
def process_expression():
    global stack
    args_concat = []
    result_stack = []
    aux_stack = [] 

    stack.reverse()

    #  aux_stack used for processing the current expression
    for symbol in stack:
        if symbol == '(':
            break
        aux_stack.append(symbol)
        
    stack.reverse()
    #  eliminate the elements from the current expression from global stack
    #  keep those that do not take part in the current expression
    while stack:
        last = stack.pop()
        if last == '(':
            break
    
    aux_stack.reverse()
    while aux_stack:
        last = aux_stack.pop()
        if last == '(':  #  finish to prelucrate the current expression
            break

        if last == '|':  #  find union => save concatenation result
            if len(args_concat) > 1:
                args_concat.reverse()
                result_stack.append(Concat(*args_concat))
            else:
                result_stack.append(args_concat[0])
            args_concat = []
        else:
            args_concat.append(last)  #  concatenate the elements before union

    #   prelucrate the last concatenation (if exists) after |
    if len(args_concat) > 1:
        args_concat.reverse()
        result_stack.append(Concat(*args_concat))
    else:
        if args_concat:
            result_stack.append(args_concat[0])
    
    #  start doing the union of all the concatenations
    args_union = []
    for result in result_stack:
        args_union.append(result)
    
    while result_stack:
        result_stack.pop()
    
    if len(args_union) > 1:
        args_union.reverse()
        result = Union(*args_union)
    else:
        result = args_union[0]
    
    result_stack.append(result)

    #  save the result on stack
    stack.append(result)

def parse_regex(regex: str) -> Regex:
    global stack
    stack = []
    i = 0

    while i < len(regex):
        element = regex[i]

        if element == '(':  #  start new expression
            stack.append('(')

        elif element == '+':
            last = stack.pop()
            stack.append(Plus(last))

        elif element == '*':
            last = stack.pop()
            stack.append(Star(last))

        elif element == '?':
            last = stack.pop()
            stack.append(Question(last))

        elif element == '|':  #  find union in expression
            stack.append('|')

        elif element == ')':  #  end current expression
            process_expression()

        elif element == '\\' and i + 1 < len(regex):
            stack.append(Symbol(regex[i + 1]))
            i += 1

        elif element == '[':  #  start of a character class
            j = i + 1
            if regex[j:j + 3] == "a-z":
                stack.append(Lowercase())
                j += 3
            elif regex[j:j + 3] == "A-Z":
                stack.append(Uppercase())
                j += 3
            elif regex[j:j + 3] == "0-9":
                stack.append(Digit())
                j += 3
            i = j  #  skip ']'

        else:
            if element == ' ' and stack:
                last = stack.pop()
                if last != '\\':
                    stack.append(last)
                    i += 1
                    continue

            stack.append(Symbol(element))

        i += 1

    process_expression()
    return stack[0]