#!/usr/bin/env python3
"""
Prosty arithmetic coder - fundament kompresji Hutter Prize
Implementacja oparta na zakresach całkowitoliczbowych (integer arithmetic coding)
"""

class ArithmeticEncoder:
    """Encoder arytmetyczny z precyzją całkowitoliczbową"""
    
    def __init__(self, precision_bits=32):
        self.precision_bits = precision_bits
        self.full = 1 << precision_bits  # 2^precision_bits
        self.half = self.full >> 1
        self.quarter = self.half >> 1
        self.three_quarters = self.half + self.quarter
        
    def encode(self, data, freq_model):
        """
        Koduje dane używając modelu częstotliwości
        
        Args:
            data: lista symboli do zakodowania
            freq_model: model zwracający (low, high, total) dla każdego symbolu
        
        Returns:
            bytes: zakodowane dane
        """
        output_bits = []
        low = 0
        high = self.full - 1
        pending_bits = 0
        
        for symbol in data:
            # Pobierz częstotliwości z modelu
            sym_low, sym_high, total = freq_model.get_range(symbol)
            
            # Aktualizuj zakres
            range_size = high - low + 1
            high = low + (range_size * sym_high // total) - 1
            low = low + (range_size * sym_low // total)
            
            # Normalizacja - wypychanie bitów
            while True:
                if high < self.half:
                    # Górna połowa zakresu poniżej połowy
                    output_bits.append(0)
                    for _ in range(pending_bits):
                        output_bits.append(1)
                    pending_bits = 0
                elif low >= self.half:
                    # Dolna połowa zakresu powyżej połowy
                    output_bits.append(1)
                    for _ in range(pending_bits):
                        output_bits.append(0)
                    pending_bits = 0
                    low -= self.half
                    high -= self.half
                elif low >= self.quarter and high < self.three_quarters:
                    # Środkowa część zakresu
                    pending_bits += 1
                    low -= self.quarter
                    high -= self.quarter
                else:
                    break
                
                # Przesunięcie (podwojenie zakresu)
                low = 2 * low
                high = 2 * high + 1
        
        # Wypychanie ostatnich bitów
        pending_bits += 1
        if low < self.quarter:
            output_bits.append(0)
            for _ in range(pending_bits):
                output_bits.append(1)
        else:
            output_bits.append(1)
            for _ in range(pending_bits):
                output_bits.append(0)
        
        # Konwersja bitów na bajty
        return self._bits_to_bytes(output_bits)
    
    def decode(self, encoded_bytes, freq_model, length):
        """
        Dekoduje dane
        
        Args:
            encoded_bytes: zakodowane dane
            freq_model: model częstotliwości
            length: liczba symboli do odkodowania
        
        Returns:
            list: odkodowane symbole
        """
        input_bits = self._bytes_to_bits(encoded_bytes)
        bit_index = 0
        
        # Inicjalizacja value z pierwszych precision_bits bitów
        value = 0
        for _ in range(self.precision_bits):
            if bit_index < len(input_bits):
                value = (value << 1) | input_bits[bit_index]
                bit_index += 1
            else:
                value = value << 1
        
        low = 0
        high = self.full - 1
        output = []
        
        for _ in range(length):
            # Znajdź symbol
            range_size = high - low + 1
            total = freq_model.get_total()
            offset = ((value - low + 1) * total - 1) // range_size
            
            symbol = freq_model.get_symbol(offset)
            output.append(symbol)
            
            # Aktualizuj zakres
            sym_low, sym_high, total = freq_model.get_range(symbol)
            high = low + (range_size * sym_high // total) - 1
            low = low + (range_size * sym_low // total)
            
            # Normalizacja
            while True:
                if high < self.half:
                    pass
                elif low >= self.half:
                    low -= self.half
                    high -= self.half
                    value -= self.half
                elif low >= self.quarter and high < self.three_quarters:
                    low -= self.quarter
                    high -= self.quarter
                    value -= self.quarter
                else:
                    break
                
                low = 2 * low
                high = 2 * high + 1
                if bit_index < len(input_bits):
                    value = (2 * value) | input_bits[bit_index]
                    bit_index += 1
                else:
                    value = 2 * value
        
        return output
    
    def _bits_to_bytes(self, bits):
        """Konwertuje listę bitów na bajty"""
        # Dopełnij do pełnych bajtów
        while len(bits) % 8 != 0:
            bits.append(0)
        
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            bytes_list.append(byte)
        
        return bytes(bytes_list)
    
    def _bytes_to_bits(self, data):
        """Konwertuje bajty na listę bitów"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits


class FrequencyModel:
    """Model częstotliwości Order-0 (statyczny)"""
    
    def __init__(self):
        self.symbol_to_range = {}
        self.offset_to_symbol = {}
        self.total_freq = 0
    
    def build_from_data(self, data):
        """Buduje model na podstawie danych treningowych"""
        # Zlicz częstotliwości
        freq_count = {}
        for symbol in data:
            freq_count[symbol] = freq_count.get(symbol, 0) + 1
        
        # Zbuduj skumulowane zakresy
        cumulative = 0
        sorted_symbols = sorted(freq_count.keys())
        
        for symbol in sorted_symbols:
            freq = freq_count[symbol]
            self.symbol_to_range[symbol] = (cumulative, cumulative + freq)
            
            # Mapowanie offset->symbol
            for offset in range(cumulative, cumulative + freq):
                self.offset_to_symbol[offset] = symbol
            
            cumulative += freq
        
        self.total_freq = cumulative
    
    def get_range(self, symbol):
        """Zwraca (low, high, total) dla symbolu"""
        low, high = self.symbol_to_range[symbol]
        return low, high, self.total_freq
    
    def get_total(self):
        """Zwraca całkowitą częstotliwość"""
        return self.total_freq
    
    def get_symbol(self, offset):
        """Zwraca symbol dla danego offsetu"""
        return self.offset_to_symbol[offset]
    
    def serialize(self):
        """Serializuje model do bajtów (potrzebne do dekompresji)"""
        import pickle
        return pickle.dumps({
            'symbol_to_range': self.symbol_to_range,
            'offset_to_symbol': self.offset_to_symbol,
            'total_freq': self.total_freq
        })
    
    @staticmethod
    def deserialize(data):
        """Deserializuje model"""
        import pickle
        state = pickle.loads(data)
        model = FrequencyModel()
        model.symbol_to_range = state['symbol_to_range']
        model.offset_to_symbol = state['offset_to_symbol']
        model.total_freq = state['total_freq']
        return model
