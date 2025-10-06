#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Semântico para Mini-Java
Verifica regras semânticas como declaração de variáveis e tipos
"""

from typing import Dict, Set
from syntax_parser import ASTNode

class SymbolTable:
    """Tabela de símbolos para variáveis"""
    def __init__(self):
        self.symbols: Dict[str, str] = {}  # nome -> tipo
    
    def declare(self, name: str, var_type: str):
        """Declara uma nova variável"""
        if name in self.symbols:
            raise SemanticError(f"Variável '{name}' já foi declarada")
        self.symbols[name] = var_type
    
    def lookup(self, name: str) -> str:
        """Busca uma variável na tabela"""
        if name not in self.symbols:
            raise SemanticError(f"Variável '{name}' não foi declarada")
        return self.symbols[name]
    
    def exists(self, name: str) -> bool:
        """Verifica se uma variável existe"""
        return name in self.symbols

class SemanticError(Exception):
    """Exceção para erros semânticos"""
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, ast: ASTNode):
        """Inicia a análise semântica"""
        self.errors = []
        try:
            self.visit_prog(ast)
        except SemanticError as e:
            self.errors.append(str(e))
        
        if self.errors:
            raise SemanticError("Erros semânticos encontrados:\n" + "\n".join(self.errors))
    
    def visit_prog(self, node: ASTNode):
        """Visita nó PROG"""
        if node.tipo != "PROG":
            return
        
        # Visitar declarações de variáveis e comandos
        for child in node.filhos:
            if child.tipo == "CMDS":
                self.visit_cmds(child)
    
    def visit_cmds(self, node: ASTNode):
        """Visita nó CMDS"""
        for child in node.filhos:
            if child.tipo == "DC":
                self.visit_dc(child)
            elif child.tipo in ["IF", "WHILE"]:
                self.visit_cmd_cond(child)
            elif child.tipo == "PRINTLN":
                self.visit_println(child)
            elif child.tipo == "ASSIGN":
                self.visit_assign(child)
    
    def visit_dc(self, node: ASTNode):
        """Visita nó DC (declaração de variável)"""
        var_node = node.filhos[0]  # VAR
        tipo_node = var_node.filhos[0]  # TIPO
        vars_node = var_node.filhos[1]  # VARS
        
        var_type = tipo_node.valor  # "double"
        self.visit_vars(vars_node, var_type)
    
    def visit_vars(self, node: ASTNode, var_type: str):
        """Visita nó VARS e declara variáveis"""
        # Primeira variável
        id_node = node.filhos[0]
        var_name = id_node.valor
        self.symbol_table.declare(var_name, var_type)
        
        # Outras variáveis (se houver)
        if len(node.filhos) > 1:
            mais_var = node.filhos[1]
            self.visit_mais_vars(mais_var, var_type)
    
    def visit_mais_vars(self, node: ASTNode, var_type: str):
        """Visita nó MAIS_VAR"""
        if node.filhos:  # Se não for λ
            vars_node = node.filhos[0]
            self.visit_vars(vars_node, var_type)
    
    def visit_cmd_cond(self, node: ASTNode):
        """Visita comando condicional (IF ou WHILE)"""
        if node.tipo in ["IF", "WHILE"]:
            # Verificar condição
            cond_node = node.filhos[0]
            self.visit_condicao(cond_node)
            
            # Verificar comandos dentro do bloco
            cmds_node = node.filhos[1]
            self.visit_cmds(cmds_node)
            
            # Se for IF, verificar else
            if node.tipo == "IF" and len(node.filhos) > 2:
                pfalsa_node = node.filhos[2]
                self.visit_pfalsa(pfalsa_node)
    
    def visit_condicao(self, node: ASTNode):
        """Visita nó CONDICAO"""
        # Verificar expressões da condição
        expr1 = node.filhos[0]
        expr2 = node.filhos[2]
        
        self.visit_expressao(expr1)
        self.visit_expressao(expr2)
    
    def visit_println(self, node: ASTNode):
        """Visita comando System.out.println"""
        expr_node = node.filhos[0]
        self.visit_expressao(expr_node)
    
    def visit_assign(self, node: ASTNode):
        """Visita atribuição de variável"""
        id_node = node.filhos[0]
        var_name = id_node.valor
        
        # Verificar se variável foi declarada
        if not self.symbol_table.exists(var_name):
            raise SemanticError(f"Variável '{var_name}' não foi declarada")
        
        # Verificar expressão do lado direito
        resto_ident = node.filhos[1]
        self.visit_resto_ident(resto_ident)
    
    def visit_resto_ident(self, node: ASTNode):
        """Visita RESTO_IDENT"""
        exp_ident = node.filhos[0]
        self.visit_exp_ident(exp_ident)
    
    def visit_exp_ident(self, node: ASTNode):
        """Visita EXP_IDENT"""
        if node.tipo == "LERDOUBLE":
            return  # lerDouble() não precisa de verificação
        else:
            self.visit_expressao(node)
    
    def visit_pfalsa(self, node: ASTNode):
        """Visita PFALSA (else)"""
        if node.filhos:  # Se não for λ
            cmds_node = node.filhos[0]
            self.visit_cmds(cmds_node)
    
    def visit_expressao(self, node: ASTNode):
        """Visita EXPRESSAO"""
        if node.tipo == "EXPRESSAO":
            termo = node.filhos[0]
            self.visit_termo(termo)
            outros = node.filhos[1]
            self.visit_outros_termos(outros)
        elif node.tipo == "TERMO":
            self.visit_termo(node)
        elif node.tipo == "FATOR":
            self.visit_fator(node)
        else:
            # Visitar recursivamente
            for child in node.filhos:
                self.visit_expressao(child)
    
    def visit_termo(self, node: ASTNode):
        """Visita TERMO"""
        fator = node.filhos[1]  # Pular OP_UN
        self.visit_fator(fator)
        mais_fatores = node.filhos[2]
        self.visit_mais_fatores(mais_fatores)
    
    def visit_fator(self, node: ASTNode):
        """Visita FATOR"""
        if node.filhos:
            child = node.filhos[0]
            if child.tipo == "ID":
                var_name = child.valor
                if not self.symbol_table.exists(var_name):
                    raise SemanticError(f"Variável '{var_name}' não foi declarada")
            elif child.tipo == "EXPRESSAO":
                self.visit_expressao(child)
            # NUMERO_REAL não precisa de verificação
    
    def visit_outros_termos(self, node: ASTNode):
        """Visita OUTROS_TERMOS"""
        if node.filhos:  # Se não for λ
            termo = node.filhos[1]
            self.visit_termo(termo)
            outros = node.filhos[2]
            self.visit_outros_termos(outros)
    
    def visit_mais_fatores(self, node: ASTNode):
        """Visita MAIS_FATORES"""
        if node.filhos:  # Se não for λ
            fator = node.filhos[1]
            self.visit_fator(fator)
            mais_fatores = node.filhos[2]
            self.visit_mais_fatores(mais_fatores)
