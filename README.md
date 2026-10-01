# Escute e Adivinhe

> **Status: arquivado.** Este projeto não receberá novas funcionalidades. O motivo está na seção [Por que foi arquivado](#por-que-foi-arquivado).

Projeto de estudo: um jogo em que o usuário ouve um trecho curto de uma música das suas próprias playlists do Spotify e tenta adivinhar qual é.

Só o backend chegou a ser construído. O jogo em si (sorteio de trecho, reprodução e pontuação) e o frontend nunca foram implementados.

## Por que foi arquivado

A ideia dependia de tocar trechos aleatórios de 5 segundos de músicas do Spotify e de esconder as informações da faixa para que o usuário pudesse adivinhar. Ao revisar as regras da plataforma, encontrei duas barreiras:

- A [Developer Policy do Spotify](https://developer.spotify.com/policy), na seção III ("Some prohibited applications"), diz: *"Do not create a game, including trivia quizzes."*
- Os [termos dos Widgets/Embeds](https://developer.spotify.com/documentation/embeds/terms) exigem exibir o player sem alteração e proíbem ofuscá-lo. Esconder o nome da faixa no embed contraria essa regra.

Também avaliei alternativas (áudio via YouTube, Deezer, Apple Music, SoundCloud e arquivos enviados pelo usuário). Nenhuma atendia à ideia original, que era usar as músicas do próprio usuário de forma simples e dentro das regras. Por isso decidi encerrar o projeto em vez de publicá-lo em desacordo com as diretrizes.

As regras podem mudar. Consulte sempre as páginas oficiais linkadas acima.

## O que foi implementado

- Login via Spotify (OAuth 2.0, authorization code), com criação ou atualização do usuário pelo `spotify_id`.
- Sessão própria da aplicação: JWT de acesso e refresh token em cookies `httponly`.
- Armazenamento dos tokens do Spotify no banco, com renovação automática do access token quando o Spotify responde 401.
- Endpoint protegido que lista as playlists do usuário.
- Banco PostgreSQL com SQLAlchemy assíncrono e migrations Alembic.
- Ambiente de desenvolvimento com Docker Compose.

## Stack

- Python 3.12, FastAPI e Uvicorn
- SQLAlchemy (async) com asyncpg e Alembic
- PostgreSQL 18
- python-jose (JWT), httpx e pydantic-settings
- Docker e Docker Compose

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/auth/login` | Redireciona para a autorização do Spotify |
| GET | `/api/auth/callback` | Recebe o `code`, cria a sessão e define os cookies |
| GET | `/api/spotify/playlists` | Lista as playlists do usuário (requer login) |

A documentação interativa fica em `http://localhost:8000/docs`.

## Como rodar

1. Crie um app no [painel do Spotify for Developers](https://developer.spotify.com/dashboard) e cadastre o redirect URI `http://localhost:8000/api/auth/callback`.
2. Copie `backend/.env.example` para `backend/.env` e preencha os valores. O compose também lê `DB_USER`, `DB_PASSWORD` e `DB_NAME` desse arquivo.
3. Suba os serviços:

   ```bash
   docker compose -f compose.dev.yaml up --build
   ```

4. Aplique as migrations dentro do container do backend:

   ```bash
   docker compose -f compose.dev.yaml exec backend alembic upgrade head
   ```

O backend responde em `http://localhost:8000` e o Postgres fica exposto em `localhost:5431`.