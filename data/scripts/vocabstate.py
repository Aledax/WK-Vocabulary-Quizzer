from dataclasses import dataclass

STATE_IDLE = 0
STATE_QUESTION = 1
STATE_ANSWER = 2

@dataclass
class VocabState:
    state: int # 0 - 2
    vocabulary: list
    vocabulary_index: int
    mistake_indices: list
    phase: int

    @property
    def current_vocabulary(self):
        return self.vocabulary[self.vocabulary_index]

    @property
    def vocabulary_count(self):
        return len(self.vocabulary)

    @property
    def mistake_count(self):
        return len(self.mistake_indices)
    
    @property
    def mistake_vocabulary(self):
        return [self.vocabulary[i] for i in self.mistake_indices]