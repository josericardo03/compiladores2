#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Máquina Virtual para executar código objeto Mini-Java
Implementa as instruções da linguagem de máquina hipotética
"""

from typing import List, Dict, Any

class VirtualMachine:
    def __init__(self):
        self.memory = []  # Memória da máquina virtual
        self.stack = []   # Pilha de execução
        self.program = [] # Programa carregado
        self.pc = 0       # Contador de programa
        self.labels = {}  # Mapeamento de labels para endereços
        
        # Tamanhos padrão
        self.memory_size = 1000
        self.stack_size = 1000
        
        # Inicializar memória
        self.memory = [0.0] * self.memory_size
    
    def load_program(self, instructions: List[str]):
        """Carrega programa na máquina virtual"""
        self.program = []
        self.labels = {}
        
        # Primeiro passagem: identificar labels
        for i, instruction in enumerate(instructions):
            if instruction.endswith(':'):
                # É um label
                label_name = instruction[:-1]
                self.labels[label_name] = i
            else:
                self.program.append(instruction)
        
        # Segunda passagem: substituir referências de labels
        processed_program = []
        for instruction in self.program:
            parts = instruction.split()
            if len(parts) > 1 and parts[1].isdigit() == False:
                # Pode ser um label
                label_ref = parts[1]
                if label_ref in self.labels:
                    # Substituir por endereço
                    address = self.labels[label_ref]
                    processed_program.append(f"{parts[0]} {address}")
                else:
                    processed_program.append(instruction)
            else:
                processed_program.append(instruction)
        
        self.program = processed_program
        self.pc = 0
    
    def execute(self):
        """Executa o programa carregado"""
        print("Iniciando execução da máquina virtual...")
        print("=" * 50)
        
        while self.pc < len(self.program):
            instruction = self.program[self.pc]
            self.execute_instruction(instruction)
            self.pc += 1
        
        print("=" * 50)
        print("Execução concluída.")
    
    def execute_instruction(self, instruction: str):
        """Executa uma instrução individual"""
        parts = instruction.split()
        opcode = parts[0]
        operand = int(parts[1]) if len(parts) > 1 else None
        
        if opcode == 'INPP':
            self.inpp()
        elif opcode == 'ALME':
            self.alme(operand)
        elif opcode == 'CRCT':
            self.crct(operand)
        elif opcode == 'CRVL':
            self.crvl(operand)
        elif opcode == 'ARMZ':
            self.armz(operand)
        elif opcode == 'LEIT':
            self.leit()
        elif opcode == 'IMPR':
            self.impr()
        elif opcode == 'CPMA':
            self.cpma()
        elif opcode == 'CPME':
            self.cpme()
        elif opcode == 'CPIG':
            self.cpig()
        elif opcode == 'CDES':
            self.cdes()
        elif opcode == 'SOMA':
            self.soma()
        elif opcode == 'SUBT':
            self.subt()
        elif opcode == 'MULT':
            self.mult()
        elif opcode == 'DIVI':
            self.divi()
        elif opcode == 'INVE':
            self.inve()
        elif opcode == 'DSVF':
            self.dsvf(operand)
        elif opcode == 'DSVI':
            self.dsvi(operand)
        elif opcode == 'PARA':
            self.para()
        else:
            print(f"Instrução não reconhecida: {opcode}")
    
    def inpp(self):
        """Inicializar programa"""
        self.stack = []
        print("Programa inicializado")
    
    def alme(self, n: int):
        """Alocar memória"""
        for _ in range(n):
            self.memory.append(0.0)
        print(f"Alocada {n} posição(ões) de memória")
    
    def crct(self, value: float):
        """Carregar constante na pilha"""
        self.stack.append(value)
        print(f"Carregada constante: {value}")
    
    def crvl(self, address: int):
        """Carregar valor de variável na pilha"""
        if address < len(self.memory):
            value = self.memory[address]
            self.stack.append(value)
            print(f"Carregado valor da variável [{address}]: {value}")
        else:
            print(f"Erro: Endereço {address} fora dos limites da memória")
    
    def armz(self, address: int):
        """Armazenar valor da pilha na memória"""
        if self.stack:
            value = self.stack.pop()
            if address < len(self.memory):
                self.memory[address] = value
                print(f"Armazenado valor {value} na posição [{address}]")
            else:
                print(f"Erro: Endereço {address} fora dos limites da memória")
        else:
            print("Erro: Pilha vazia para armazenamento")
    
    def leit(self):
        """Ler valor do teclado e colocar na pilha"""
        try:
            value = float(input("Digite um número: "))
            self.stack.append(value)
            print(f"Valor lido: {value}")
        except ValueError:
            print("Erro: Valor inválido. Usando 0.0")
            self.stack.append(0.0)
    
    def impr(self):
        """Imprimir valor do topo da pilha"""
        if self.stack:
            value = self.stack.pop()
            print(f"Saída: {value}")
        else:
            print("Erro: Pilha vazia para impressão")
    
    def cpma(self):
        """Comparar maior (a > b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1.0 if a > b else 0.0
            self.stack.append(result)
            print(f"Comparação {a} > {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para comparação")
    
    def cpme(self):
        """Comparar menor (a < b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1.0 if a < b else 0.0
            self.stack.append(result)
            print(f"Comparação {a} < {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para comparação")
    
    def cpig(self):
        """Comparar igual (a == b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1.0 if a == b else 0.0
            self.stack.append(result)
            print(f"Comparação {a} == {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para comparação")
    
    def cdes(self):
        """Comparar diferente (a != b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1.0 if a != b else 0.0
            self.stack.append(result)
            print(f"Comparação {a} != {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para comparação")
    
    def soma(self):
        """Somar (a + b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = a + b
            self.stack.append(result)
            print(f"Soma: {a} + {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para soma")
    
    def subt(self):
        """Subtrair (a - b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = a - b
            self.stack.append(result)
            print(f"Subtração: {a} - {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para subtração")
    
    def mult(self):
        """Multiplicar (a * b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            result = a * b
            self.stack.append(result)
            print(f"Multiplicação: {a} * {b} = {result}")
        else:
            print("Erro: Pilha não tem elementos suficientes para multiplicação")
    
    def divi(self):
        """Dividir (a / b)"""
        if len(self.stack) >= 2:
            b = self.stack.pop()
            a = self.stack.pop()
            if b != 0:
                result = a / b
                self.stack.append(result)
                print(f"Divisão: {a} / {b} = {result}")
            else:
                print("Erro: Divisão por zero")
                self.stack.append(0.0)
        else:
            print("Erro: Pilha não tem elementos suficientes para divisão")
    
    def inve(self):
        """Inverter sinal"""
        if self.stack:
            value = self.stack.pop()
            result = -value
            self.stack.append(result)
            print(f"Inversão de sinal: {value} -> {result}")
        else:
            print("Erro: Pilha vazia para inversão de sinal")
    
    def dsvf(self, label: int):
        """Desvio se falso"""
        if self.stack:
            condition = self.stack.pop()
            if condition == 0.0:  # Falso
                self.pc = label - 1  # -1 porque o PC será incrementado
                print(f"Desvio para label {label} (condição falsa)")
            else:
                print(f"Não desviou para label {label} (condição verdadeira)")
        else:
            print("Erro: Pilha vazia para desvio condicional")
    
    def dsvi(self, label: int):
        """Desvio incondicional"""
        self.pc = label - 1  # -1 porque o PC será incrementado
        print(f"Desvio incondicional para label {label}")
    
    def para(self):
        """Parar execução"""
        print("Execução parada")
        self.pc = len(self.program)  # Força saída do loop
    
    def print_state(self):
        """Imprime estado atual da máquina"""
        print(f"PC: {self.pc}")
        print(f"Pilha: {self.stack}")
        print(f"Memória: {self.memory[:10]}...")  # Primeiros 10 elementos
