# 🚀 Inforday API

> API responsável pelo gerenciamento de inscrições do **Inforday**, incluindo cadastro de participantes, envio de e-mails de confirmação e validação de presença através de **QR Code**.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Manager-60A5FA?style=for-the-badge\&logo=poetry\&logoColor=white)

</p>

---

## 📌 Sobre o projeto

O **Inforday API** é o backend responsável por centralizar as funcionalidades do sistema de inscrições do evento.

Entre suas principais funções estão:

* 📝 Gerenciamento de inscrições
* 📧 Envio de e-mails de confirmação
* 🎟️ Geração e validação de QR Codes
* ✅ Controle de check-in dos participantes
* 🗄️ Integração com PostgreSQL
* 📚 Documentação automática através do FastAPI

---

# 🚀 Como executar o projeto

Siga os passos abaixo na ordem.

## 🛠️ 1. Pré-requisitos

Antes de começar, certifique-se de ter instalado:

* 🐍 **Python 3.10 ou superior**
* 🐘 **PostgreSQL**
* 📦 **Poetry**
* 🔧 **Git**

Para verificar se estão instalados:

```bash
python3 --version
psql --version
git --version
poetry --version
```

> 💡 **Dica:** caso algum comando não seja reconhecido, instale a ferramenta correspondente antes de continuar.

---

## 📥 2. Clonar o repositório

Abra o terminal e execute:

```bash
git clone https://github.com/crisocean/inforday-api.git
```

Depois, entre na pasta:

```bash
cd inforday-api
```

---

## 📦 3. Instalar as dependências

O projeto utiliza o **Poetry** para gerenciamento das dependências e do ambiente virtual.

Execute:

```bash
poetry install
```

O Poetry irá configurar automaticamente o ambiente necessário para executar a aplicação.

Para verificar o ambiente:

```bash
poetry env info
```

---

## 🗄️ 4. Configurar o PostgreSQL

O projeto utiliza o **PostgreSQL** como banco de dados.

### Criar o banco

Abra o PostgreSQL pelo **DBeaver**, **pgAdmin** ou `psql` e execute:

```sql
CREATE DATABASE inforday_db;
```

### Criar as tabelas

Na raiz do projeto existe o arquivo:

```text
schema.sql
```

Execute esse arquivo no banco `inforday_db`.

Pelo terminal:

```bash
psql -U postgres -d inforday_db -f schema.sql
```

> 🐘 **DBeaver:** também é possível abrir o `schema.sql`, selecionar o banco `inforday_db` e executar o script diretamente pela interface.

---

## 🔐 5. Configurar as variáveis de ambiente

Na raiz do projeto, crie um arquivo chamado:

```text
.env
```

A estrutura ficará semelhante a:

```text
inforday-api/
├── .env
├── schema.sql
├── main.py
├── pyproject.toml
└── ...
```

Dentro do `.env`, adicione:

```env
# 🗄️ Banco de dados
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres
DB_NAME=inforday_db

# 📧 E-mail
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

### ⚠️ Atenção

O `.env` contém informações sensíveis.

**Nunca envie esse arquivo para o GitHub.**

Verifique se ele está presente no `.gitignore`:

```gitignore
.env
```

> 🔒 **Regra de ouro:** credenciais, senhas e chaves nunca devem ser versionadas.

---

# 📧 6. Configurar o Gmail

A API utiliza uma conta do Gmail para enviar os e-mails de confirmação.

Para isso, utilize uma **Senha de app do Google**.

### 🔑 Criando uma senha de app

1. Acesse sua **Conta do Google**.
2. Entre em **Segurança**.
3. Ative a **Verificação em duas etapas**.
4. Procure por **Senhas de app**.
5. Crie uma nova senha.
6. Utilize um nome como:

```text
Inforday API
```

7. O Google irá gerar uma senha de 16 caracteres.
8. Coloque essa senha no `.env`:

```env
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

> 📌 Não utilize a senha normal da sua conta Google.

---

# ▶️ 7. Executar a API

Com o PostgreSQL funcionando e o `.env` configurado, execute:

```bash
poetry run uvicorn main:app --reload
```

Se tudo estiver correto, você verá algo semelhante a:

```text
Uvicorn running on http://127.0.0.1:8000
```

🎉 **A API está rodando!**

---

# 🌐 8. Acessar a aplicação

### 🏠 API

Acesse:

**http://127.0.0.1:8000**

### 📚 Swagger UI

A documentação interativa está disponível em:

**http://127.0.0.1:8000/docs**

> 💡 O Swagger permite visualizar e testar as rotas da API diretamente pelo navegador.

---

# ✅ 9. Verificar a instalação

Para confirmar que tudo está funcionando:

### ① 🖥️ Verifique o terminal

O servidor deve estar executando sem erros.

A aplicação também deverá informar que o pool de conexões com o PostgreSQL foi aberto com sucesso:

```text
Pool de conexões com o PostgreSQL aberto com sucesso!
```

### ② 🌐 Teste a API

Abra:

**http://127.0.0.1:8000**

A aplicação deverá retornar a resposta da rota inicial.

### ③ 📚 Teste o Swagger

Abra:

**http://127.0.0.1:8000/docs**

As rotas da API deverão aparecer na documentação interativa.

---

# ⚡ Execução rápida

Depois de configurar o PostgreSQL e o `.env`, o fluxo principal é:

```bash
git clone https://github.com/crisocean/inforday-api.git

cd inforday-api

poetry install

poetry run uvicorn main:app --reload
```

Depois acesse:

🌐 **API:** http://127.0.0.1:8000

📚 **Documentação:** http://127.0.0.1:8000/docs

---

# ❗ Problemas comuns

<details>
<summary>🔴 <b>poetry: command not found</b></summary>

O Poetry não está instalado ou não está disponível no PATH.

Verifique:

```bash
poetry --version
```

</details>

<details>
<summary>🔴 <b>Erro de conexão com PostgreSQL</b></summary>

Verifique se:

* PostgreSQL está em execução;
* o banco `inforday_db` existe;
* usuário e senha estão corretos;
* os dados do `.env` estão corretos.

</details>

<details>
<summary>🔴 <b>Erro relacionado ao Gmail</b></summary>

Verifique se:

* a verificação em duas etapas está ativada;
* você está utilizando uma Senha de app;
* a senha foi colocada corretamente no `.env`.

</details>

<details>
<summary>🔴 <b>ModuleNotFoundError</b></summary>

Instale novamente as dependências:

```bash
poetry install
```

Depois execute:

```bash
poetry run uvicorn main:app --reload
```

</details>

---

<p align="center">

### 🚀 Inforday API

**Backend do sistema de inscrições e check-in do Inforday.**

</p>
