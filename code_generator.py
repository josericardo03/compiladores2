#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Código Objeto para Mini-Java
Gera código para a máquina virtual hipotética baseado no exemplo fornecido
"""

from typing import List, Dict
from syntax_parser import ASTNode

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.label_counter = 0
        self.var_addresses = {}  # nome -> endereço
        self.next_address = 0
        
        # Instruções da máquina virtual
        self.instructions = {
            'INPP': 'Inicializar programa',
            'ALME': 'Alocar memória',
            'CRCT': 'Carregar constante',
            'CRVL': 'Carregar valor de variável',
            'ARMZ': 'Armazenar valor',
            'LEIT': 'Ler valor',
            'IMPR': 'Imprimir valor',
            'CPMA': 'Comparar maior',
            'CPME': 'Comparar menor',
            'CPIG': 'Comparar igual',
            'CDES': 'Comparar diferente',
            'CPMI': 'Comparar menor ou igual',
            'CPMI': 'Comparar maior ou igual',
            'SOMA': 'Somar',
            'SUBT': 'Subtrair',
            'MULT': 'Multiplicar',
            'DIVI': 'Dividir',
            'INVE': 'Inverter sinal',
            'CONJ': 'Conjunção (AND)',
            'DISJ': 'Disjunção (OR)',
            'NEGA': 'Negação',
            'CMME': 'Copiar maior',
            'CMMA': 'Copiar menor',
            'CMIG': 'Copiar igual',
            'CMDG': 'Copiar diferente',
            'CMLE': 'Copiar menor ou igual',
            'CMAG': 'Copiar maior ou igual',
            'NADA': 'Não fazer nada',
            'PARA': 'Parar execução',
            'DSVF': 'Desvio se falso',
            'DSVI': 'Desvio incondicional'
        }
    
    def generate(self, ast: ASTNode) -> List[str]:
        """Gera código objeto a partir da AST"""
        self.code = []
        self.var_addresses = {}
        self.next_address = 0
        
        # Inicializar programa
        self.emit('INPP')
        
        # Processar AST
        self.visit_prog(ast)
        
        # Finalizar programa
        self.emit('PARA')
        
        return self.code
    
    def emit(self, instruction: str, operand: str = ''):
        """Emite uma instrução"""
        if operand:
            self.code.append(f"{instruction} {operand}")
        else:
            self.code.append(instruction)
    
    def new_label(self) -> int:
        """Gera novo label"""
        self.label_counter += 1
        return self.label_counter
    
    def get_var_address(self, var_name: str) -> int:
        """Obtém endereço de uma variável"""
        if var_name not in self.var_addresses:
            self.var_addresses[var_name] = self.next_address
            self.next_address += 1
        return self.var_addresses[var_name]
    
    def visit_prog(self, node: ASTNode):
        """Visita nó PROG"""
        if node.tipo != "PROG":
            return
        
        # Alocar espaço para variáveis
        self.allocate_variables(node)
        
        # Processar comandos
        for child in node.filhos:
            if child.tipo == "CMDS":
                self.visit_cmds(child)
    
    def allocate_variables(self, node: ASTNode):
        """Aloca espaço para todas as variáveis"""
        # Primeiro passagem: coletar todas as variáveis
        variables = []
        self.collect_variables(node, variables)
        
        # Alocar memória para cada variável
        for var_name in variables:
            self.emit('ALME', '1')
    
    def collect_variables(self, node: ASTNode, variables: List[str]):
        """Coleta todas as variáveis declaradas"""
        if node.tipo == "VAR":
            tipo_node = node.filhos[0]
            vars_node = node.filhos[1]
            self.collect_vars(vars_node, variables)
        elif node.tipo == "ASSIGN":
            id_node = node.filhos[0]
            var_name = id_node.valor
            if var_name not in variables:
                variables.append(var_name)
        elif node.tipo == "FATOR" and node.filhos and node.filhos[0].tipo == "ID":
            var_name = node.filhos[0].valor
            if var_name not in variables:
                variables.append(var_name)
        
        # Visitar filhos recursivamente
        for child in node.filhos:
            self.collect_variables(child, variables)
    
    def collect_vars(self, node: ASTNode, variables: List[str]):
        """Coleta variáveis do nó VARS"""
        if node.tipo == "VARS":
            id_node = node.filhos[0]
            var_name = id_node.valor
            variables.append(var_name)
            
            if len(node.filhos) > 1:
                mais_var = node.filhos[1]
                self.collect_mais_vars(mais_var, variables)
    
    def collect_mais_vars(self, node: ASTNode, variables: List[str]):
        """Coleta variáveis do nó MAIS_VAR"""
        if node.filhos:  # Se não for λ
            vars_node = node.filhos[0]
            self.collect_vars(vars_node, variables)
    
    def visit_cmds(self, node: ASTNode):
        """Visita nó CMDS"""
        for child in node.filhos:
            if child.tipo == "DC":
                # Declarações já foram processadas na alocação
                pass
            elif child.tipo == "IF":
                self.visit_if(child)
            elif child.tipo == "WHILE":
                self.visit_while(child)
            elif child.tipo == "PRINTLN":
                self.visit_println(child)
            elif child.tipo == "ASSIGN":
                self.visit_assign(child)
    
    def visit_if(self, node: ASTNode):
        """Visita comando IF"""
        cond_node = node.filhos[0]  # CONDICAO
        cmds_true = node.filhos[1]  # CMDS (bloco if)
        pfalsa_node = node.filhos[2]  # PFALSA (else)
        
        # Gerar condição
        self.visit_condicao(cond_node)
        
        # Desvio se falso para else (ou fim se não houver else)
        else_label = self.new_label()
        if pfalsa_node.filhos:  # Se há else
            self.emit('DSVF', str(else_label))
            self.visit_cmds(cmds_true)
            end_label = self.new_label()
            self.emit('DSVI', str(end_label))
            self.emit_label(else_label)
            self.visit_pfalsa(pfalsa_node)
            self.emit_label(end_label)
        else:
            end_label = self.new_label()
            self.emit('DSVF', str(end_label))
            self.visit_cmds(cmds_true)
            self.emit_label(end_label)
    
    def visit_while(self, node: ASTNode):
        """Visita comando WHILE"""
        cond_node = node.filhos[0]  # CONDICAO
        cmds_node = node.filhos[1]  # CMDS
        
        loop_label = self.new_label()
        end_label = self.new_label()
        
        self.emit_label(loop_label)
        self.visit_condicao(cond_node)
        self.emit('DSVF', str(end_label))
        self.visit_cmds(cmds_node)
        self.emit('DSVI', str(loop_label))
        self.emit_label(end_label)
    
    def visit_condicao(self, node: ASTNode):
        """Visita CONDICAO"""
        expr1 = node.filhos[0]
        rel = node.filhos[1]
        expr2 = node.filhos[2]
        
        # Avaliar expressões
        self.visit_expressao(expr1)
        self.visit_expressao(expr2)
        
        # Gerar operação relacional
        self.visit_relacao(rel)
    
    def visit_relacao(self, node: ASTNode):
        """Visita RELACAO"""
        op = node.valor
        if op == '>':
            self.emit('CPMA')
        elif op == '<':
            self.emit('CPME')
        elif op == '==':
            self.emit('CPIG')
        elif op == '!=':
            self.emit('CDES')
        elif op == '>=':
            self.emit('CPMI')  # Maior ou igual
        elif op == '<=':
            self.emit('CPME')  # Menor ou igual
    
    def visit_println(self, node: ASTNode):
        """Visita System.out.println"""
        expr_node = node.filhos[0]
        self.visit_expressao(expr_node)
        self.emit('IMPR')
    
    def visit_assign(self, node: ASTNode):
        """Visita atribuição"""
        id_node = node.filhos[0]
        var_name = id_node.valor
        resto_ident = node.filhos[1]
        
        # Avaliar expressão
        self.visit_exp_ident(resto_ident.filhos[0])
        
        # Armazenar na variável
        address = self.get_var_address(var_name)
        self.emit('ARMZ', str(address))
    
    def visit_exp_ident(self, node: ASTNode):
        """Visita EXP_IDENT"""
        if node.tipo == "LERDOUBLE":
            self.emit('LEIT')
        else:
            self.visit_expressao(node)
    
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
    
    def visit_termo(self, node: ASTNode):
        """Visita TERMO"""
        op_un = node.filhos[0]
        fator = node.filhos[1]
        mais_fatores = node.filhos[2]
        
        # Visitar fator
        self.visit_fator(fator)
        
        # Aplicar operador unário se houver
        if op_un.valor == '-':
            self.emit('INVE')
        
        # Visitar mais fatores
        self.visit_mais_fatores(mais_fatores)
    
    def visit_fator(self, node: ASTNode):
        """Visita FATOR"""
        if node.filhos:
            child = node.filhos[0]
            if child.tipo == "ID":
                var_name = child.valor
                address = self.get_var_address(var_name)
                self.emit('CRVL', str(address))
            elif child.tipo == "NUMERO_REAL":
                value = child.valor
                self.emit('CRCT', value)
            elif child.tipo == "EXPRESSAO":
                self.visit_expressao(child)
    
    def visit_outros_termos(self, node: ASTNode):
        """Visita OUTROS_TERMOS"""
        if node.filhos:  # Se não for λ
            op_ad = node.filhos[0]
            termo = node.filhos[1]
            outros = node.filhos[2]
            
            self.visit_termo(termo)
            
            # Aplicar operador
            if op_ad.valor == '+':
                self.emit('SOMA')
            elif op_ad.valor == '-':
                self.emit('SUBT')
            
            self.visit_outros_termos(outros)
    
    def visit_mais_fatores(self, node: ASTNode):
        """Visita MAIS_FATORES"""
        if node.filhos:  # Se não for λ
            op_mul = node.filhos[0]
            fator = node.filhos[1]
            mais_fatores = node.filhos[2]
            
            self.visit_fator(fator)
            
            # Aplicar operador
            if op_mul.valor == '*':
                self.emit('MULT')
            elif op_mul.valor == '/':
                self.emit('DIVI')
            
            self.visit_mais_fatores(mais_fatores)
    
    def visit_pfalsa(self, node: ASTNode):
        """Visita PFALSA (else)"""
        if node.filhos:  # Se não for λ
            cmds_node = node.filhos[0]
            self.visit_cmds(cmds_node)
    
    def emit_label(self, label: int):
        """Emite um label (comentário no código)"""
        self.code.append(f"L{label}:")
