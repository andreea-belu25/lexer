from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable
from collections import deque

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
	S: set[str]
	K: set[STATE]
	q0: STATE
	d: dict[tuple[STATE, str], set[STATE]]
	F: set[STATE]

	def epsilon_closure(self, state: STATE) -> set[STATE]:
		# compute the epsilon closure of a state (you will need this for subset construction)
		# see the EPSILON definition at the top of this file
		
		#  sort of bfs for traversing the NFA
		closure = {state}
		processing = deque([state])
		processed = set()

		while processing:
			current_state = processing.popleft()
			
			if current_state in processed:
				continue

			processed.add(current_state)

			# find all states reachable through epsilon transitions from current_state
			transition = (current_state, EPSILON)
			if transition in self.d:
				transitions = self.d[transition]
				for new_state in transitions:
					if new_state not in processed:
						processing.append(new_state)
						closure.add(new_state)


		return closure

	def subset_construction(self) -> DFA[frozenset[STATE]]:  
		# convert this nfa to a dfa using the subset construction algorithm
		
		states = set()
		transitions = {}

		#  initial_state of the DFA = initial_closure
		initial_closure = frozenset(self.epsilon_closure(self.q0))

		processing = deque([initial_closure])
		states.add(initial_closure)

		#  add a sink state for cases when for a given input it goes nowhere
		sink_state = frozenset()
		states.add(sink_state)
		for symbol in self.S:
			transitions[(sink_state, symbol)] = sink_state

		#  using bfs for updating the states and transitions for the resulting DFA
		while processing:
			current = processing.popleft()

			for symbol in self.S:
				reachable_states = set()

				for state in current:
					dest_states_from_state = self.d.get((state, symbol), set())
					for dest in dest_states_from_state:
						reachable_states.update(self.epsilon_closure(dest))

				if reachable_states:
					next_state = frozenset(reachable_states)
					transitions[(current, symbol)] = next_state

					if next_state not in states:
						states.add(next_state)
						processing.append(next_state)
				else:
					transitions[(current, symbol)] = sink_state

		#  final_states of the DFA are the states from the NFA which contain a final_state
		final_states = set()
		for state in states:
			for sub_state in state:
				if sub_state in self.F:
					final_states.add(state)
					break 

		return DFA(S = self.S, K = states, q0 = initial_closure, d = transitions, F = final_states)	
				
	def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
		# optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
		# from the DFA class. See the comments there for more details.

		# remap the set of states
		remapped_states = set()
		for state in self.K:
			remapped_states.add(f(state))

		# remap the initial state
		remapped_initial_state = f(self.q0)

		# remap the transitions
		remapped_transitions = {}
		for (current_state, symbol), target_states in self.d.items():
			remapped_current_state = f(current_state)
			remapped_target_states = set()
			for target_state in target_states:
				remapped_target_states.add(f(target_state))
			remapped_transitions[(remapped_current_state, symbol)] = remapped_target_states

		# remap the set of accepting states
		remapped_final_states = set()
		for state in self.F:
			remapped_final_states.add(f(state))

		# return the new NFA with remapped components
		return NFA(S = self.S.copy(), K = remapped_states, q0 = remapped_initial_state, d = remapped_transitions, F = remapped_final_states)