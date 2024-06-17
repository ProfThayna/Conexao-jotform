import requests

# Sua chave de API do JotForm
api_key = ''

# ID do formulário que você deseja buscar
form_id = ''

url = f'https://api.jotform.com/form/{form_id}/submissions?apiKey={api_key}'

# Faz a requisição à API
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    data = response.json()
    submissions = data.get('content', [])
    
    # Exibindo as respostas
    for submission in submissions:
        print(submission)
else:
    print(f"Erro ao acessar a API: {response.status_code}")