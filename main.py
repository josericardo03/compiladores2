#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Mini-Java
Implementa analisador léxico, sintático, semântico e gerador de código objeto
"""

import sys
import os
from lexer import Lexer
from syntax_parser import Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from virtual_machine import VirtualMachine

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_entrada> [opções]")
        print("Opções:")
        print("  --compile: Apenas compilar (gerar código objeto)")
        print("  --execute: Apenas executar código objeto existente")
        print("  --full: Compilar e executar (padrão)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    mode = 'full'
    
    if len(sys.argv) > 2:
        mode = sys.argv[2].replace('--', '')
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        sys.exit(1)
    
    try:
        if mode in ['compile', 'full']:
            print("=== COMPILAÇÃO ===")
            compile_file(input_file)
        
        if mode in ['execute', 'full']:
            print("\n=== EXECUÇÃO ===")
            execute_object_code(input_file)
            
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

def compile_file(input_file):
    """Compila um arquivo Mini-Java para código objeto"""
    # Ler arquivo de entrada
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    print(f"Compilando: {input_file}")
    
    # Análise Léxica
    print("1. Análise Léxica...")
    lexer = Lexer()
    tokens = lexer.tokenize(source_code)
    print(f"   {len(tokens)} tokens encontrados")
    
    # Análise Sintática
    print("2. Análise Sintática...")
    parser = Parser(tokens)
    ast = parser.parse()
    print("   Análise sintática concluída")
    
    # Análise Semântica
    print("3. Análise Semântica...")
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.analyze(ast)
    print("   Análise semântica concluída")
    
    # Geração de Código
    print("4. Geração de Código Objeto...")
    code_generator = CodeGenerator()
    object_code = code_generator.generate(ast)
    
    # Salvar código objeto
    output_file = input_file.replace('.java', '.obj') if input_file.endswith('.java') else input_file + '.obj'
    with open(output_file, 'w', encoding='utf-8') as f:
        for instruction in object_code:
            f.write(instruction + '\n')
    
    print(f"   Código objeto salvo em: {output_file}")
    return output_file

def execute_object_code(input_file):
    """Executa código objeto"""
    # Determinar arquivo de código objeto
    if input_file.endswith('.obj'):
        obj_file = input_file
    else:
        obj_file = input_file.replace('.java', '.obj') if input_file.endswith('.java') else input_file + '.obj'
    
    if not os.path.exists(obj_file):
        print(f"Erro: Arquivo de código objeto '{obj_file}' não encontrado.")
        print("Execute primeiro com --compile para gerar o código objeto.")
        return
    
    # Ler código objeto
    with open(obj_file, 'r', encoding='utf-8') as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"Executando: {obj_file}")
    print(f"{len(instructions)} instruções carregadas")
    
    # Executar na máquina virtual
    vm = VirtualMachine()
    vm.load_program(instructions)
    vm.execute()
    print("Execução concluída")

if __name__ == "__main__":
    main()
