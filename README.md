# IVER Financeiro

Sistema web de gestão financeira para o restaurante **IVER**, desenvolvido em **Django** para substituir a planilha operacional usada no controle diário e mensal da empresa.

O sistema centraliza:

- faturamento diário e mensal
- controle de despesas
- folha de pagamento
- despesas trabalhistas
- DRE anual dinâmica
- cadastros administrativos

## Visão Geral

O projeto foi pensado para funcionar como a base operacional financeira do restaurante, sem depender de planilhas externas para cálculo da DRE.

Regras principais já implementadas:

- o faturamento líquido é sempre `90%` do faturamento bruto
- a taxa de serviço é sempre `10%`
- a DRE usa `mes_referencia` e `ano_referencia` das despesas
- a produtividade da folha é calculada automaticamente por setor/cargo
- novas subcategorias de despesas aparecem automaticamente na DRE

## Stack

- Python 3
- Django 5.2.x
- PostgreSQL
- Django Templates
- Bootstrap 5
- `django-crispy-forms`
- `crispy-bootstrap5`
- `django-filter`
- `openpyxl`

## Observação de Ambiente

A especificação original pede **Python 3.12**.  
O projeto foi montado e validado neste ambiente com **Python 3.14**.

Na prática:

- para aderência total à especificação, prefira Python `3.12`
- no ambiente atual, o projeto já foi testado com Python `3.14`

## Estrutura do Projeto

```text
Iver/
├── cadastros/
├── config/
├── core/
├── despesas/
├── dre/
├── faturamento/
├── fixtures/
├── folha/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── .env.example
```

## Módulos

### Dashboard

A página inicial apresenta:

- faturamento bruto do mês
- total de despesas do mês
- saldo líquido do mês
- total da folha do mês
- gráfico de faturamento x despesas
- alertas de despesas próximas do vencimento
- pendências de pagamentos da folha

### Cadastros

Responsável pelos dados mestres do sistema:

- bancos
- setores
- cargos
- colaboradores
- formas de pagamento
- categorias de despesa
- subcategorias de despesa

O menu lateral permite expandir **Cadastros** e acessar diretamente cada tipo de registro.

### Faturamento

Registra o fechamento diário do restaurante com:

- dinheiro
- PIX
- crédito
- débito
- fiado
- vale
- faturamento do bar
- faturamento da cozinha

Recursos:

- cadastro diário
- edição por dia
- filtro por mês e ano
- resumo mensal com total bruto, taxa de serviço, total líquido, dias trabalhados e média diária

### Despesas

Gerencia contas a pagar e classificação contábil.

Recursos:

- CRUD completo
- filtros por mês, ano, categoria, subcategoria e status
- marcação de pagamento
- resumo mensal por categoria e subcategoria
- gráfico por categoria no mês selecionado

### Folha

Controla os períodos mensais e os lançamentos por colaborador.

Recursos:

- criação de período de folha
- geração automática dos lançamentos para colaboradores ativos
- cálculo automático de INSS, salário líquido, adiantamento, saldo final e produtividade
- benefícios por colaborador
- despesas trabalhistas do mês
- histórico por colaborador
- ações inline para marcar pagamentos

### DRE

A DRE não possui modelos próprios.  
Ela é montada dinamicamente a partir dos dados de:

- faturamento
- despesas
- folha
- despesas trabalhistas

Recursos:

- visualização anual
- colunas de janeiro a dezembro
- total anual por linha
- exportação para `.xlsx`

## Regras de Negócio Importantes

### Faturamento

- `RegistroFaturamento.total` é a soma dos métodos de pagamento
- `faturamento_bar` e `faturamento_cozinha` podem ser zero

### Despesas

- a DRE considera `mes_referencia` e `ano_referencia`
- `data_pagamento` serve para fluxo financeiro, não para competência contábil

### Folha

- `inss = 7,5%` do salário bruto
- `salario_liquido = salario_bruto - inss - vale_consumo`
- `adiantamento = 40%` do salário líquido
- `saldo_final = 60%` do salário líquido

### Produtividade

O cálculo é automático ao sincronizar o período da folha:

- cargos de `BAR` usam o faturamento do bar
- cargos de `COZINHA` usam o faturamento da cozinha
- cargos de `SALÃO` e `ADM` usam o faturamento bruto total do mês

### DRE

- taxa de serviço = `10%`
- receita líquida = `90%`
- novas subcategorias cadastradas passam a aparecer automaticamente no demonstrativo

## Instalação

### 1. Clonar o projeto

```bash
git clone https://github.com/jotapn/iver_finan.git
cd iver_finan
```

### 2. Criar e ativar ambiente virtual

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o Python 3.12 não estiver disponível, o projeto também roda no ambiente validado com Python 3.14.

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um `.env` com base no arquivo `.env.example`.

Exemplo:

```env
DJANGO_SECRET_KEY=troque-esta-chave
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=iver_financeiro
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Banco de Dados

Por padrão:

- se `POSTGRES_DB` estiver configurado, o sistema usa PostgreSQL
- se `POSTGRES_DB` não estiver configurado, o sistema usa SQLite local

Isso facilita desenvolvimento e testes rápidos.

## Migrações

Aplicar migrações:

```bash
python manage.py migrate
```

## Executando o Projeto

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## Login

O sistema usa autenticação padrão do Django.

Para criar um usuário administrador:

```bash
python manage.py createsuperuser
```

Admin:

```text
/admin/
```

## Testes

Executar a suíte:

```bash
python manage.py test
```

Validar a configuração:

```bash
python manage.py check
```

## Deploy com Docker

### 1. Preparar variáveis

Use `.env.example` como base e ajuste pelo menos:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- credenciais de `POSTGRES_*`

### 2. Subir os containers

```bash
docker compose up -d --build
```

### 3. Criar usuário administrador

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Publicação na VPS/CPS

- exponha apenas a aplicação web para fora do servidor
- mantenha o PostgreSQL sem porta pública
- coloque Nginx ou Caddy na frente do container `web`
- encaminhe HTTPS para a porta `8000`
- use o endpoint `/healthz/` para monitoramento

### 5. Validar produção

```bash
docker compose logs -f web
docker compose ps
```

## Arquivos Importantes

- `config/settings.py`
- `config/urls.py`
- `core/services.py`
- `faturamento/services.py`
- `folha/services.py`
- `dre/services.py`

## Estado Atual

O sistema já possui:

- estrutura completa do projeto Django
- autenticação obrigatória nas áreas principais
- dashboard funcional
- cadastros via frontend
- faturamento com resumo mensal
- despesas com filtros e resumo
- folha com cálculo automático base
- DRE dinâmica com exportação XLSX
- testes automatizados básicos

## Observação Sobre Dados de Carga

Os arquivos usados para alimentar banco local a partir da planilha foram mantidos fora do versionamento do Git.

Isso evita subir para o repositório:

- bases locais temporárias
- arquivos auxiliares de importação
- dados operacionais que servem apenas para carga manual

## Próximos Passos Sugeridos

- continuar a revisão e importação mês a mês do histórico financeiro
- conectar definitivamente ao PostgreSQL de produção ou homologação
- criar seed inicial de usuário administrador
- melhorar paginação, mensagens e validações
- adicionar importação via CSV ou XLSX

## Repositório

GitHub:

```text
https://github.com/jotapn/iver_finan
```
