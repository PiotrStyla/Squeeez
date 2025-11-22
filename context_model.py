#!/usr/bin/env python3
"""
Model kontekstowy (Order-N) dla kompresji
Używa poprzednich N znaków jako kontekstu do przewidywania następnego
"""
from collections import defaultdict
import struct
import pickle

class ContextModel:
    """Model Order-N z escape mechanism (PPM-like)"""
    
    def __init__(self, order=2):
        """
        Args:
            order: długość kontekstu (0 = brak kontekstu, 1 = 1 znak, etc.)
        """
        self.order = order
        # contexts[context][symbol] = count
        self.contexts = defaultdict(lambda: defaultdict(int))
        # Statystyki globalne (fallback dla nieznanych kontekstów)
        self.global_counts = defaultdict(int)
        self.total_global = 0
        
        # Stan dla sekwencyjnego kodowania
        self.current_context = b''
        
    def train(self, data):
        """Trenuje model na danych"""
        print(f"    Trening modelu Order-{self.order}...")
        
        # Konwersja do bytes jeśli potrzeba
        if isinstance(data, list):
            data = bytes(data)
        
        # Trenuj dla wszystkich długości kontekstu (0 do order)
        for i in range(len(data)):
            symbol = data[i]
            
            # Konteksty różnej długości
            for ctx_len in range(self.order + 1):
                if i >= ctx_len:
                    context = data[i - ctx_len:i] if ctx_len > 0 else b''
                    self.contexts[context][symbol] += 1
            
            # Statystyki globalne
            self.global_counts[symbol] += 1
            self.total_global += 1
        
        # Statystyki
        num_contexts = len(self.contexts)
        avg_symbols = sum(len(counts) for counts in self.contexts.values()) / max(num_contexts, 1)
        print(f"    Konteksty: {num_contexts:,}")
        print(f"    Średnio symboli/kontekst: {avg_symbols:.1f}")
    
    def start_encoding(self):
        """Resetuje stan do kodowania nowej sekwencji"""
        self.current_context = b''
    
    def get_probabilities(self, context):
        """
        Zwraca rozkład prawdopodobieństwa dla danego kontekstu
        Używa backoff: próbuje pełnego kontekstu, potem krótszego, aż do Order-0
        
        Returns:
            dict: {symbol: (cumulative_low, cumulative_high, total)}
        """
        # Spróbuj od najdłuższego kontekstu do najkrótszego
        for ctx_len in range(len(context), -1, -1):
            test_context = context[-ctx_len:] if ctx_len > 0 else b''
            
            if test_context in self.contexts and self.contexts[test_context]:
                # Znaleziono kontekst
                counts = self.contexts[test_context]
                total = sum(counts.values())
                
                # Zbuduj skumulowany rozkład
                cumulative = 0
                prob_dist = {}
                for symbol in sorted(counts.keys()):
                    count = counts[symbol]
                    prob_dist[symbol] = (cumulative, cumulative + count, total)
                    cumulative += count
                
                return prob_dist, test_context
        
        # Fallback: użyj statystyk globalnych
        cumulative = 0
        prob_dist = {}
        for symbol in sorted(self.global_counts.keys()):
            count = self.global_counts[symbol]
            prob_dist[symbol] = (cumulative, cumulative + count, self.total_global)
            cumulative += count
        
        return prob_dist, b''
    
    def get_range(self, symbol):
        """Zwraca zakres dla symbolu w bieżącym kontekście"""
        prob_dist, used_context = self.get_probabilities(self.current_context[-self.order:])
        
        if symbol in prob_dist:
            low, high, total = prob_dist[symbol]
        else:
            # Symbol nieznany - uniform distribution (nie powinno się zdarzyć po treningu)
            total = 256
            low = symbol
            high = symbol + 1
        
        return low, high, total
    
    def get_total(self):
        """Zwraca całkowitą częstotliwość dla bieżącego kontekstu"""
        prob_dist, _ = self.get_probabilities(self.current_context[-self.order:])
        if prob_dist:
            # Total z pierwszego symbolu (wszystkie mają ten sam total)
            return list(prob_dist.values())[0][2]
        return 256
    
    def get_symbol(self, offset):
        """Zwraca symbol dla danego offsetu w bieżącym kontekście"""
        prob_dist, _ = self.get_probabilities(self.current_context[-self.order:])
        
        for symbol, (low, high, total) in prob_dist.items():
            if low <= offset < high:
                return symbol
        
        # Nie powinno się zdarzyć
        raise ValueError(f"Invalid offset {offset} for context {self.current_context}")
    
    def update_context(self, symbol):
        """Aktualizuje kontekst po zakodowaniu/odkodowaniu symbolu"""
        self.current_context += bytes([symbol])
        if len(self.current_context) > self.order:
            self.current_context = self.current_context[-self.order:]
    
    def serialize(self):
        """Serializuje model (dla dekompresora)"""
        return pickle.dumps({
            'order': self.order,
            'contexts': dict(self.contexts),
            'global_counts': dict(self.global_counts),
            'total_global': self.total_global
        })
    
    @staticmethod
    def deserialize(data):
        """Deserializuje model"""
        state = pickle.loads(data)
        model = ContextModel(order=state['order'])
        model.contexts = defaultdict(lambda: defaultdict(int), state['contexts'])
        model.global_counts = defaultdict(int, state['global_counts'])
        model.total_global = state['total_global']
        return model


class AdaptiveContextModel(ContextModel):
    """
    Wersja adaptacyjna - model aktualizuje się podczas kodowania
    Lepsze dla dużych plików, ale wymaga identycznej sekwencji operacji w koderze i dekoderze
    """
    
    def __init__(self, order=2):
        super().__init__(order)
        self.update_during_coding = True
    
    def train(self, data):
        """W wersji adaptacyjnej możemy zacząć od pustego modelu lub prostego seeda"""
        # Inicjalizuj z uniform distribution
        for i in range(256):
            self.global_counts[i] = 1
        self.total_global = 256
        print(f"    Model adaptacyjny Order-{self.order} (inicjalizacja uniform)")
    
    def update_after_symbol(self, symbol):
        """Aktualizuje model po zakodowaniu symbolu (wywołaj w koderze i dekoderze)"""
        context = self.current_context[-self.order:] if len(self.current_context) >= self.order else self.current_context
        
        # Aktualizuj wszystkie poziomy kontekstu
        for ctx_len in range(self.order + 1):
            if len(context) >= ctx_len:
                ctx = context[-ctx_len:] if ctx_len > 0 else b''
                self.contexts[ctx][symbol] += 1
        
        # Aktualizuj globalne
        self.global_counts[symbol] += 1
        self.total_global += 1
        
        # Aktualizuj kontekst
        self.update_context(symbol)
