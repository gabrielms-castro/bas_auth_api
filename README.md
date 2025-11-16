
# BAS Auth API

## Descrição

BAS Auth API é uma aplicação Django que permite o gerenciamento de códigos TOTP (Time-based One-Time Password) para diferentes serviços. 
Os usuários podem criar, editar e excluir serviços, além de gerar códigos TOTP automaticamente, com suporte para integração via API.

![Client/Server Flow](/docs/flow.png)
---

## Funcionalidades

- **Gerenciamento de Serviços**: Cadastro, edição e exclusão de serviços com chaves TOTP.
- **Geração de Códigos TOTP**: Criação de códigos temporários automáticos para autenticação.
- **Integração via API**: Suporte para geração de códigos por requisição externa.
- **Interface Web**: Interface amigável para os usuários gerenciarem seus serviços.
- **Login/Logout**: Sistema seguro de autenticação de usuários.

---

## Requisitos do Sistema

- **Python**: 3.10 ou superior.
- **Django**: 5.1.3.
- **Banco de Dados**: SQLite (ou outro configurado).
- **Bibliotecas Adicionais**:
  - `djangorestframework`
  - `djangorestframework-simplejwt`
  - `pyotp`

---

## Configuração e Instalação

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/seu-usuario/bas-auth-api.git
   cd bas-auth-api
   ```

2. **Crie um ambiente virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crie um superusuário para acessar o painel administrativo**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor de desenvolvimento**:

   ```bash
   python manage.py runserver
   ```

   O servidor estará disponível em `http://127.0.0.1:8000`.

---

## Estrutura do Projeto

- **authentication**: Gerenciamento de autenticação de usuários.
- **otp**: Lógica para gerenciamento de chaves TOTP e APIs associadas.
- **templates**: Arquivos HTML para a interface web.
- **static**: Arquivos CSS e JavaScript.

---

## Como Usar

### Interface Web

1. Acesse o sistema em `http://127.0.0.1:8000`.
2. Faça login com seu usuário e senha.
3. Gerencie seus serviços diretamente pela interface.

### API

- **Gerar Código TOTP**:

  **Endpoint**: `/api/v1/totp/`  
  **Método**: `POST`  
  **Cabeçalho**: `Authorization: Bearer <token>`  
  **Body**:
  ```json
  {
      "nome_servico": "NomeDoServico"
  }
  ```

  **Resposta**:
  ```json
  {
      "totp_code": "123456"
  }
  ```

---

## Deploy no PythonAnywhere

1. Faça upload dos arquivos do projeto.
2. Configure o ambiente virtual e instale as dependências.
3. Configure o WSGI para apontar para o arquivo `wsgi.py` do Django.
4. Reinicie o aplicativo na interface do PythonAnywhere.


## Exemplo de Client em Python:
```py
class AuthClient:
    def __init__(self):
        self.__user = os.getenv("USUARIO")
        self.__password = os.getenv("SENHA")
        self.__base_url = ""
        self.__token = self.get_refresh_token()
    
    def get_refresh_token(self):
        endpoint = "/token/"
        payload = {"username":self.__user, "password":self.__password}
        try:
            response = requests.post(
                url=f"{self.__base_url}{endpoint}",
                data=payload
            )
            response.raise_for_status()
            return response.json().get("access")
        except requests.exceptions.RequestException as e:
            return f"Erro ao acessar a API: {e}"
        except ValueError:
            return "Erro ao processar a resposta da API."            

    def get_totp(self, nome_servico, endpoint="totp/"):
        payload = {
            "nome_servico": nome_servico,
        }
        url = f"{self.__base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.__token}"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("totp_code")
        
        except requests.exceptions.RequestException as e:
            return f"Erro ao acessar a API: {e}"
        
        except ValueError:
            return "Erro ao processar a resposta da API."
```

---

## Licença

Este projeto é licenciado sob a MIT License. Consulte o arquivo `LICENSE` para mais detalhes.

---

## Autor

**Gabriel Santos de Castro**  
Entre em contato: [gabrielms.castro@gmail.com](mailto:gabrielms.castro@gmail.com)
