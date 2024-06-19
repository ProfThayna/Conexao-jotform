import requests
import pandas as pd
from bs4 import BeautifulSoup

# Defina sua chave de API e o código do formulário
api_key = ''
form_id = ''

# Endpoint para obter os envios do formulário
url = f'https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}&limit=1000'

# Faça a requisição
response = requests.get(url)
data = response.json()

# Verifique se a chave 'content' está presente nos dados retornados
if 'content' not in data:
    raise ValueError("A resposta da API não contém a chave 'content'.")

# Supondo que 'data' contém os envios dentro da chave 'content'
submissions = data['content']

def clean_html(raw_html):
    if isinstance(raw_html, list):
        raw_html = ' '.join(raw_html)
    if isinstance(raw_html, str) and raw_html.strip():
        clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
        return clean_text.strip()
    return ""

# Extraindo os campos desejados
rows = []
for submission in submissions:
    answers = submission.get('answers', {})
    row = {
        'Submission Date': submission.get('created_at', ''),
        'Professor': clean_html(answers.get('446', {}).get('answer', '')),
        'Patrocinador': clean_html(answers.get('439', {}).get('answer', '')),
        'Cidade': clean_html(answers.get('440', {}).get('answer', '')),
        'NOME COMPLETO DO ALUNO': clean_html(answers.get('403', {}).get('answer', '')),
        'ESCOLA/NÚCLEO:': clean_html(answers.get('455', {}).get('answer', '')),
        'TURNO:': clean_html(answers.get('402', {}).get('answer', '')),
        'SÉRIE/ANO:': clean_html(answers.get('456', {}).get('answer', '')),
        'IDADE:': clean_html(answers.get('453', {}).get('answer', '')),
        'Local de execução': clean_html(answers.get('441', {}).get('answer', '')),
        '03 - Você gosta de praticar esportes?': clean_html(answers.get('458', {}).get('answer', '')),
        '03.1 Quais esportes você mais gosta?': clean_html(answers.get('452', {}).get('answer', '')),
        '04. Você considera que tem alguma dificuldade para praticar esportes?': clean_html(answers.get('428', {}).get('answer', '')),
        '05 - Você sabe o que é Fair Play?': clean_html(answers.get('459', {}).get('answer', '')),
        '06 - Marque as opções de Fair Play que você já pratica:': clean_html(answers.get('451', {}).get('answer', '')),
        '07 - Você sabe o que é protagonismo?': clean_html(answers.get('460', {}).get('answer', '')),
        '08 - O que você considera ser protagonismo?': clean_html(answers.get('461', {}).get('answer', '')),
        '10 - Quais valores você tem praticado até o momento?': clean_html(answers.get('463', {}).get('answer', '')),
        '11 - Você gosta de futebol?': clean_html(answers.get('514', {}).get('answer', '')),
        '14 - Você conhece os dribles do futebol?': clean_html(answers.get('517', {}).get('answer', '')),
        '15 - Quando você enfrenta dificuldades no dia a dia, como acha que pode superá-las? Marque as opções que você consegue fazer:': clean_html(answers.get('518', {}).get('answer', '')),
        '16 - Como o Projeto Futebol de Rua Pela Educação pode ajudar no seu desenvolvimento? Marque as opções mais importantes para você:': clean_html(answers.get('519', {}).get('answer', '')),
        '17 - Quais dos temas a seguir você já sabe ou já estudou antes de participar do projeto?': clean_html(answers.get('501', {}).get('answer', ''))
    }
    rows.append(row)


# Crie um DataFrame do pandas
df = pd.DataFrame(rows)

# Colunas relevantes para a nova tabela
colunas_relevantes = ['Submission Date',
                      'Professor',
                      'Patrocinador',
                      'Cidade',
                      'NOME COMPLETO DO ALUNO',
                      'ESCOLA/NÚCLEO:',
                      'TURNO:',
                      'SÉRIE/ANO:',
                      'IDADE:',
                      'Local de execução',
                      '03 - Você gosta de praticar esportes?',
                      '03.1 Quais esportes você mais gosta?',
                      '04. Você considera que tem alguma dificuldade para praticar esportes?',
                      '05 - Você sabe o que é Fair Play?',
                      '06 - Marque as opções de Fair Play que você já pratica:',
                      '07 - Você sabe o que é protagonismo?',
                      '08 - O que você considera ser protagonismo?',
                      '10 - Quais valores você tem praticado até o momento?',
                      '11 - Você gosta de futebol?',
                      '14 - Você conhece os dribles do futebol?',
                      '15 - Quando você enfrenta dificuldades no dia a dia, como acha que pode superá-las? Marque as opções que você consegue fazer:',
                      '16 - Como o Projeto Futebol de Rua Pela Educação pode ajudar no seu desenvolvimento? Marque as opções mais importantes para você:',
                      '17 - Quais dos temas a seguir você já sabe ou já estudou antes de participar do projeto?']

# Selecionar apenas as colunas relevantes
df_relevante = df[colunas_relevantes]

# Identifica duplicatas baseando-se em colunas específicas (Nome e Idade)
# Mantém apenas uma das duplicatas
df_relevante = df_relevante.drop_duplicates(subset=['NOME COMPLETO DO ALUNO', 'IDADE:'], keep='first')

# Função para contabilizar as respostas e marcar as três mais comuns
def contar_respostas(coluna, n=3):
    # Verificar se a coluna existe
    if coluna in df_relevante.columns:
        # Separar as respostas em itens individuais e contar a frequência de cada um
        todas_respostas = df_relevante[coluna].dropna().str.split(', ').explode()
        frequencias = todas_respostas.value_counts()
        
        # Identificar as três respostas mais comuns
        top_n_respostas = frequencias.nlargest(n).index.tolist()
        
        # Marcar as outras respostas como "Outros"
        def marcar_respostas(respostas):
            marcadas = [resposta if resposta in top_n_respostas else 'Outros' for resposta in respostas.split(', ')]
            return ', '.join(marcadas)
        
        # Aplicar a marcação de "Outros" para todas as respostas na coluna
        return df_relevante[coluna].dropna().apply(marcar_respostas)
    else:
        return df_relevante[coluna]

# Aplicar a função de contabilização para cada coluna específica
colunas_especificas = [
    '03.1 Quais esportes você mais gosta?',
    '06 - Marque as opções de Fair Play que você já pratica:',
    '08 - O que você considera ser protagonismo?',
    '10 - Quais valores você tem praticado até o momento?',
    '14 - Você conhece os dribles do futebol?',
    '15 - Quando você enfrenta dificuldades no dia a dia, como acha que pode superá-las? Marque as opções que você consegue fazer:',
    '16 - Como o Projeto Futebol de Rua Pela Educação pode ajudar no seu desenvolvimento? Marque as opções mais importantes para você:',
    '17 - Quais dos temas a seguir você já sabe ou já estudou antes de participar do projeto?'
]

for coluna in colunas_especificas:
    df_relevante[coluna] = contar_respostas(coluna, n=3)

# Caminho para salvar a nova planilha
output_file = r"C:\Users\FDR Thay\Downloads\novaTabelaDados.xlsx"

# Salvar a nova tabela em um arquivo Excel
df_relevante.to_excel(output_file, index=False)

print(f"Nova planilha criada e salva em {output_file}")

