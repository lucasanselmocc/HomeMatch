# HomeMatch — Sprint 3 Issues (atualizado)
---

## ISSUE 10 — Celery + Redis: infraestrutura de tarefas assíncronas

**Labels:** `infra` `backend` `sprint-2`
**Milestone:** Sprint 3 — Semana 1

### Descrição
As análises de IA não podem bloquear a requisição HTTP. Esta issue configura toda a infraestrutura de filas necessária para as Issues 1, 2, 3 e 4. Pré-requisito hard de tudo relacionado a IA.

### Critérios de aceitação
- [x] Adicionar serviço `redis` ao `docker-compose.yaml` (imagem `redis:7-alpine`)
- [x] Adicionar serviço `celery_worker` ao docker-compose com command `celery -A config worker -l info`
- [x] Criar `config/celery.py` com app Celery configurado
- [x] Adicionar `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND` ao `settings.py`
- [x] Adicionar `celery` e `redis` ao `requirements.txt`
- [x] Criar task de teste (`@shared_task`) que escreve log — confirmar funcionamento manual
- [x] `docker-compose up` sobe Redis + Worker automaticamente

> ⚠️ Pré-requisito de todas as issues de IA. Deve ser a **primeira tarefa concluída** da sprint.

---

## ISSUE 14 — Paginação nas listagens

**Labels:** `backend` `refactor` `sprint-2`
**Milestone:** Sprint 3 — Semana 1

### Descrição
O endpoint `GET /api/properties/` retorna todos os imóveis sem paginação. Com volume real de dados isso causa timeout e sobrecarga no banco.

### Critérios de aceitação
- [x] Criar `HomematchPagination` com `PageNumberPagination`, `page_size=20`
- [x] Permitir `page_size` customizável via query param (`?page_size=10`)
- [x] Definir `max_page_size=100` para evitar abuso
- [x] Aplicar em `CreateListPropertyView`
- [x] Aplicar em `GET /api/properties/{id}/reviews/`
- [ ] Aplicar em `GET /api/users/favorites/`
- [x] Response retorna `{ count, next, previous, results }` (PADRÃO)
- [x] Registrar `DEFAULT_PAGINATION_CLASS` no `REST_FRAMEWORK` do `settings.py`

### Observações
- `max_page_size=100` protege o banco de requisições abusivas com `page_size` muito alto
- A paginação global via `settings.py` evita ter que aplicar manualmente em cada view futura


---

## ISSUE 2 — Busca por linguagem natural

**Labels:** `ai` `backend` `search` `sprint-2`
**Milestone:** Sprint 3 — Semana 1
**Depende de:** #10 #1

### Descrição
O usuário descreve o que quer em texto livre. O sistema usa LLM para extrair filtros e cruza com os atributos visuais da Issue 1, retornando uma lista ranqueada com score de compatibilidade.

### Critérios de aceitação
- [ ] Endpoint `POST /api/search/natural/` recebe `{ "query": "string" }`
- [ ] LLM interpreta a query e retorna JSON estruturado de filtros: `{ brightness, atmosphere, type, max_price, city, ... }`
- [ ] Filtros cruzados com `Properties` que têm `PhotoAnalysis` com `status=done`
- [ ] Cada resultado retorna `match_score` (0–100) calculado por compatibilidade de atributos
- [ ] Fallback: se nenhum imóvel tiver análise de IA, usar filtros padrão do sistema
- [ ] Exemplo funcional: `"apartamento aconchegante com boa iluminação"` → `{ brightness: "high", atmosphere: "cozy", type: "A" }`

> O prompt para extração de filtros deve ser determinístico — instrua o LLM a responder **somente em JSON**, sem texto adicional.

---

## ISSUE 23 — Geocoding e busca de arredores

**Labels:** `backend` `feature` `sprint-3`
**Milestone:** Sprint 3

### Descrição
Ao cadastrar um imóvel, o sistema geocodifica o endereço via **Nominatim** (gratuito) e salva `lat/lng` no banco. Em seguida, dispara uma task Celery que busca pontos de interesse ao redor via **Google Places API** e salva no banco.

### Critérios de aceitação

#### Nominatim
- [x] Criar `NominatimService` em `apps/properties/services.py`
- [x] Geocodifica `address` + `city` do imóvel
- [x] Salva `latitude` e `longitude` via `update_fields`
- [x] `User-Agent` obrigatório nas requisições

#### Google Places
- [x] Criar `NearbyPlacesService` em `apps/properties/services.py`
- [x] Busca por categoria: `restaurant`, `gym`, `school`, `hospital`, `supermarket`, `park`
- [x] Raio de 3km
- [x] Calcula distância via fórmula Haversine
- [x] Salva resultados via `update_or_create`

#### Task Celery
- [x] Criar `buscar_arredores(property_id)` em `apps/properties/tasks.py`
- [x] Disparada no `perform_create` somente se `lat/lng` foram encontrados

#### Configuração
- [x] `GOOGLE_PLACES_API_KEY` no `settings.py` e `.env.example`

### Observações
- Nominatim é gratuito — reserva os créditos do Google só para o Places
- Rate limit do Nominatim: 1 req/s — suficiente para projeto acadêmico
- Se geocoding falhar, `lat/lng` ficam `null` e task não é disparada


## ISSUE 4 — Análise de arredores e índice de segurança

**Labels:** `ai` `backend` `sprint-2`
**Milestone:** Sprint 3 — Semana 1
**Depende de:** #10

### Descrição
Analisa a vizinhança usando APIs externas para fornecer índice de segurança e serviços próximos.

### Critérios de aceitação
- [ ] Model `SurroundingsAnalysis`: `property` (OneToOne FK), `safety_index` (float 0–10), `nearby_services` (JSONField), `walkability_score` (float), `cached_at`
- [ ] Migration para `SurroundingsAnalysis`
- [ ] Integração com **OpenStreetMap Nominatim** (gratuito, sem chave)
- [ ] `safety_index` estimado por LLM com base no bairro e cidade
- [ ] Cache de 7 dias por bairro
- [ ] Endpoint `GET /api/properties/{id}/surroundings/`
- [ ] Bloco `surroundings` incluído no detalhe quando disponível

---

## ISSUE 12 — Match Score: compatibilidade usuário × imóvel 🆕 refinada

**Labels:** `ai` `backend` `frontend` `inovacao` `sprint-2`
**Milestone:** Sprint 3 — Semana 2
**Depende de:** #1

### Descrição
A feature de pitch do projeto. Em vez de listar imóveis por preço, o sistema calcula um percentual de compatibilidade entre o perfil do usuário e cada imóvel.

**Abordagem com pgvector:** o docker-compose já usa `pgvector/pgvector:pg16`. Em vez de cruzar campos separados manualmente, converter preferências do usuário e atributos do imóvel em vetores e usar **similaridade vetorial diretamente no banco** (`embedding <=> query_vector`). Mais preciso, escala melhor, usa infra já configurada.

### Critérios de aceitação
- [ ] Adicionar campo `embedding` tipo `VectorField` (pgvector) ao model `PhotoAnalysis` — gerado a partir dos atributos visuais
- [ ] Função `build_user_vector(user)` que converte `SearchPreference` + histórico de favoritos em vetor de query
- [ ] `GET /api/properties/?match=true` retorna imóveis com `match_score` (0–100), ordenados por similaridade
- [ ] Usuário sem preferências recebe score baseado em popularidade (favoritos + rating médio)
- [ ] Frontend exibe badge `"94% compatível"` nos cards — na listagem e no detalhe
- [ ] Score calculado on-the-fly para refletir preferências atuais

> Feature de pitch: uma demo ao vivo com o badge de compatibilidade é mais memorável do que qualquer slide.

---

## ISSUE 16 — Mapa de imóveis com imóveis próximos

**Labels:** `frontend` `backend` `inovacao` `sprint-2`
**Milestone:** Sprint 3 — Semana 2

### Descrição
Mapa interativo na listagem e no detalhe do imóvel mostrando localização e imóveis próximos. Usa **Leaflet.js** (open source) + **OpenStreetMap Nominatim** para geocoding — sem custo, sem API key.

### Critérios de aceitação

**Backend:**
- [ ] Campos `latitude` e `longitude` (FloatField, null=True) no model `Properties`
- [ ] Migration para os novos campos
- [ ] Celery task `geocode_property(property_id)` — chama Nominatim e salva lat/lng
- [ ] Task disparada via signal `post_save` quando imóvel é criado
- [ ] Endpoint `GET /api/properties/nearby/?lat=X&lng=Y&radius=2` retorna imóveis num raio (padrão 2km)
- [ ] `lat` e `lng` incluídos no serializer de leitura

**Frontend:**
- [ ] **Listagem:** mapa com pins dos imóveis filtrados + toggle "Ver no Mapa / Ver Lista"
- [ ] **Detalhe:** mapa centralizado no imóvel com pins de imóveis próximos
- [ ] Ao clicar no pin, destaca o card correspondente (na listagem) ou abre o detalhe (no mapa de próximos)
- [ ] Pins com cor diferente para venda vs aluguel
- [ ] Leaflet.js via CDN

> OpenStreetMap tem limite de 1 req/s — usar delay na task ou cache de geocoding por endereço.



## ISSUE 19 — Pastas/coleções de imóveis

**Labels:** `backend` `frontend` `ux` `sprint-3`
**Milestone:** Sprint 3

### Descrição
Evolução dos favoritos. Em vez de uma lista plana, o usuário organiza imóveis em coleções nomeadas ("Opções para 2026", "Perto do trabalho", "Mostrar pra família"). Aumenta engajamento e tempo no produto.

### Critérios de aceitação

**Backend:**
- [ ] Model `Collection`: `user` (FK), `name`, `created_at`
- [ ] Model `CollectionItem`: `collection` (FK), `property` (FK), `added_at`
- [ ] `POST /api/users/collections/` — cria coleção
- [ ] `GET /api/users/collections/` — lista com contagem de imóveis
- [ ] `POST /api/users/collections/{id}/items/` — adiciona imóvel
- [ ] `DELETE /api/users/collections/{id}/items/{property_id}/` — remove imóvel
- [ ] `DELETE /api/users/collections/{id}/` — deleta coleção
- [ ] Limite de 20 coleções por usuário

**Frontend:**
- [ ] Botão "Salvar em pasta" no card e no detalhe — dropdown com coleções + "Nova pasta"
- [ ] Página `/collections` com grid de pastas e miniatura das fotos
- [ ] Dentro da pasta: grid de imóveis com opção de remover
- [ ] Modal para criar/renomear pasta

> **Sprint 3** — não bloqueia nada da Sprint 2, mas o backend é simples e pode ser antecipado se sobrar tempo.

---

## ISSUE 15 — Dashboard do anunciante expandido

**Labels:** `frontend` `sprint-2`
**Milestone:** Sprint 3 — Semana 2
**Depende de:** #1

### Critérios de aceitação
- [ ] Status da análise IA por imóvel: `pending` / `processing` / `done` / `failed` com badge colorido
- [ ] Botão "Analisar fotos" que chama `POST /api/properties/{id}/analyze/`
- [ ] Polling do status a cada 5s enquanto `status == processing`
- [ ] Upload de fotos direto no dashboard (input file → `POST /api/properties/{id}/photos/`)
- [ ] Atributos visuais resumidos quando análise concluída

---

## ISSUE 7 — Detalhe do imóvel: seções de IA, mapa e calculadora

**Labels:** `frontend` `sprint-2`
**Milestone:** Sprint 3 — Semana 2
**Depende de:** #1 #3 #4 #16 #17

### Critérios de aceitação
- [ ] Seção **"Análise Visual IA"** — brightness, style, atmosphere com ícones (quando `status == done`)
- [ ] Seção **"Custo de vida estimado"** com breakdown (quando disponível)
- [ ] Seção **"Arredores"** com serviços e barra de `safety_index` (quando disponível)
- [ ] **Mapa** centralizado com pins de imóveis próximos (Issue #16)
- [ ] **Calculadora de financiamento** — apenas para imóveis à venda (Issue #17)
- [ ] Badge `match_score` no card lateral quando usuário logado
- [ ] Cada seção tem estado independente de loading/indisponível

---

## ISSUE 6 — Listagem: mapa, paginação e URL params

**Labels:** `frontend` `sprint-2`
**Milestone:** Sprint 3 — Semana 2
**Depende de:** #14 #12 #16 #18

### Critérios de aceitação
- [ ] Consumir `{ count, next, previous, results }` da API paginada
- [ ] Controles de paginação
- [ ] Filtros refletidos em URL params — links compartilháveis
- [ ] Skeleton loading
- [ ] Badge `"XX% compatível"` nos cards quando `?match=true` e usuário logado
- [ ] Toggle **"Ver no Mapa / Ver Lista"** (Issue #16)
- [ ] Botão **"Me avise quando chegar"** quando resultado vazio ou < 3 imóveis (Issue #18)

---

## ISSUE 21 — Embeddings pgvector completos

**Labels:** `backend` `ai` `sprint-3`
**Milestone:** Sprint 3

### Descrição
O modelo `Properties` já possui o campo `embedding` (vector 1536 dim) mas ele nunca é populado. Esta issue implementa a geração e armazenamento de embeddings para cada imóvel, permitindo busca semântica via pgvector.

### Critérios de aceitação

#### Geração do embedding
- [ ] Criar `EmbeddingService` em `apps/ai_analysis/services.py`
- [ ] Integrar com API de embeddings (OpenAI `text-embedding-3-small` ou equivalente)
- [ ] O embedding deve ser gerado a partir da descrição + atributos visuais extraídos pela LLM
- [ ] Criar `@shared_task` `gerar_embedding(property_id)` em `apps/ai_analysis/tasks.py`
- [ ] Disparar task automaticamente após análise de fotos concluída

#### Busca semântica
- [ ] Criar `SemanticSearchService` em `apps/search/services.py`
- [ ] Recebe texto do usuário, gera embedding da query e busca por similaridade com `pgvector`
- [ ] Endpoint `GET /api/search/?q=quero+algo+aconchegante` retorna imóveis ordenados por similaridade
- [ ] Registrar URL em `apps/search/urls.py`

#### Banco de dados
- [ ] Confirmar que extensão `pgvector` está ativa no PostgreSQL
- [ ] Confirmar que coluna `embedding` está com índice `ivfflat` ou `hnsw` para performance

#### Configuração
- [ ] Adicionar `OPENAI_API_KEY` (ou equivalente) ao `settings.py` e `.env.example`

### Observações
- O campo `embedding` já existe no modelo, não precisa de nova migration
- Sem embedding gerado, a busca semântica retorna vazio — tratar esse caso
- Embeddings devem ser regerados se a descrição do imóvel for atualizada

## ISSUE 22 — Testes automatizados

**Labels:** `backend` `qualidade` `sprint-3`
**Milestone:** Sprint 3

### Descrição
O projeto não possui nenhum teste automatizado. Esta issue implementa a suite de testes cobrindo autenticação, imóveis, reviews e favoritos.

### Critérios de aceitação

#### Configuração
- [ ] Confirmar `coverage` no `requirements-dev.txt`
- [ ] Configurar `pytest-django` como runner de testes
- [ ] Criar `pytest.ini` ou configuração em `setup.cfg`
- [ ] Criar `conftest.py` com fixtures reutilizáveis (usuário, imóvel, token JWT)

#### Testes de autenticação (`apps/users/tests/`)
- [ ] Registro de usuário com dados válidos
- [ ] Registro com email duplicado retorna 400
- [ ] Login com credenciais corretas retorna tokens
- [ ] Login com credenciais erradas retorna 401
- [ ] Logout blacklista o refresh token
- [ ] Refresh token retorna novo access token

#### Testes de imóveis (`apps/properties/tests/`)
- [ ] Listagem pública retorna 200 com paginação
- [ ] Filtros funcionam corretamente
- [ ] Criação por advertiser retorna 201
- [ ] Criação por usuário comum retorna 403
- [ ] Update apenas pelo dono retorna 200
- [ ] Update por outro usuário retorna 403
- [ ] Delete apenas pelo dono retorna 204

#### Testes de reviews (`apps/properties/tests/`)
- [ ] Listagem pública retorna 200
- [ ] Criação por usuário autenticado retorna 201
- [ ] Edição apenas pelo autor retorna 200
- [ ] Delete apenas pelo autor retorna 204

#### Testes de favoritos (`apps/users/tests/`)
- [ ] GET retorna apenas favoritos do usuário autenticado
- [ ] POST adiciona imóvel aos favoritos
- [ ] DELETE remove imóvel dos favoritos
- [ ] Usuário não autenticado retorna 401

#### Meta
- [ ] Cobertura mínima de 80%
- [ ] CI passa com `coverage run -m pytest` no GitHub Actions

### Observações
- Usar `APIClient` do DRF para simular requisições
- Fixtures devem cobrir usuário advertiser e usuário comum separadamente
- Banco de testes separado — configurar `TEST` no `settings.py`

## ISSUE 23 — Notificações in-app via WebSocket

**Labels:** `backend` `feature` `sprint-3`
**Milestone:** Sprint 3

### Descrição
Usuários precisam receber notificações em tempo real — quando um imóvel favoritado tem preço atualizado, quando uma review é feita no seu imóvel, ou quando uma análise de IA é concluída. Esta issue implementa a infraestrutura de WebSocket com Django Channels.

### Critérios de aceitação

#### Infraestrutura
- [ ] Adicionar `channels` e `channels-redis` ao `requirements.txt`
- [ ] Adicionar serviço `channels_worker` ao `docker-compose.yaml`
- [ ] Configurar `CHANNEL_LAYERS` no `settings.py` apontando pro Redis existente
- [ ] Substituir `WSGI_APPLICATION` por `ASGI_APPLICATION` no `settings.py`
- [ ] Atualizar `config/asgi.py` para suportar HTTP + WebSocket

#### App de notificações
- [ ] Criar app `apps/notifications/`
- [ ] Criar modelo `Notification` com campos: `user`, `type`, `message`, `read`, `created_at`
- [ ] Criar migration
- [ ] Criar `NotificationConsumer` em `apps/notifications/consumers.py`
- [ ] Registrar rotas WebSocket em `config/routing.py`

#### Integração
- [ ] Disparar notificação quando análise de IA for concluída (via Celery task)
- [ ] Disparar notificação quando review for criada no imóvel do usuário
- [ ] Endpoint `GET /api/notifications/` lista notificações do usuário autenticado
- [ ] Endpoint `PATCH /api/notifications/{id}/` marca notificação como lida

#### URLs
- [ ] Registrar URLs REST em `apps/notifications/urls.py`
- [ ] Registrar rotas WebSocket em `config/routing.py`

### Observações
- O Redis já está configurado e rodando — reutilizar o mesmo serviço como channel layer
- Autenticação no WebSocket deve usar o JWT existente
- Sem frontend ainda — testar com `wscat` ou Postman WebSocket

## ISSUE 24 — Refresh token via httpOnly cookie

**Labels:** `backend` `segurança` `sprint-3`
**Milestone:** Sprint 3

### Descrição
Atualmente o refresh token é retornado no body da resposta e armazenado no frontend (localStorage ou similar), o que o expõe a ataques XSS. Esta issue move o refresh token para um cookie httpOnly, eliminando esse vetor de ataque.

### Critérios de aceitação

#### Backend
- [ ] Criar `CookieTokenRefreshView` customizada sobrescrevendo `TokenRefreshView` do SimpleJWT
- [ ] Criar `CookieLoginView` customizada sobrescrevendo `TokenObtainPairView`
- [ ] No login, setar cookie httpOnly com o refresh token:
  - `httponly=True`
  - `samesite="Lax"`
  - `secure=True` em produção (`DEBUG=False`)
  - `max_age` igual ao `REFRESH_TOKEN_LIFETIME` do SimpleJWT
- [ ] No refresh, ler o token do cookie em vez do body
- [ ] No logout, deletar o cookie além de blacklistar o token
- [ ] Access token continua sendo retornado no body normalmente

#### Configuração
- [ ] Adicionar `COOKIE_SECURE` ao `settings.py` controlado por `DEBUG`
- [ ] Atualizar `.env.example` com variável de domínio do cookie se necessário

#### URLs
- [ ] Substituir URLs de login e refresh pelas views customizadas em `config/urls.py`

#### Testes
- [ ] Login seta cookie httpOnly na response
- [ ] Refresh lê cookie e retorna novo access token
- [ ] Logout deleta cookie e blacklista token
- [ ] Request sem cookie retorna 401

### Observações
- O access token não muda — apenas o refresh token vai pro cookie
- `CORS_ALLOW_CREDENTIALS = True` precisa ser adicionado ao `settings.py` para o frontend conseguir enviar o cookie
- Testar com Postman habilitando cookies nas configurações da collection


## Resumo por milestone

### Sprint 2 
| # | Issue | Tipo |
|---|-------|------|
| 11 | Encoding requirements.txt | Bug fix |
| 10 | Celery + Redis | Infra |
| 1 | LLM Vision análise de fotos | IA |
| 14 | Paginação | Refactor |
| 13 | Reset senha + troca email | Backend |
| 17 | Calculadora de financiamento | Feature |
| 18 | Alertas "Me avise quando chegar" | Feature |
| 8 | Auth tokens em memória | Frontend |
| 1 | LLM Vision: extração de atributos visuais das fotos

### Sprint 3 (planejamento inicial)
| # | Issue | Tipo |
|---|-------|------|
| 19 | Pastas/coleções de imóveis | Feature |
| — | Embeddings pgvector completos | IA |
| — | Testes automatizados | Qualidade |
| — | Notificações in-app (WebSocket) | Feature |
| — | Refresh token httpOnly cookie | Segurança |
| 2 | Busca por linguagem natural | IA |
| 4 | Arredores e segurança | IA |
| 12 | Match Score com pgvector | IA + Feature |
| 15 | Dashboard anunciante expandido | Frontend |
| 7 | Detalhe com IA + mapa + calc | Frontend |
| 6 | Listagem com mapa + paginação | Frontend |
| 16 | Mapa com imóveis próximos | Feature |



---

> **Já concluído na Sprint 1 e 2 — não entra no backlog:**
> CRUD imóveis · Auth JWT · Upload fotos R2 com validações · Reviews · Permissões por user_type · Signal limpeza órfãos · Fix RegisterSerializer · Frontend base (5 páginas) · Reset de senha e troca de email · Calculadora de financiamento · Alertas "Me avise" · Auth tokens em memória · Análise de fotos pela IA · Celery + Redis · Paginação · Tratamento de exceções

=======================================================

Tag / Nome pra criação das sprints


⚙️ Infraestrutura & Configuração
ISSUE 10 — [INFRA] Celery + Redis: infraestrutura de tarefas assíncronas

ISSUE 11 — [INFRA] Corrigir encoding do requirements.txt para UTF-8

🤖 Inteligência Artificial (App: ai_analysis)
ISSUE 1 — [AI_ANALYSIS] LLM Vision: extração de atributos visuais das fotos

ISSUE 4 — [AI_ANALYSIS] Análise de vizinhança e índice de segurança

🔍 Busca & Imóveis (App: properties)
ISSUE 14 — [PROPERTIES] Implementação de paginação nas listagens de imóveis

ISSUE 2 — [SEARCH] Busca por linguagem natural via processamento LLM

ISSUE 12 — [SEARCH] Match Score: cálculo de compatibilidade com pgvector

ISSUE 16 — [PROPERTIES] Integração OpenStreetMap para imóveis próximos

👤 Usuários & Autenticação (App: users)
ISSUE 13 — [AUTH] Fluxo de redefinição de senha e troca de email

ISSUE 18 — [USERS] Sistema de alertas por email ("Me avise quando chegar")

ISSUE 19 — [USERS] Criação de pastas/coleções para organização de favoritos

💻 Frontend (React / Vite)
ISSUE 8 — [AUTH] Frontend: migração de tokens JWT para memória (segurança)

ISSUE 17 — [FRONTEND] Calculadora interativa de financiamento (SFH)

ISSUE 15 — [FRONTEND] Dashboard do anunciante: status de IA e upload

ISSUE 7 — [FRONTEND] UI Detalhe do Imóvel: seções de IA, mapa e calculadora

ISSUE 6 — [FRONTEND] UI Listagem: toggle de mapa, paginação e parâmetros de URL