"""Este script utiliza a API Google Generative AI para interagir com um modelo de linguagem grande e analisar o conteúdo de um arquivo PDF específico, permitindo que o usuário selecione o arquivo através de uma interface gráfica."""

# Importar bibliotecas necessárias
from pathlib import Path
import hashlib
import google.generativeai as genai
import textwrap
from IPython.display import display
from IPython.display import Markdown
import PyPDF2
import tkinter as tk
from tkinter import filedialog

# Função para solicitar o arquivo PDF com interface gráfica
def get_pdf_path():
    root = tk.Tk()
    root.withdraw()  # Ocultar a janela principal do Tkinter
    file_path = filedialog.askopenfilename(
        title="Selecione um arquivo PDF", filetypes=[("Arquivos PDF", "*.pdf")]
    )
    return file_path


def obter_chave_api():
  """Solicita ao usuário uma chave de API e a valida."""

  while True:
    chave_api = input("Por favor, digite sua chave de API do Google Generative AI: ")
    if len(chave_api) > 0:
      return chave_api
    else:
      print("A chave de API não pode estar vazia. Tente novamente.")

# Obter a chave de API do usuário
CHAVE_API = obter_chave_api() #insira sua api key aqui ou deixe assim para o usuário possa inserir a sua propiá 

# Configurar a API do Google Generative AI com a chave de API fornecida
genai.configure(api_key=CHAVE_API)


# Configurações para o modelo de linguagem
generation_config = {
    "temperature": 1,  # Controla a criatividade do modelo
    "top_p": 0.95,     # Controla a diversidade das respostas
    "top_k": 0,        # Não utilizado neste caso
    "max_output_tokens": 8192  # Número máximo de tokens na resposta
}

# Configurações de segurança para o modelo
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Instrução para o sistema
system_instruction = "Aja como um alguém que leu o arquivo e conhece com detalhes  o assunto mencione sempre a pagina e o paragrafo em que esta baseando suas respostas. Não responda nada que não esteja relacionado ao arquivo. De forma educada, diga que este assunto não esta relacionado ao livro. "

# Criar um modelo generativo com as configurações especificadas
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=system_instruction,
    safety_settings=safety_settings
)

# Função para extrair texto de um arquivo PDF
def extract_pdf_pages(pathname: str) -> list[str]:
    parts = [f"--- START OF PDF ${pathname} ---"]
    with open(pathname, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            parts.append(f"--- PAGE {page_num} ---")
            parts.append(text)
    return parts

# Solicitar ao usuário o caminho do arquivo PDF usando a GUI
print("Escolha um arquivo PDF do seu ficheiro:")  # Informar o usuário
pdf_path = get_pdf_path()

# Verificar se um arquivo foi selecionado
if not pdf_path:
    print("Nenhum arquivo selecionado.")
    exit()  # Encerrar o script se nenhum arquivo for escolhido

# Iniciar uma sessão de chat com o modelo
chat = model.start_chat(history=[])
print('Vamos conversar sobre esse livro?')

# Solicitar ao usuário o prompt (pergunta ou instrução)
prompt = input('Prompt Usuário:')


# Função para converter texto em Markdown
def to_markdown(text):
    text = text.replace('.', '\n')
    return Markdown(textwrap.indent(text, '>', predicate=lambda _: True))

# Loop para interagir com o modelo
while prompt != "fim":
    # Extrair o texto do PDF
    pdf_text = extract_pdf_pages(pdf_path)

    # Combinar o texto do PDF com o prompt
    full_prompt = "\n".join(pdf_text) + "\n" + prompt

    # Enviar o prompt completo para o modelo e obter a resposta
    response = chat.send_message(full_prompt)

    # # Imprimir a resposta do modelo formatada com Markdown
    # print(to_markdown(f"**Resposta assistente**: {response.text}")) 
    # print('--------------------------')

      # Imprimir a resposta do modelo
    print('Resposta: ', response.text, '\n')


    # Solicitar o próximo prompt ou encerrar a sessão
    prompt = input('Prompt Usuário (Digite "fim" para encerrar): ')