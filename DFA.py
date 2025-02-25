from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar
from collections import deque

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
	S: set[str]
	K: set[STATE]
	q0: STATE
	d: dict[tuple[STATE, str], STATE]
	F: set[STATE]

	def accept(self, word: str) -> bool:
		# simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise

		#  start from the initial state
		current_state = self.q0

		#  trying to consume the word
		for symbol in word:
			next_state = self.d.get((current_state, symbol))
			if next_state:
				current_state = next_state
			else:
				return False
		
		#  check if after consuming the word I received a final state => the word is accepted
		if current_state not in self.F:
			return False
		return True

	def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
		# optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
		# this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
		# automaton.

		# for example, given this dfa:

		# > (0) -a,b-> (1) ----a----> ((2))
		#               \-b-> (3) <-a,b-/
		#                   /     ⬉
		#                   \-a,b-/

		# applying the x -> x+2 function would create the following dfa:

		# > (2) -a,b-> (3) ----a----> ((4))
		#               \-b-> (5) <-a,b-/
		#                   /     ⬉
		#                   \-a,b-/
		pass
	
	def minimize(self) -> 'DFA[STATE]':
		#  step 1: split states between final states and non-final states using bfs traversal
		final_states = set()
		normal_states = set()

		processing = deque()
		processing.append(self.q0)
		processed = set()
		while processing:
			current_state = processing.popleft()
			if current_state in processed:
				continue

			processed.add(current_state)

			if current_state in self.F:
				final_states.add(current_state)
			else:
				normal_states.add(current_state)

			for symbol in self.S:
				if (current_state, symbol) in self.d:
					next_state = self.d.get((current_state, symbol))
					processing.append(next_state)
		
		#  step 2: make partitions
		if len(final_states) > 0 and len(normal_states) > 0:
			partition = [final_states, normal_states]
		elif len(final_states) > 0:
			partition = [final_states]
		elif len(normal_states) > 0:
			partition = [normal_states]
		else:
			partition = []

		#  sort the alphabet for consistency in processing
		alphabet = sorted(self.S)

		#  assign a number to a group (each of the state of the group will have that number)
		while True:
			no_of_group = 1
			state_group_no = {}

			for group in partition:
				for state in group:
					state_group_no[state] = no_of_group
				no_of_group += 1

			#  current_partition - current split of groups of states
			next_partition = []

			for group in partition:
				keys = []
				for state in group:
					key = []
					for symbol in self.S:
						if (state, symbol) in self.d:
							next_state = self.d.get((state, symbol))
							key.append(state_group_no[next_state])
					keys.append(tuple([tuple(key), state]))
				
				next_groups = {}
				for (key, state) in keys:
					if key not in next_groups:
						next_groups[key] = set()
					next_groups[key].add(state)

				for next_group in next_groups.values():
					next_partition.append(next_group)

			#  stop when the partition did not change
			if len(partition) == len(next_partition):
				break

			partition = next_partition

		#  step 3: actual construction of the minimised dfa
		states = {}
		for group in partition:
			for state in group:
				states[state] = frozenset(group)
		
		states_dfa_minimised = set(states.values())

		initial_state_dfa_minimised = states[self.q0]
		
		final_states_dfa_minimised = set()
		for state, group in states.items():
			for final_state in self.F:
				if final_state in group:
					final_states_dfa_minimised.add(group)
					break

		transitions_dfa_minimised = {}
		for group in partition:
			for state in group:
				for symbol in self.S:
					next_state = self.d.get((state, symbol))
					if next_state and next_state not in transitions_dfa_minimised:
						transitions_dfa_minimised[(states[state], symbol)] = states[next_state]
		
		return DFA(
			S = self.S, 
			K = states_dfa_minimised, 
			q0 = initial_state_dfa_minimised, 
			d = transitions_dfa_minimised, 
			F = final_states_dfa_minimised
		)