#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Sintático para Mini-Java
Implementa análise descendente recursiva baseada na gramática fornecida
"""

from typing import List, Optional, Any
from lexer import Token

class SyntaxError(Exception):
    """Classe para erros sintáticos com informações detalhadas"""
    def __init__(self, message: str, linha: int, coluna: int, token_atual: Token = None, 
                 tokens_esperados: List[str] = None, contexto: str = ""):
        self.message = message
        self.linha = linha
        self.coluna = coluna
        self.token_atual = token_atual
        self.tokens_esperados = tokens_esperados or []
        self.contexto = contexto
    
    def __str__(self):
        resultado = f"ERRO SINTÁTICO na linha {self.linha}, coluna {self.coluna}:\n"
        resultado += f"  {self.message}\n"
        
        if self.token_atual:
            resultado += f"  Token encontrado: {self.token_atual.tipo} ('{self.token_atual.valor}')\n"
        
        if self.tokens_esperados:
            resultado += f"  Tokens esperados: {', '.join(self.tokens_esperados)}\n"
        
        # Adicionar sugestões de correção
        sugestao = self.get_suggestion()
        if sugestao:
            resultado += f"  >> Sugestao: {sugestao}\n"
        
        if self.contexto:
            resultado += f"  Contexto:\n{self.contexto}\n"
        
        return resultado
    
    def get_suggestion(self) -> str:
        """Retorna sugestões de correção baseadas no erro"""
        if not self.token_atual or not self.tokens_esperados:
            return ""
        
        token_atual = self.token_atual.tipo
        tokens_esperados = self.tokens_esperados
        
        # Sugestões específicas baseadas no contexto
        if 'DOUBLE' in tokens_esperados and token_atual == 'ID':
            return "Adicione o tipo 'double' antes do identificador"
        elif 'ASSIGN' in tokens_esperados and token_atual == 'ID':
            return "Use '=' para atribuição ou adicione o tipo antes do identificador"
        elif 'SEMICOLON' in tokens_esperados:
            return "Adicione ';' no final da declaração/comando"
        elif 'LPAREN' in tokens_esperados:
            return "Adicione '(' para abrir parênteses"
        elif 'RPAREN' in tokens_esperados:
            return "Adicione ')' para fechar parênteses"
        elif 'LBRACE' in tokens_esperados:
            return "Adicione '{' para abrir chaves"
        elif 'RBRACE' in tokens_esperados:
            return "Adicione '}' para fechar chaves"
        
        return ""

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
    
    def print_tree(self, indent: int = 0):
        """Imprime a árvore sintática de forma hierárquica"""
        prefix = "  " * indent
        if self.valor:
            print(f"{prefix}{self.tipo}: {self.valor}")
        else:
            print(f"{prefix}{self.tipo}")
        
        for child in self.filhos:
            child.print_tree(indent + 1)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.ast = None
        self.erros = []  # Lista para coletar múltiplos erros
        self.source_lines = []  # Linhas do código fonte para contexto
    
    def parse(self) -> ASTNode:
        """Inicia a análise sintática"""
        self.ast = self.prog()
        if self.current < len(self.tokens) - 1:  # -1 porque o último é EOF
            raise SyntaxError(f"Tokens extras após análise: {self.tokens[self.current:]}")
        return self.ast
    
    def print_ast(self):
        """Imprime a árvore sintática abstrata"""
        if self.ast:
            print("=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===")
            self.ast.print_tree()
        else:
            print("Nenhuma AST disponível. Execute parse() primeiro.")
    
    def print_erros(self):
        """Imprime todos os erros sintáticos encontrados"""
        if self.erros:
            print(f"\n=== ERROS SINTÁTICOS ENCONTRADOS ({len(self.erros)}) ===")
            for i, erro in enumerate(self.erros, 1):
                print(f"\nErro {i}:")
                print(erro)
        else:
            print("Nenhum erro sintático encontrado.")
    
    def set_source_lines(self, lines: List[str]):
        """Define as linhas do código fonte para contexto de erro"""
        self.source_lines = lines
    
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
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message=f"Esperado {expected}, encontrado {token.tipo}",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=expected_types,
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
    
    def get_context(self, linha: int, raio: int = 2) -> str:
        """Retorna contexto ao redor da linha com erro"""
        if not self.source_lines:
            return ""
        
        inicio = max(0, linha - raio - 1)
        fim = min(len(self.source_lines), linha + raio)
        
        contexto = []
        for i in range(inicio, fim):
            prefixo = ">>> " if i + 1 == linha else "    "
            contexto.append(f"{prefixo}{i+1:3d}: {self.source_lines[i]}")
        
        return "\n".join(contexto)
    
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
                # DC -> <VAR> <MAIS_CMDS>
                decl = self.dc()
                node.add_child(decl)
            elif self.match(['IF', 'WHILE']):
                # CMD_COND -> if/while com <CMDS> recursivo
                cmd_cond = self.cmd_cond()
                node.add_child(cmd_cond)
            elif self.match(['SYSTEM', 'ID']):
                # CMD -> System.out.println ou id <RESTO_IDENT>
                cmd = self.cmd()
                node.add_child(cmd)
                # MAIS_CMDS -> ;<CMDS>
                mais_cmds = self.mais_cmds()
                if mais_cmds.filhos:
                    node.add_child(mais_cmds)
            else:
                # λ (lambda) - não há mais comandos
                break
        
        return node
    
    def dc(self) -> ASTNode:
        """DC -> <VAR> <MAIS_CMDS>"""
        node = ASTNode("DC")
        var_node = self.var()
        node.add_child(var_node)
        # MAIS_CMDS -> ;<CMDS>
        self.consume(['SEMICOLON'])  # Obrigatório segundo a gramática
        mais_cmds = self.mais_cmds()
        if mais_cmds.filhos:  # Se há filhos, adiciona
            node.add_child(mais_cmds)
        return node
    
    def mais_cmds(self) -> ASTNode:
        """MAIS_CMDS -> ;<CMDS>"""
        node = ASTNode("MAIS_CMDS")
        if self.match(['SEMICOLON']):
            self.consume(['SEMICOLON'])
            cmds = self.cmds()
            node.add_child(cmds)
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
            token = self.current_token()
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Esperado IF ou WHILE",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['IF', 'WHILE'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
    
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
            token = self.current_token()
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Esperado SYSTEM ou ID",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['SYSTEM', 'ID'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
    
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
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Operador relacional inválido",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['EQUALS', 'NOT_EQUALS', 'GREATER_EQUAL', 'LESS_EQUAL', 'GREATER', 'LESS'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
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
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Fator inválido",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['ID', 'NUMERO_REAL', 'LPAREN'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
        
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
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Operador aditivo inválido",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['PLUS', 'MINUS'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
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
            contexto = self.get_context(token.linha)
            erro = SyntaxError(
                message="Operador multiplicativo inválido",
                linha=token.linha,
                coluna=token.coluna,
                token_atual=token,
                tokens_esperados=['MULTIPLY', 'DIVIDE'],
                contexto=contexto
            )
            self.erros.append(erro)
            raise erro
        return node
