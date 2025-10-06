# Compilador Mini-Java

Este projeto implementa um compilador completo para a linguagem Mini-Java, incluindo análise léxica, sintática, semântica e geração de código objeto, além de uma máquina virtual para execução.

## Estrutura do Projeto

```
compiladores-2/
├── main.py                 # Arquivo principal do compilador
├── lexer.py               # Analisador léxico
├── parser.py              # Analisador sintático
├── semantic_analyzer.py   # Analisador semântico
├── code_generator.py      # Gerador de código objeto
├── virtual_machine.py     # Máquina virtual
├── README.md              # Este arquivo
└── exemplos/              # Arquivos de exemplo
    ├── exemplo.java       # Exemplo de código Mini-Java
    └── exemplo.obj        # Código objeto gerado
```

## Requisitos

- Python 3.6 ou superior
- Nenhuma dependência externa (apenas bibliotecas padrão do Python)

## Como Executar

### 1. Compilação Completa (Recomendado)

```bash
python main.py arquivo.java --full
```

Compila o arquivo Mini-Java e executa o código objeto gerado.

### 2. Apenas Compilar

```bash
python main.py arquivo.java --compile
```

Gera apenas o código objeto (.obj) sem executar.

### 3. Apenas Executar

```bash
python main.py arquivo.obj --execute
```

Executa um arquivo de código objeto existente.

## Gramática Mini-Java Suportada

A linguagem Mini-Java implementada segue a gramática fornecida:

```
PROG -> public class id { public static void main ( String [ ] id ) { <CMDS> } }
CMDS -> <CMD><MAIS_CMDS> | <CMD_COND><CMDS> | <DC> | λ
CMD -> System.out.println (<EXPRESSAO>) | id <RESTO_IDENT>
CMD_COND -> if ( <CONDICAO> ) {<CMDS>} <PFALSA> | while ( <CONDICAO> ) {<CMDS>}
```

### Características Suportadas:

- **Tipos**: Apenas `double`
- **Operadores**: `+`, `-`, `*`, `/`, `==`, `!=`, `>=`, `<=`, `>`, `<`
- **Comandos**: Atribuição, `if-else`, `while`, `System.out.println`
- **Entrada**: `lerDouble()` para leitura de números
- **Expressões**: Aritméticas e relacionais com precedência correta

## Exemplo de Uso

### Arquivo de Entrada (exemplo.java):

```java
public class Teste {
    public static void main(String[] args) {
        double cont;
        double a,b,c;
        cont = 10;
        while(cont > 0) {
            a = lerDouble();
            b = lerDouble();
            if (a > b) {
                c = a - b;
            } else {
                c = b - a;
            }
            System.out.println(c);
            cont = cont - 1;
        }
        System.out.println(c);
    }
}
```

### Execução:

```bash
python main.py exemplo.java --full
```

### Saída Esperada:

```
=== COMPILAÇÃO ===
Compilando: exemplo.java
1. Análise Léxica...
   45 tokens encontrados
2. Análise Sintática...
   Análise sintática concluída
3. Análise Semântica...
   Análise semântica concluída
4. Geração de Código Objeto...
   Código objeto salvo em: exemplo.obj

=== EXECUÇÃO ===
Executando: exemplo.obj
39 instruções carregadas
Iniciando execução da máquina virtual...
...
```

## Instruções da Máquina Virtual

O compilador gera código para uma máquina virtual hipotética com as seguintes instruções:

| Instrução       | Descrição                    |
| --------------- | ---------------------------- |
| `INPP`          | Inicializar programa         |
| `ALME n`        | Alocar n posições de memória |
| `CRCT valor`    | Carregar constante na pilha  |
| `CRVL endereço` | Carregar valor de variável   |
| `ARMZ endereço` | Armazenar valor na memória   |
| `LEIT`          | Ler valor do teclado         |
| `IMPR`          | Imprimir valor da pilha      |
| `CPMA`          | Comparar maior               |
| `CPME`          | Comparar menor               |
| `CPIG`          | Comparar igual               |
| `CDES`          | Comparar diferente           |
| `SOMA`          | Somar                        |
| `SUBT`          | Subtrair                     |
| `MULT`          | Multiplicar                  |
| `DIVI`          | Dividir                      |
| `INVE`          | Inverter sinal               |
| `DSVF label`    | Desvio se falso              |
| `DSVI label`    | Desvio incondicional         |
| `PARA`          | Parar execução               |

## Arquitetura do Compilador

### 1. Analisador Léxico (lexer.py)

- Reconhece tokens da linguagem Mini-Java
- Suporta palavras reservadas, operadores, identificadores e números reais
- Ignora comentários e espaços em branco

### 2. Analisador Sintático (parser.py)

- Implementa análise descendente recursiva
- Constrói Árvore Sintática Abstrata (AST)
- Segue exatamente a gramática fornecida

### 3. Analisador Semântico (semantic_analyzer.py)

- Verifica declaração de variáveis
- Mantém tabela de símbolos
- Valida uso correto de identificadores

### 4. Gerador de Código (code_generator.py)

- Gera código objeto para máquina virtual
- Aloca memória para variáveis
- Implementa controle de fluxo (if, while)
- Gera labels para desvios

### 5. Máquina Virtual (virtual_machine.py)

- Executa código objeto gerado
- Implementa pilha e memória
- Suporta todas as instruções definidas
- Fornece saída detalhada da execução

## Tratamento de Erros

O compilador detecta e reporta:

- **Erros Léxicos**: Caracteres não reconhecidos
- **Erros Sintáticos**: Construções inválidas
- **Erros Semânticos**: Variáveis não declaradas, uso incorreto

## Limitações

- Suporta apenas tipo `double`
- Não implementa arrays (apenas sintaxe básica)
- Não suporta funções/métodos além de `main`
- Máquina virtual tem tamanho limitado de memória

## Testes

Para testar o compilador, use o arquivo de exemplo fornecido:

```bash
python main.py "mini-java-examplo (1).java" --full
```

O resultado deve ser equivalente ao código objeto fornecido em `codigo-objeto-exemplo (1).txt`.

## Autor

Compilador Mini-Java implementado como projeto de Compiladores 2.

# Compilar e executar

py main.py "mini-java-examplo (1).java" --full

# Apenas compilar

py main.py "mini-java-examplo (1).java" --compile

# Apenas executar código objeto

py main.py "arquivo.obj" --execute
