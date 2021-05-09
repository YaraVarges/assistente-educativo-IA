import speech_recognition as sr
from nltk import word_tokenize, corpus
import json

IDIOMA_CORPUS = "portuguese"
IDIOMA_FALADO = "pt-BR"
CAMINHO_CONFIG = "C:/Users/Yara/Desktop/Assistente_Educativo/config.json"


def iniciar():
    global reconhecedor
    global palavras_paradas
    
    global nome_da_assistente
    global perguntas
    global solucao

    
    reconhecedor = sr.Recognizer()
    palavras_paradas = set(corpus.stopwords.words(IDIOMA_CORPUS))
    

    with open(CAMINHO_CONFIG, "r") as arq_config:
        config = json.load(arq_config)
        
        nome_da_assistente = config["nome"]
        perguntas = config["perguntas"]
        solucao = config["solucao"]
        arq_config.close()
       
        
def ouvir_pergunta():
    global reconhecedor
    global palavras_paradas
    
    pergunta = None
    
    with sr.Microphone() as audio:
        reconhecedor.adjust_for_ambient_noise(audio)
        
        print("PERGUNTE ALGO PARA A ANA...")
        fala = reconhecedor.listen(audio)
        
        try:
            pergunta = reconhecedor.recognize_google(fala, language=IDIOMA_FALADO)
            pergunta = pergunta.lower()
            
            print("A PERGUNTA INFORMADA FOI: ", pergunta)
        except sr.UnknownValueError:
            pass
      
    return pergunta  
  
def retirar_palavras_de_paradas(tokens):
    global palavras_paradas
    
    tokens_filtrados = []
    for token in tokens:
        if token not in palavras_paradas:
            tokens_filtrados.append(token)

    return tokens_filtrados

def tokenizar_pergunta(pergunta):
    global nome_da_assistente
    
    partes_da_pergunta = None
    
    tokens = word_tokenize(pergunta, IDIOMA_CORPUS)
    if tokens: 
        tokens = retirar_palavras_de_paradas(tokens)
        
        total_tokens = len(tokens)
        if total_tokens >= 3:
            if nome_da_assistente == tokens[0]:
                partes_da_pergunta = []
                for i in range(1, total_tokens):
                    partes_da_pergunta.append(tokens[i])

    return partes_da_pergunta

def reconhecer_pergunta(partes_da_pergunta):
    global perguntas
    
    valida = False
    total_partes_pergunta = len(partes_da_pergunta)
    total_partes_validas = 0
    
    for pergunta_prevista in perguntas:
        partes_previstas = word_tokenize(pergunta_prevista, IDIOMA_CORPUS)
        total_partes_previstas = len(partes_previstas)

        if total_partes_previstas <= total_partes_pergunta:
           total_partes_validas = 0
        for i in range(0, total_partes_previstas):
            if partes_previstas[i] == partes_da_pergunta[i]:
                total_partes_validas = total_partes_validas + 1
        if total_partes_pergunta == total_partes_previstas:
            valida = True
            break
           
    return valida, total_partes_validas
 
    
def reconhecer_solucao(partes_pergunta):
    global solucao

    valida = False
    resposta = None
    total_partes_solucao = len(partes_pergunta)

    for constante_prevista in solucao:
        partes_previstas = word_tokenize(constante_prevista["nomes"], IDIOMA_CORPUS)
        total_partes_prevista = len(partes_previstas)
        
        if total_partes_prevista <= total_partes_solucao:
            total_partes_validas = 0

            for i in range(0, total_partes_prevista):
                if partes_previstas[i] == partes_pergunta[i]:
                    total_partes_validas = total_partes_validas + 1
        
                if total_partes_validas == total_partes_prevista:
                    resposta = constante_prevista["resposta"]
                    valida = True
                    break
                
    return valida, resposta           
          

if __name__ == "__main__":
    iniciar()

    continuar = True
    while continuar:
        pergunta = ouvir_pergunta()
        pergunta_valida, solucao_valida = False, False
       
        if pergunta:
            partes_pergunta = tokenizar_pergunta(pergunta)
            
            if partes_pergunta:
                pergunta_valida, total_partes_validas = reconhecer_pergunta(partes_pergunta)  

                if pergunta_valida:
                    partes_pergunta = partes_pergunta[total_partes_validas:]
                    solucao_valida, resposta = reconhecer_solucao(partes_pergunta)

                    if solucao_valida:
                        print("A RESPOSTA É: ", resposta)

        if not (pergunta_valida and solucao_valida):
            print("NÃO ENTENDI A SUA PERGUNTA. DIGA NOVAMENTE POR FAVOR!")