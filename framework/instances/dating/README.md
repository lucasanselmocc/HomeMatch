# Instância Dating / Relacionamentos

Esta instância demonstra o uso do framework HomeMatch em uma aplicação estilo Tinder, baseada em perfis, interesses e compatibilidade.

## O que ela usa do framework

- Usuários: pessoas cadastradas na plataforma.
- Postagens: perfis públicos de relacionamento.
- Fotos: fotos associadas ao perfil.
- Atributos: interesses, hobbies, estilo de vida e atributos extraídos por análise de imagem.
- Busca natural: frases como “pessoas que gostam de praia e praticam esportes”.
- Match-score: compatibilidade entre o usuário atual e os perfis candidatos.

## Rodar somente esta instância

```bash
uvicorn framework.instances.dating.api:api --reload --port 8002
```

Acesse:

```txt
http://localhost:8002
```

## Rodar pelo Docker

```bash
docker compose up --build dating_api
```

Acesse:

```txt
http://localhost:8002
```
