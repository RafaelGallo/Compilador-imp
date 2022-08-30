'''
Grupo:

- Clarice Dantas    RA 1902815
- Leandro Soares    RA 1901845
- Rafael Gallo      RA 1901885
- Rodrigo Santiago  RA 1902375
- Yago Rodrigues    RA 1902362
'''

from ast import Lt
#from ctypes.wintypes import INT
from tokenize import String
from typing import NamedTuple, Union
from sys import argv
from numpy import lookfor

from zmq import SUB

class ErroLexicoRxception(Exception):
    pass


#tolkens da linguagem (tipo do tolken)
ERRO = 0
IDENTIFICADOR = 1
NUM_INT = 2
NUM_REAL = 3
EOS = 4 #fim da cadeia
RELOP = 5 # OPERADORES RELACIONAIS
ADDOP = 6 # OPERADORES DE SOMA E SIBTRAÇÃO
MULOP = 7 #OPERADORES DE MULTIPLICAÇÃO E DIVISÃO
ALGORITMO = 8
ATE = 9
CADEIA = 10
CARACTER = 11
ENQUANTO = 12
ENTAO = 13 
FACA = 14
FIM = 15
FUNCAO = 16
INICIO = 17
INTEIRO = 18
PARA = 19 
PASSO = 20
PROCEDIMENTO = 21
REAL = 22
REF = 23
RETORNE = 24
SE = 25 
SENAO = 26
VARIAVEIS = 27
COMENTARIO = 28
STRING = 29
ATRIBU=30
PONTO = 31 # .
ABRE_PAR = 32 # (
FECHA_PAR = 33 # )
VIRGULA = 34 # ,
PONTO_VIRGULA = 35 # ;

# OPERADOR RELACIONAL
MEI = 1000 # MENOR IGUAL (<=)
DI = 1001 # DIFERENTE (<>)
ME = 1002 # MENOR QUE (<)
MAI = 1003 # MAIOR IGUAL (>=)
MA = 1004 # MAIOR QUE  (>)
IG = 1005 # IGUAL (=)
ADICAO = 1006 # MAIS (+)
SUBTRACAO = 1007 # MENOS (-)
DIVISAO = 1008 # dividir (/)
COMENT = 1009  #  /* COMENTARIOS */
MULTIPLICACAO = 1010 # (*)
ATRIBUICAO = 1011 # ATRIBUIR (<-)
RESTO = 1012 # RESTO DA DIVISAO (%)



E = 1018 # (&)
OU = 1019 # ($)
NEG = 1020 # (!)

tolken_msg = ['ERRO', 'IDENTIF', 'NUM_INT', 'NUM_REAL', 'EOS', 'RELOP', 'ADDOP', 'MULOP',
                'ALGORITMO', 'ATE', 'CADEIA', 'CARACTER','ENQUANTO','ENTAO','FACA','FIM',
                'FUNCAO','INICIO','INTEIRO','PARA','PASSO','PROCEDIMENTO','REAL','REF',
                'RETORNE','SE','SENAO','VARIAVEIS', 'COMENTARIO', 'STRING','ATRIBUIÇÃO','PONTO','ABRE_PAR','FECHA_PAR',
                'VIRGULA','PONTO_VIRGULA']

operador_msg ={
    DI:'DI',
    MEI:'MEI',
    ME:'LT',
    MAI:'MAI',
    MA:'MA',
    IG:'IG',
    ADICAO:'ADICAO',
    SUBTRACAO:'SUBTRACAO',
    DIVISAO:'DIVISAO',
    MULTIPLICACAO:'MULTIPLICACAO',
    ATRIBUICAO: 'ATRIBUICAO',
    RESTO:'RESTO',
    VIRGULA:'VIRGULA',
    PONTO_VIRGULA:'PONTO_VIRGULA',
    ABRE_PAR:'ABRE_PAR',
    FECHA_PAR:'FECHA_PAR',
    PONTO:'PONTO',
    E:'E',
    OU:'OU',
    NEG:'NEG',
    0:'--'
}

palavras_reservadas = {
    'ALGORITMO':ALGORITMO,
    'ATE':ATE,
    'CADEIA':CADEIA,
    'CARACTER':CARACTER,
    'ENQUANTO':ENQUANTO,
    'ENTAO':ENTAO,
    'FACA':FACA,
    'FIM':FIM,
    'FUNCAO':FUNCAO,
    'INICIO':INICIO,
    'INTEIRO':INTEIRO,
    'PARA':PARA,
    'PASSO':PASSO,
    'PROCEDIMENTO':PROCEDIMENTO,
    'REAL':REAL,
    'REF':REF,
    'RETORNE':RETORNE,
    'SE':SE,
    'SENAO':SENAO,
    'VARIAVEIS':VARIAVEIS
}

class Tolken(NamedTuple):
    tipo: int                #[ 0 - erro, 1 - indentificador, 2 - num_int, 3 - num_real, 4 - eos]     
    lexema: str
    valor: Union[int, float] # pode guardar um valor inteiro ou flutuante
    operador: int            # LE, NE, LT, GE, GT, EQ, adição e multiplicação
    linha: int


class Analisador_Lexico:
    def __init__(self, buffer):
        self.nlinha = 1
        self.buffer = buffer + '\0' #indica o fim da string
        self.i = 0
        
    def proximo_char(self):
        c = self.buffer[self.i]
        self.i += 1
        return c
    
    def retrac_char(self):
        self.i -= 1
        
    def tratar_numero(self, c):
        lexema = c
        estado = 1

        c = self.proximo_char()
        while True:
            # estado 1
            if estado == 1:
                if  c.isdigit():
                    lexema = lexema + c
                    estado =1
                    c = self.proximo_char()
                elif c == '.':
                    lexema = lexema + c
                    estado = 3
                    c = self.proximo_char()
                else:
                    estado = 2
            
            # estado 2
            elif estado ==2:
                self.retrac_char()
                return Tolken(NUM_INT, lexema,int(lexema), 0, self.nlinha)
            
            # estado 3
            elif estado ==3:
                if c.isdigit():
                    estado= 4
                else:
                    return Tolken(ERRO, '', 0, 0, self.nlinha)
            
            # estado 4
            elif estado == 4:
                if c.isdigit():
                    lexema = lexema + c
                    estado = 4
                    c = self.proximo_char()
                else:
                    estado = 5
                
            # estado 5
            elif estado == 5:
                self.retrac_char()
                return Tolken(NUM_REAL, lexema, float(lexema), 0, self.nlinha)

        return Tolken(NUM_INT, '', 0, self.nlinha)
    
    def tratar_identificador(self, c):
        lexema = c
        c = self.proximo_char()
        estado = 1

        while True:
            if estado ==1:
                if c.isdigit() or c.isalpha() or c =='_' or c =='-':
                    lexema = lexema + c
                    estado = 1
                    c = self.proximo_char()
                else:
                    estado = 2
            elif estado ==2:
                self.retrac_char()
                if lexema.upper() in palavras_reservadas:
                    codigo = palavras_reservadas[lexema.upper()]
                    return Tolken(codigo, lexema.upper(), 0, 0, self.nlinha)
                else:
                    return Tolken(IDENTIFICADOR, lexema, 0, 0, self.nlinha)

    def tratar_divcomentario(self, c):
        lexema = c
        c = self.proximo_char()
        estado = 1

        while True:
            if estado == 1:
                if c == '*':
                    estado = 3
                    lexema = lexema + c
                    c = self.proximo_char()
                else:
                    estado =2

            elif estado == 2:
                self.retrac_char()
                return Tolken(MULOP,lexema, 0,DIVISAO, self.nlinha)
            
            elif estado ==3:
                if c == '*':
                    estado = 4
                    lexema = lexema + c
                    c = self.proximo_char()
                else:
                    lexema = lexema + c
                    estado = 3
                    c = self. proximo_char()
            
            elif estado ==4:
                if c =='/':
                    lexema = lexema + c
                    estado = 5
                    #c = self.proximo_char()
                else:
                    lexema = lexema + c
                    estado = 3
                    c = self.proximo_char()

            elif estado ==5:
                return Tolken(COMENTARIO,lexema,0, 0, self.nlinha)
              
    def tratar_operador_menor(self, c):
        lexema = c
        estado = 1
        c = self.proximo_char()
        while True:
            # estado 1
            if estado ==1:
                if c == '=':
                    lexema = lexema + c
                    estado = 2
                elif c =='>':
                    lexema = lexema + c
                    estado = 3
                
                elif c =='-':
                    lexema = lexema + c
                    estado = 9
                else:
                    estado = 4
            
            # estado 2
            elif estado ==2:
                return Tolken(RELOP, lexema, 0, MEI, self.nlinha)
                

            # estado 3
            elif estado ==3:
                return Tolken(RELOP, lexema, 0, DI, self.nlinha)
                

            # estado 4
            elif estado ==4:
                return Tolken(RELOP, lexema, 0, MA, self.nlinha)

            # estado 9
            elif estado ==9:
                return Tolken(ATRIBU, lexema, 0, 0, self.nlinha)

    def tratar_operador_maior(self, c):
        lexema = c
        estado = 6
        c = self.proximo_char()
        while True:
            if estado ==6:
                if c == '=':
                    lexema = lexema +c
                    estado = 7
                else:
                    self.retrac_char()
                    estado = 8

            elif estado == 7:
                return Tolken(RELOP,lexema, 0, MAI, self.nlinha) 
            
            elif estado == 8:
                return Tolken(RELOP, lexema, 0, ME, self.nlinha)

    def tratar_string(self, c):
        lexema = c
        estado = 0
        c = self.proximo_char()

        while True:
            if estado == 0:
                if lexema == '"':
                    estado = 1
                else:
                    estado = 3

            elif estado == 1:
                if c == '"':
                    lexema = lexema + c
                    estado = 2
                else:
                    lexema = lexema + c
                    estado = 1
                    c = self.proximo_char()

            elif estado ==2:
                return Tolken(STRING,lexema, 0, 0, self.nlinha)

            elif estado == 3:
                if c == "'":
                    lexema = lexema + c
                    estado = 2
                else:
                    lexema = lexema + c
                    estado = 3
                    c = self.proximo_char()                

    def gerar_erro(self, erro):
        raise ErroLexicoRxception(f'Erro léxico: {erro}')
    
    def proximo_tolken(self):
        tolken = Tolken(ERRO, '', 0, 0, self.nlinha)
        c = self.proximo_char()
        
        # Trata os delimitadores
        while c in [' ', '\n','\0']:
            
            if c == '\n':
                self.nlinha +=1
            
            if c =='\x00':
                return Tolken(EOS, '', 0, 0, self.nlinha)
            
            c = self.proximo_char()
        #Tratar os outros Tolkens aqui
        if c.isdigit():
            return self.tratar_numero(c)
            
        elif c.isalpha():
            return self.tratar_identificador(c)
        
        elif c =='+':
            return Tolken(ADDOP, '+', 0, ADICAO, self.nlinha)

        elif c == '/':
            return self.tratar_divcomentario(c)

        elif c =='*':
            return Tolken(MULOP, '*', 0, MULTIPLICACAO, self.nlinha)

        elif c =='-':
            return Tolken(ADDOP, '-', 0, SUBTRACAO, self.nlinha)

        elif c == '<':
            return self.tratar_operador_menor(c)

        elif c == '>':
            return self.tratar_operador_maior(c)

        elif c == '%':
            return Tolken(MULOP, c, 0, RESTO, self.nlinha)
        
        elif c == ',':
            return Tolken(VIRGULA, c, 0, 0, self.nlinha)

        elif c == ';':
            return Tolken(PONTO_VIRGULA, c, 0, 0, self.nlinha)

        elif c == '(':
            return Tolken(ABRE_PAR, c, 0, 0, self.nlinha)

        elif c == ')':
            return Tolken(FECHA_PAR, c, 0, 0, self.nlinha)

        elif c == '.':
            return Tolken(PONTO, c, 0, 0, self.nlinha)

        elif c == '=':
            return Tolken(RELOP, c, 0, IG, self.nlinha)

        elif c == "'" or c == '"':
            return self.tratar_string(c)

        elif c == '!':
            return Tolken(RELOP, c, 0, NEG, self.nlinha)

        elif c == '&':
            return Tolken(RELOP, c, 0, E, self.nlinha)

        elif c == '$':
            return Tolken(RELOP, c, 0, OU, self.nlinha)

        return tolken

################################################################################################################### Fim do analisador lexico

#variaveis globais
i = 0
lookahead = 0
atributos_tolken = {}
lexico = {}
atributos_atomo = None

def erro(atomo):
    global atributos_tolken
    global tolken_msg
    print(f'erro de sintaxe linha: {atributos_tolken.linha}, era esperado tolken do tipo:{tolken_msg[atomo]}, foi recebido o tipo {tolken_msg[lookahead]}')
    quit()
    


def consome(atomo):
    global lookahead
    global lexico
    global atributos_tolken
    if (atomo == lookahead):
        if atomo != EOS:
            atributos_tolken = lexico.proximo_tolken()
            lookahead = atributos_tolken.tipo
    else:
        try:
            raise
        except Exception as e:
            erro(atomo)
            

def TIPO_SIMPLES():
    if lookahead == INTEIRO:
        consome(INTEIRO)
    elif lookahead == REAL:
        consome(REAL)
    elif lookahead == CARACTER:
        consome(CARACTER)
    elif lookahead == STRING:
        consome(STRING)

def SECAO_PARAMETROS():
    if lookahead == INTEIRO:
        TIPO_SIMPLES()
        if lookahead == REF:
            consome(REF)
        LISTA_DE_INDENTIFICADORES()
    elif lookahead == EOS:
        consome(EOS)

def PARAMETROS_FORMAIS():
    consome(ABRE_PAR)
    SECAO_PARAMETROS()
    while lookahead == PONTO_VIRGULA or lookahead == INTEIRO or lookahead == EOS:
        consome(PONTO_VIRGULA)
        SECAO_PARAMETROS()
    consome(FECHA_PAR)

def DECLARA_FUNCAO():
    consome(FUNCAO)
    TIPO_SIMPLES()
    consome(IDENTIFICADOR)
    PARAMETROS_FORMAIS()
    if lookahead ==VARIAVEIS:
        DECLARA_VAR()
    consome(INICIO)
    COMANDO_COMPOSTO()
    consome(FIM)
    if lookahead == FUNCAO or lookahead == PROCEDIMENTO:
        DECLARA_MOD()

def DECLARA_PROCEDIMENTO():
    consome(PROCEDIMENTO)
    consome(IDENTIFICADOR)
    PARAMETROS_FORMAIS()
    if lookahead == VARIAVEIS:
        DECLARA_VAR()
    consome(INICIO)
    COMANDO_COMPOSTO()
    consome(FIM)
    if lookahead == FUNCAO or lookahead == PROCEDIMENTO:
        DECLARA_MOD()

def DECLARA_MOD():
    if lookahead == FUNCAO:
        DECLARA_FUNCAO()
    elif lookahead == PROCEDIMENTO:
        DECLARA_PROCEDIMENTO()

def TERMO_RELACIONAL():
    TERMO()
    while lookahead in [ADICAO, SUBTRACAO, IDENTIFICADOR]:
        OPERADOR_ADICAO()
        TERMO()

def OPERADOR_RELACIONAL():
    if lookahead == RELOP:
        consome(RELOP)

def FATOR():
    if lookahead == IDENTIFICADOR:
        consome(IDENTIFICADOR)
        if lookahead == ABRE_PAR:
            consome(ABRE_PAR)
            LISTA_EXPRESSAO()
            consome(FECHA_PAR)
    elif lookahead == NUM_INT:
        consome(NUM_INT)
    elif lookahead == NUM_REAL:
        consome(NUM_REAL)
    elif lookahead == STRING:
        consome(STRING)
    elif lookahead == NEG:
        consome(NEG)
        FATOR()
    elif lookahead == SUBTRACAO:
        consome(SUBTRACAO)
    elif lookahead == ABRE_PAR:
        consome(ABRE_PAR)
        EXPRESSAO()
        consome(FECHA_PAR)

def OPERADOR_MULTIPLICACAO():
    if lookahead == MULOP:
        consome(MULOP)

def TERMO():
    FATOR()
    while lookahead == MULOP or lookahead == IDENTIFICADOR:
        OPERADOR_MULTIPLICACAO()
        FATOR()

def OPERADOR_ADICAO():
    if lookahead == ADDOP:
        consome(ADDOP)

def TERMO_RELACIONAL():
    TERMO()
    if lookahead == ADDOP or lookahead == IDENTIFICADOR:
        OPERADOR_ADICAO()
        TERMO()

def EXPRESSAO_SIMPLES():
    TERMO_RELACIONAL()
    while lookahead == RELOP:
        OPERADOR_RELACIONAL()
        TERMO_RELACIONAL()

def OPERADOR_LOGICO():
    if lookahead == E:
        consome(E)
    elif lookahead == OU:
        consome(OU)

def EXPRESSAO():
    EXPRESSAO_SIMPLES()
    while lookahead == E:
        OPERADOR_LOGICO()
        EXPRESSAO_SIMPLES()

def COMANDO_ATRIBUICAO():
    consome(IDENTIFICADOR)
    consome(ATRIBU)
    EXPRESSAO()

def LISTA_EXPRESSAO():
    EXPRESSAO()
    while lookahead == PONTO_VIRGULA:
        consome(PONTO_VIRGULA)
        EXPRESSAO()

def CHAMADA_MODULO():
    consome(IDENTIFICADOR)
    if lookahead == ABRE_PAR:
        consome(ABRE_PAR)
        LISTA_EXPRESSAO()
        consome(FECHA_PAR)

def COMANDO_SE():
    consome(SE)
    EXPRESSAO()
    consome(ENTAO)
    COMANDO_COMPOSTO()
    if lookahead == SENAO:
        consome(SENAO)
        COMANDO_COMPOSTO()
    consome(FIM)
    consome(SUBTRACAO)
    consome(SE)
    

def COMANDO_ENQUANTO():
    consome(ENQUANTO)
    EXPRESSAO()
    consome(FACA)
    COMANDO_COMPOSTO()
    consome(FIM)
    consome(SUBTRACAO)
    consome(ENQUANTO)

def COMANDO_RETORNE():
    consome(RETORNE)
    EXPRESSAO()

def COMANDO():
    if lookahead == IDENTIFICADOR:
        COMANDO_ATRIBUICAO()
    elif lookahead == IDENTIFICADOR:
        CHAMADA_MODULO()
    elif lookahead == SE:
        COMANDO_SE()
    elif lookahead == ENQUANTO:
        COMANDO_ENQUANTO()
    elif lookahead == RETORNE:
        COMANDO_RETORNE()

def COMANDO_COMPOSTO():
    COMANDO()
    while lookahead == PONTO_VIRGULA:
        consome(PONTO_VIRGULA)
        COMANDO()

def LISTA_DE_INDENTIFICADORES():
    consome(IDENTIFICADOR)
    while lookahead == VIRGULA:
        consome(VIRGULA)
        consome(IDENTIFICADOR)

def DECLARA_VAR():
    consome(VARIAVEIS)
    TIPO_SIMPLES()
    LISTA_DE_INDENTIFICADORES()
    while lookahead == INTEIRO or lookahead == REAL or lookahead == CARACTER or lookahead == CADEIA:
        TIPO_SIMPLES()
        LISTA_DE_INDENTIFICADORES()

def BLOCO():
    global lookahead
    if lookahead == VARIAVEIS:
        DECLARA_VAR()
    if lookahead == FUNCAO or lookahead ==PROCEDIMENTO:
        DECLARA_MOD()
    consome(INICIO)
    COMANDO_COMPOSTO()
    consome(FIM)
    consome(PONTO)
    
def PROGRAMA():
    global lookahead
    consome(ALGORITMO)
    consome(IDENTIFICADOR)
    BLOCO()

def sintatico():
    global lookahead
    global lexico
    global atributos_tolken

    atributos_tolken = lexico.proximo_tolken()
    lookahead = atributos_tolken.tipo
    PROGRAMA()
    consome(EOS)
    print('fim da analise sintatica')

def ler_arquivo():
    '''Ler o arquivo passado no argumento'''
    #arquivo = 'ex01.ptl'
    arquivo = argv[1]
    with open(arquivo, 'r') as f:
        cadeia = f.read()
    return cadeia

def main():
    global lexico
    buffer = ler_arquivo()     # ler de um arquivo de entrada
    lexico = Analisador_Lexico(buffer)
    sintatico()

main()