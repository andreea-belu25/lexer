from .Regex import Regex, parse_regex
from .NFA import NFA
from functools import reduce

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs

class Lexer:
	def __init__(self, spec: list[tuple[str, str]]) -> None:
		#  Save [(token1, its corresponding NFA1)..]
		self.afnsList = []

		#  Handle the first NFA separately
		firstName, firstRegex = spec[0]
		previousNfa = parse_regex(firstRegex).thompson()
		#  Save (token1, NFA1)
		self.afnsList.append((firstName, previousNfa))

		newInitialState = 0

		# Process subsequent NFAs
		for name, regex in spec[1:]:
			# Build the NFA for current regex
			nextNfa = parse_regex(regex).thompson()
			
			# Remap states of the next NFA
			nextNfa = nextNfa.remap_states(lambda x: x + len(previousNfa.K))
			
			# Store the token and its corresponding NFA
			self.afnsList.append((name, nextNfa))

			# Combine transitions with epsilon transitions from initial state
			combinedD = dict(previousNfa.d)
			combinedD.update(nextNfa.d)
			if (newInitialState, EPSILON) in combinedD:
				combinedD[(newInitialState, EPSILON)] |= {previousNfa.q0, nextNfa.q0}
			else:
				combinedD[(newInitialState, EPSILON)] = {previousNfa.q0, nextNfa.q0}

			# Combine all elements and update the previous NFA
			previousNfa = NFA(S=previousNfa.S | nextNfa.S, K=previousNfa.K | nextNfa.K | {newInitialState},
								q0=newInitialState, d=combinedD, F=previousNfa.F | nextNfa.F)

		# Store the final combined NFA
		self.nfa = previousNfa
		
		# Convert NFA to DFA
		self.dfa = self.nfa.subset_construction()

	def findMatchingToken(self, matchState, start, end, word):
		for name, nfa in self.afnsList:   				#  Parse NFAs
			for finalState in nfa.F:       				#  For each NFA, parse its final states
				if finalState in set(matchState):  		#  Check if a final state is in the set states of the DFA
					return (name, word[start:end])		#  Return the first pair (token, matched_string) 
		return None										#  Didn't find a corresponding match token
	
	def lex(self, word: str) -> list[tuple[str, str]] | None:
		# this method splits the lexer indto tokens based on the specification and the rules described in the lecture
		# the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

		# if an error occurs and the lexing fails, you should return none
		
		#  Save the resulted tokens
		tokens = []
		
		#  Error handling
		noOfLines = 0    			#  line where the error occured
		errorPos = 0	 			#  the column where the error occured	
	
		# State tracking
		currentState = self.dfa.q0  
		prevState = None			#  for handling sink state errors
	
		# Match tracking
		lastMatchEnd = 0   			#  start position of the possible current match (start from the position of the last match)   
		lastRuleMatchPos = 0		#  end position of the possible current match
		lastRuleState = None

		# Process the word
		i = 0
		while i < len(word):
			letter = word[i]

			if letter == '\n':
				noOfLines += 1	
				errorPos = -1		
			errorPos += 1

			#  Try current transition if it exists
			if (currentState, letter) in self.dfa.d:
				currentTrans = self.dfa.d[(currentState, letter)]

				prevState = currentState
				currentState = currentTrans

				token = self.findMatchingToken(prevState, lastMatchEnd, i, word)

				if token:
					lastRuleState = prevState  #  last state where it was a match
					lastRuleMatchPos = i       #  last position where it was a match
			else:
				#  If there is no possible transition over letter => letter is not in the alphabet
				return [("", "No viable alternative at character " + str(errorPos) + ", line " + str(noOfLines))]

			#  Check if there is a sink state
			#  If yes, go back to the previous state that was a matching state which should be final
			if currentState == frozenset():
				#  A lexing error was found if there is no previous state
				#  I am at the final of the word and there is no matching pattern
				if prevState == None:
					return [("", "No viable alternative at character EOF, line " + str(noOfLines))]
				
				if lastMatchEnd == lastRuleMatchPos:  #  there is no character in a match => eliminate the possibility of cicles 
					return [("", "No viable alternative at character " + str(errorPos) + ", line " + str(noOfLines))]
				
				#  Take the first rule with which there is a match
				token = self.findMatchingToken(lastRuleState, lastMatchEnd, lastRuleMatchPos, word)

				#  Save the result 
				if token:
					tokens.append(token)
					lastMatchEnd = lastRuleMatchPos
				else:
					return [("", "No viable alternative at character " + str(errorPos) + ", line " + str(noOfLines))]

				#  Reset the DFA
				prevState = None
				currentState = self.dfa.q0
				#  Start from the position where it matched last time
				i = lastMatchEnd - 1
				
			i += 1
		
		#  a+ (regex), aaa (input)=> in case the word is finished before making a match => check the final match 
		token = self.findMatchingToken(currentState, lastMatchEnd, len(word), word)
		if token:
			lastRuleState = currentState
			lastRuleMatchPos = len(word)

		if currentState == frozenset():
			if prevState == None:
				return [("", "No viable alternative at character EOF, line " + str(noOfLines))]
			token = self.findMatchingToken(lastRuleState, lastMatchEnd, len(word), word)
			if token:
				tokens.append(token)
			else:
				return [("", "No viable alternative at character EOF, line " + str(noOfLines))]
		
		else: 
			token = self.findMatchingToken(lastRuleState, lastMatchEnd, len(word), word)
			if token:
				tokens.append(token)
			else:
				return [("", "No viable alternative at character EOF, line " + str(noOfLines))]

		return tokens