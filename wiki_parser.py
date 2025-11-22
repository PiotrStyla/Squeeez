#!/usr/bin/env python3
"""
Parser struktury MediaWiki XML do wielokanałowego modelowania
Rozbija tekst na różne "kanały" (nagłówki, linki, treść, etc.)
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

class TokenType(Enum):
    """Typy tokenów w strukturze Wiki"""
    HEADING = 1          # == Nagłówek ==
    LINK = 2             # [[Artykuł]] lub [[Artykuł|tekst]]
    TEMPLATE = 3         # {{Template|param=val}}
    XML_TAG = 4          # <tag>...</tag>
    ENTITY = 5           # &nbsp; &amp; etc.
    PLAIN_TEXT = 6       # Zwykły tekst
    NEWLINE = 7          # \n
    SPECIAL = 8          # Inne specjalne znaki

@dataclass
class Token:
    """Token z typem i zawartością"""
    type: TokenType
    content: bytes
    context: str = ""    # Dodatkowy kontekst (np. poziom nagłówka, nazwa template)

class WikiParser:
    """
    Parser struktury MediaWiki
    Rozbija strumień bajtów na tokeny z typami
    """
    
    def __init__(self):
        # Regex patterns (na stringach, potem konwertujemy)
        self.heading_pattern = re.compile(rb'(={2,6})([^=]+)\1')
        self.link_pattern = re.compile(rb'\[\[([^\]|]+)(\|[^\]]+)?\]\]')
        self.template_pattern = re.compile(rb'\{\{([^}]+)\}\}')
        self.xml_tag_pattern = re.compile(rb'<(/?)(\w+)([^>]*)>')
        self.entity_pattern = re.compile(rb'&[a-zA-Z]+;|&#\d+;')
        
    def tokenize(self, data: bytes) -> List[Token]:
        """
        Rozbija dane na tokeny
        
        Args:
            data: surowe bajty z pliku enwik
        
        Returns:
            Lista tokenów
        """
        tokens = []
        pos = 0
        
        while pos < len(data):
            # Sprawdź nagłówki
            match = self.heading_pattern.match(data, pos)
            if match:
                level = len(match.group(1))
                content = match.group(2)
                tokens.append(Token(
                    type=TokenType.HEADING,
                    content=content.strip(),
                    context=f"h{level}"
                ))
                pos = match.end()
                continue
            
            # Sprawdź linki
            match = self.link_pattern.match(data, pos)
            if match:
                target = match.group(1)
                tokens.append(Token(
                    type=TokenType.LINK,
                    content=target,
                    context="link"
                ))
                pos = match.end()
                continue
            
            # Sprawdź template
            match = self.template_pattern.match(data, pos)
            if match:
                content = match.group(1)
                tokens.append(Token(
                    type=TokenType.TEMPLATE,
                    content=content,
                    context="template"
                ))
                pos = match.end()
                continue
            
            # Sprawdź XML tag
            match = self.xml_tag_pattern.match(data, pos)
            if match:
                closing = match.group(1)
                tagname = match.group(2)
                tokens.append(Token(
                    type=TokenType.XML_TAG,
                    content=tagname,
                    context="close" if closing else "open"
                ))
                pos = match.end()
                continue
            
            # Sprawdź entity
            match = self.entity_pattern.match(data, pos)
            if match:
                tokens.append(Token(
                    type=TokenType.ENTITY,
                    content=match.group(0),
                    context="entity"
                ))
                pos = match.end()
                continue
            
            # Newline
            if data[pos:pos+1] == b'\n':
                tokens.append(Token(
                    type=TokenType.NEWLINE,
                    content=b'\n'
                ))
                pos += 1
                continue
            
            # Specjalne znaki (markup)
            if data[pos:pos+1] in b"*#:;'":
                tokens.append(Token(
                    type=TokenType.SPECIAL,
                    content=data[pos:pos+1]
                ))
                pos += 1
                continue
            
            # Plain text - zbieraj do następnego specjalnego znaku
            start = pos
            while pos < len(data):
                ch = data[pos:pos+1]
                # Zatrzymaj się na początku specjalnych struktur
                if ch in b'\n*#:;\'[{<&=' or data[pos:pos+2] in [b'[[', b'{{', b'==']:
                    break
                pos += 1
            
            if pos > start:
                tokens.append(Token(
                    type=TokenType.PLAIN_TEXT,
                    content=data[start:pos]
                ))
        
        return tokens
    
    def tokens_to_channels(self, tokens: List[Token]) -> dict:
        """
        Konwertuje tokeny na osobne kanały
        
        Returns:
            dict z kluczami: 'heading', 'link', 'template', 'text', 'structure'
        """
        channels = {
            'heading': bytearray(),
            'link': bytearray(),
            'template': bytearray(),
            'text': bytearray(),
            'structure': bytearray(),  # Metadane struktury
        }
        
        for token in tokens:
            if token.type == TokenType.HEADING:
                channels['heading'].extend(token.content)
                channels['heading'].append(ord('\n'))
            elif token.type == TokenType.LINK:
                channels['link'].extend(token.content)
                channels['link'].append(ord('\n'))
            elif token.type == TokenType.TEMPLATE:
                channels['template'].extend(token.content)
                channels['template'].append(ord('\n'))
            elif token.type == TokenType.PLAIN_TEXT:
                channels['text'].extend(token.content)
            elif token.type in [TokenType.XML_TAG, TokenType.ENTITY, TokenType.SPECIAL, TokenType.NEWLINE]:
                channels['structure'].extend(token.content)
        
        # Konwertuj na bytes
        return {k: bytes(v) for k, v in channels.items()}
    
    def analyze_structure(self, data: bytes, max_bytes: int = 100000) -> dict:
        """
        Analizuje strukturę fragmentu danych
        
        Returns:
            Statystyki o tokenach
        """
        subset = data[:max_bytes]
        tokens = self.tokenize(subset)
        
        stats = {
            'total_tokens': len(tokens),
            'by_type': {},
            'total_bytes': len(subset),
            'bytes_by_type': {}
        }
        
        for token in tokens:
            type_name = token.type.name
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1
            stats['bytes_by_type'][type_name] = stats['bytes_by_type'].get(type_name, 0) + len(token.content)
        
        return stats

def demo():
    """Demonstracja parsera"""
    print("=" * 70)
    print("WIKI PARSER - Demonstracja")
    print("=" * 70)
    
    # Przykładowy fragment Wiki
    sample = b"""<mediawiki>
  <page>
    <title>Artificial intelligence</title>
    <text>
'''Artificial intelligence''' ('''AI''') is the field of [[computer science]].

==History==
The field has a long history. See [[Alan Turing]] and the [[Turing test]].

===Early work===
In 1956, [[John McCarthy (computer scientist)|John McCarthy]] organized the {{cite conference|name=Dartmouth}}.

The term &quot;AI&quot; was coined at this conference.
    </text>
  </page>
</mediawiki>"""
    
    parser = WikiParser()
    
    print("\n[1] Tokenizacja...")
    tokens = parser.tokenize(sample)
    
    print(f"    Znaleziono {len(tokens)} tokenów")
    print("\n    Pierwsze 15 tokenów:")
    for i, token in enumerate(tokens[:15]):
        content_preview = token.content[:30] if len(token.content) <= 30 else token.content[:27] + b'...'
        print(f"      {i+1:2d}. {token.type.name:<15} {content_preview}")
    
    print("\n[2] Podział na kanały...")
    channels = parser.tokens_to_channels(tokens)
    
    for name, data in channels.items():
        if data:
            print(f"    {name:<12}: {len(data):>6} bajtów")
    
    print("\n[3] Analiza struktury...")
    stats = parser.analyze_structure(sample)
    
    print(f"    Wszystkie tokeny: {stats['total_tokens']}")
    print(f"    Bajty całkowite:  {stats['total_bytes']}")
    print("\n    Rozkład tokenów:")
    for type_name, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        bytes_count = stats['bytes_by_type'][type_name]
        percent = (bytes_count / stats['total_bytes']) * 100
        print(f"      {type_name:<15}: {count:>4} tokenów, {bytes_count:>6} bajtów ({percent:>5.1f}%)")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    demo()
