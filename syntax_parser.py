#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Sintático para Mini-Java
Implementa análise descendente recursiva baseada na gramática fornecida
"""

from typing import List, Optional, Any
from lexer import Token

class ASTNode:
    """Nó da Árvore Sintática Abstrata"""
    def __init__(self, tipo: str, valor: str = "", filhos: List['ASTNode'] = None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = filhos or []
        self.token = None  # Token associado (para alguns nós)
    
    def add_child(self, child: 'ASTNode'):
        self.filhos.append(child)
    
    def __repr__(self):
        if self.valor:
            return f"{self.tipo}({self.valor})"
        return self.tipo

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.ast = None
    
    def parse(self) -> ASTNode:
        """Inicia a análise sintática"""
        self.ast = self.prog()
        if self.current < len(self.tokens) - 1:  # -1 porque o último é EOF
            raise SyntaxError(f"Tokens extras após análise: {self.tokens[self.current:]}")
        return self.ast
    
    def current_token(self) -> Token:
        """Retorna o token atual"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF
    
    def peek(self, offset: int = 1) -> Token:
        """Retorna token com offset"""
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        """Avança para o próximo token"""
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        return self.tokens[-1]  # EOF
    
    def match(self, expected_types: List[str]) -> bool:
        """Verifica se o token atual corresponde aos tipos esperados"""
        token = self.current_token()
        return token.tipo in expected_types
    
    def consume(self, expected_types: List[str]) -> Token:
        """Consome token se corresponder aos tipos esperados"""
        token = self.current_token()
        if token.tipo in expected_types:
            return self.advance()
        else:
            expected = " | ".join(expected_types)
            raise SyntaxError(f"Esperado {expected}, encontrado {token.tipo} na linha {token.linha}")
    
    # Regras da gramática
    
    def prog(self) -> ASTNode:
        """PROG -> public class id { public static void main ( String [ ] id ) { <CMDS> } }"""
        node = ASTNode("PROG")
        
        # public class id {
        self.consume(['PUBLIC'])
        self.consume(['CLASS'])
        id_token = self.consume(['ID'])
        node.add_child(ASTNode("CLASS_NAME", id_token.valor))
        self.consume(['LBRACE'])
        
        # public static void main ( String [ ] id ) {
        self.consume(['PUBLIC'])
        self.consume(['STATIC'])
        self.consume(['VOID'])
        self.consume(['MAIN'])
        self.consume(['LPAREN'])
        self.consume(['STRING'])
        self.consume(['LBRACKET'])
        self.consume(['RBRACKET'])
        args_token = self.consume(['ID'])
        node.add_child(ASTNode("ARGS_NAME", args_token.valor))
        self.consume(['RPAREN'])
        self.consume(['LBRACE'])
        
        # <CMDS>
        commands = self.cmds()
        node.add_child(commands)
        
        # } (fechar método main)
        self.consume(['RBRACE'])
        
        # } (fechar classe)
        self.consume(['RBRACE'])
        
        return node
    
    def cmds(self) -> ASTNode:
        """CMDS -> <CMD><MAIS_CMDS> | <CMD_COND><CMDS> | <DC> | λ"""
        node = ASTNode("CMDS")
        
        while not self.match(['RBRACE', 'EOF']):
            if self.match(['DOUBLE']):
                # Declaração de variável
                decl = self.dc()
                node.add_child(decl)
            elif self.match(['IF', 'WHILE']):
                # Comando condicional
                cmd_cond = self.cmd_cond()
                node.add_child(cmd_cond)
            elif self.match(['SYSTEM', 'ID']):
                # Comando simples
                cmd = self.cmd()
                node.add_child(cmd)
                if self.match(['SEMICOLON']):
                    self.consume(['SEMICOLON'])
            else:
                # Não há mais comandos
                break
        
        return node
    
    def dc(self) -> ASTNode:
        """DC -> <VAR> <MAIS_CMDS>"""
        node = ASTNode("DC")
        var_node = self.var()
        node.add_child(var_node)
        # Consumir o ponto e vírgula após a declaração
        if self.match(['SEMICOLON']):
            self.consume(['SEMICOLON'])
        return node
    
    def var(self) -> ASTNode:
        """VAR -> <TIPO> <VARS>"""
        node = ASTNode("VAR")
        tipo_node = self.tipo()
        node.add_child(tipo_node)
        vars_node = self.vars()
        node.add_child(vars_node)
        return node
    
    def vars(self) -> ASTNode:
        """VARS -> id<MAIS_VAR>"""
        node = ASTNode("VARS")
        id_token = self.consume(['ID'])
        node.add_child(ASTNode("ID", id_token.valor))
        mais_var = self.mais_var()
        node.add_child(mais_var)
        return node
    
    def mais_var(self) -> ASTNode:
        """MAIS_VAR -> ,<VARS> | λ"""
        node = ASTNode("MAIS_VAR")
        if self.match(['COMMA']):
            self.consume(['COMMA'])
            vars_node = self.vars()
            node.add_child(vars_node)
        return node
    
    def tipo(self) -> ASTNode:
        """TIPO -> double"""
        node = ASTNode("TIPO")
        self.consume(['DOUBLE'])
        node.valor = "double"
        return node
    
    def cmd_cond(self) -> ASTNode:
        """CMD_COND -> if ( <CONDICAO> ) {<CMDS>} <PFALSA>
                     | while ( <CONDICAO> ) {<CMDS>}"""
        if self.match(['IF']):
            node = ASTNode("IF")
            self.consume(['IF'])
            self.consume(['LPAREN'])
            cond = self.condicao()
            node.add_child(cond)
            self.consume(['RPAREN'])
            self.consume(['LBRACE'])
            cmds = self.cmds()
            node.add_child(cmds)
            self.consume(['RBRACE'])
            pfalsa = self.pfalsa()
            node.add_child(pfalsa)
            return node
        elif self.match(['WHILE']):
            node = ASTNode("WHILE")
            self.consume(['WHILE'])
            self.consume(['LPAREN'])
            cond = self.condicao()
            node.add_child(cond)
            self.consume(['RPAREN'])
            self.consume(['LBRACE'])
            cmds = self.cmds()
            node.add_child(cmds)
            self.consume(['RBRACE'])
            return node
        else:
            raise SyntaxError(f"Esperado IF ou WHILE, encontrado {self.current_token().tipo}")
    
    def cmd(self) -> ASTNode:
        """CMD -> System.out.println (<EXPRESSAO>) 
                 | id <RESTO_IDENT>"""
        if self.match(['SYSTEM']):
            node = ASTNode("PRINTLN")
            self.consume(['SYSTEM'])
            self.consume(['DOT'])
            self.consume(['OUT'])
            self.consume(['DOT'])
            self.consume(['PRINTLN'])
            self.consume(['LPAREN'])
            expr = self.expressao()
            node.add_child(expr)
            self.consume(['RPAREN'])
            return node
        elif self.match(['ID']):
            node = ASTNode("ASSIGN")
            id_token = self.consume(['ID'])
            node.add_child(ASTNode("ID", id_token.valor))
            resto = self.resto_ident()
            node.add_child(resto)
            return node
        else:
            raise SyntaxError(f"Esperado SYSTEM ou ID, encontrado {self.current_token().tipo}")
    
    def pfalsa(self) -> ASTNode:
        """PFALSA -> else { <CMDS> } | λ"""
        node = ASTNode("PFALSA")
        if self.match(['ELSE']):
            self.consume(['ELSE'])
            self.consume(['LBRACE'])
            cmds = self.cmds()
            node.add_child(cmds)
            self.consume(['RBRACE'])
        return node
    
    def resto_ident(self) -> ASTNode:
        """RESTO_IDENT -> = <EXP_IDENT>"""
        node = ASTNode("RESTO_IDENT")
        self.consume(['ASSIGN'])
        exp_ident = self.exp_ident()
        node.add_child(exp_ident)
        return node
    
    def exp_ident(self) -> ASTNode:
        """EXP_IDENT -> <EXPRESSAO> | lerDouble()"""
        if self.match(['LERDOUBLE']):
            node = ASTNode("LERDOUBLE")
            self.consume(['LERDOUBLE'])
            self.consume(['LPAREN'])
            self.consume(['RPAREN'])
            return node
        else:
            return self.expressao()
    
    def condicao(self) -> ASTNode:
        """CONDICAO -> <EXPRESSAO> <RELACAO> <EXPRESSAO>"""
        node = ASTNode("CONDICAO")
        expr1 = self.expressao()
        node.add_child(expr1)
        rel = self.relacao()
        node.add_child(rel)
        expr2 = self.expressao()
        node.add_child(expr2)
        return node
    
    def relacao(self) -> ASTNode:
        """RELACAO -> == | != | >= | <= | > | <"""
        node = ASTNode("RELACAO")
        token = self.current_token()
        if token.tipo in ['EQUALS', 'NOT_EQUALS', 'GREATER_EQUAL', 'LESS_EQUAL', 'GREATER', 'LESS']:
            node.valor = token.valor
            self.advance()
        else:
            raise SyntaxError(f"Operador relacional inválido: {token.tipo}")
        return node
    
    def expressao(self) -> ASTNode:
        """EXPRESSAO -> <TERMO> <OUTROS_TERMOS>"""
        node = ASTNode("EXPRESSAO")
        termo = self.termo()
        node.add_child(termo)
        outros = self.outros_termos()
        node.add_child(outros)
        return node
    
    def termo(self) -> ASTNode:
        """TERMO -> <OP_UN> <FATOR> <MAIS_FATORES>"""
        node = ASTNode("TERMO")
        op_un = self.op_un()
        node.add_child(op_un)
        fator = self.fator()
        node.add_child(fator)
        mais_fatores = self.mais_fatores()
        node.add_child(mais_fatores)
        return node
    
    def op_un(self) -> ASTNode:
        """OP_UN -> - | λ"""
        node = ASTNode("OP_UN")
        if self.match(['MINUS']):
            node.valor = "-"
            self.advance()
        else:
            node.valor = ""
        return node
    
    def fator(self) -> ASTNode:
        """FATOR -> id | numero_real | (<EXPRESSAO>)"""
        node = ASTNode("FATOR")
        token = self.current_token()
        
        if token.tipo == 'ID':
            node.add_child(ASTNode("ID", token.valor))
            self.advance()
        elif token.tipo == 'NUMERO_REAL':
            node.add_child(ASTNode("NUMERO_REAL", token.valor))
            self.advance()
        elif token.tipo == 'LPAREN':
            self.advance()
            expr = self.expressao()
            node.add_child(expr)
            self.consume(['RPAREN'])
        else:
            raise SyntaxError(f"Fator inválido: {token.tipo}")
        
        return node
    
    def outros_termos(self) -> ASTNode:
        """OUTROS_TERMOS -> <OP_AD> <TERMO> <OUTROS_TERMOS> | λ"""
        node = ASTNode("OUTROS_TERMOS")
        if self.match(['PLUS', 'MINUS']):
            op_ad = self.op_ad()
            node.add_child(op_ad)
            termo = self.termo()
            node.add_child(termo)
            outros = self.outros_termos()
            node.add_child(outros)
        return node
    
    def op_ad(self) -> ASTNode:
        """OP_AD -> + | -"""
        node = ASTNode("OP_AD")
        token = self.current_token()
        if token.tipo in ['PLUS', 'MINUS']:
            node.valor = token.valor
            self.advance()
        else:
            raise SyntaxError(f"Operador aditivo inválido: {token.tipo}")
        return node
    
    def mais_fatores(self) -> ASTNode:
        """MAIS_FATORES -> <OP_MUL> <FATOR> <MAIS_FATORES> | λ"""
        node = ASTNode("MAIS_FATORES")
        if self.match(['MULTIPLY', 'DIVIDE']):
            op_mul = self.op_mul()
            node.add_child(op_mul)
            fator = self.fator()
            node.add_child(fator)
            mais_fatores = self.mais_fatores()
            node.add_child(mais_fatores)
        return node
    
    def op_mul(self) -> ASTNode:
        """OP_MUL -> * | /"""
        node = ASTNode("OP_MUL")
        token = self.current_token()
        if token.tipo in ['MULTIPLY', 'DIVIDE']:
            node.valor = token.valor
            self.advance()
        else:
            raise SyntaxError(f"Operador multiplicativo inválido: {token.tipo}")
        return node
