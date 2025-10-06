#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Léxico para Mini-Java
Reconhece tokens da linguagem Mini-Java
"""

import re
from typing import List, Tuple, Optional

class Token:
    def __init__(self, tipo: str, valor: str, linha: int, coluna: int):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna
    
    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', linha={self.linha}, coluna={self.coluna})"

class Lexer:
    def __init__(self):
        # Definir padrões de tokens
        self.patterns = [
            # Palavras reservadas
            ('PUBLIC', r'\bpublic\b'),
            ('CLASS', r'\bclass\b'),
            ('STATIC', r'\bstatic\b'),
            ('VOID', r'\bvoid\b'),
            ('MAIN', r'\bmain\b'),
            ('STRING', r'\bString\b'),
            ('DOUBLE', r'\bdouble\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('WHILE', r'\bwhile\b'),
            ('SYSTEM', r'\bSystem\b'),
            ('OUT', r'\bout\b'),
            ('PRINTLN', r'\bprintln\b'),
            ('LERDOUBLE', r'\blerDouble\b'),
            
            # Operadores e símbolos
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('ASSIGN', r'='),
            ('EQUALS', r'=='),
            ('NOT_EQUALS', r'!='),
            ('GREATER_EQUAL', r'>='),
            ('LESS_EQUAL', r'<='),
            ('GREATER', r'>'),
            ('LESS', r'<'),
            
            # Delimitadores
            ('SEMICOLON', r';'),
            ('COMMA', r','),
            ('DOT', r'\.'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LBRACKET', r'\['),
            ('RBRACKET', r'\]'),
            
            # Literais
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO_REAL', r'\d+\.?\d*'),
            
            # Comentários e espaços (serão ignorados)
            ('COMMENT', r'//.*'),
            ('WHITESPACE', r'\s+'),
        ]
        
        # Compilar padrões regex
        self.compiled_patterns = [(nome, re.compile(pattern)) for nome, pattern in self.patterns]
    
    def tokenize(self, source_code: str) -> List[Token]:
        """Tokeniza o código fonte"""
        tokens = []
        lines = source_code.split('\n')
        
        for linha_num, line in enumerate(lines, 1):
            coluna = 0
            while coluna < len(line):
                # Tentar encontrar um padrão que corresponda
                match = None
                for token_type, pattern in self.compiled_patterns:
                    match = pattern.match(line, coluna)
                    if match:
                        valor = match.group(0)
                        
                        # Ignorar comentários e espaços em branco
                        if token_type in ['COMMENT', 'WHITESPACE']:
                            coluna = match.end()
                            break
                        
                        # Criar token
                        token = Token(token_type, valor, linha_num, coluna + 1)
                        tokens.append(token)
                        coluna = match.end()
                        break
                
                if not match:
                    # Caractere não reconhecido
                    char = line[coluna]
                    raise SyntaxError(f"Caractere não reconhecido '{char}' na linha {linha_num}, coluna {coluna + 1}")
        
        # Adicionar token EOF
        tokens.append(Token('EOF', '', len(lines), 0))
        return tokens
    
    def print_tokens(self, tokens: List[Token]):
        """Imprime lista de tokens (para debug)"""
        print("Tokens encontrados:")
        for token in tokens:
            print(f"  {token}")
