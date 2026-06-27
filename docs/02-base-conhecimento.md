# Base de Conhecimento

## Dados Utilizados

O KartBot usa a pasta `data/` como base local de conhecimento. A proposta é manter o agente restrito a fontes controladas, rastreáveis e fáceis de auditar.

| Arquivo | Formato | Utilização no Agente |
|---------|---------|----------------------|
| `produtos_financeiros.json` | JSON | Armazena produtos monitorados no mercado, preço médio calculado e data de coleta |
| `transacoes.csv` | CSV | Registra o histórico financeiro do piloto ou equipe, incluindo entradas e saídas |
| `perfil_investidor.json` | JSON | Mantido como dado legado do desafio original, sem uso principal no KartBot |
| `historico_atendimento.csv` | CSV | Mantido como dado legado do desafio original, sem uso principal no KartBot |

## Adaptações nos Dados

O arquivo `produtos_financeiros.json` foi reaproveitado como base de preços de mercado para produtos de kart. A coleta é feita pelo script `src/google_shopping_scraper.py`, que busca itens no Google Shopping, extrai valores monetários dos resultados com Regex e calcula o preço médio por produto.

O arquivo `transacoes.csv` é a base para análise de gastos. Ele contém campos simples e auditáveis:

```text
data,descricao,categoria,valor,tipo
```

Essa estrutura permite calcular saídas mensais, consultar despesas por categoria e identificar gastos operacionais, como manutenção e inscrição.

## Estratégia de Integração

### Como os dados são carregados?

Os dados são acessados pela camada DAO em `src/dao.py`.

`ProdutoDAO` lê o JSON e converte os registros para objetos tipados `ProdutoMercado`. `TransacaoDAO` lê o CSV e converte cada linha para objetos tipados `Transacao`.

Essa separação evita que a interface Streamlit conheça detalhes de leitura de arquivos, parsing de JSON ou parsing de CSV.

### Como os dados são usados no prompt?

A aplicação `src/app.py` carrega os dados por meio dos DAOs no início da sessão e monta um contexto textual autorizado para o modelo. Esse contexto é enviado como mensagem de sistema junto com o system prompt do KartBot.

O modelo recebe:

- lista de produtos e preços médios do JSON;
- lista de transações do CSV;
- total de despesas de inscrição encontrado no CSV;
- instrução explícita para não usar dados externos.

## Exemplo de Contexto Montado

```text
Contexto autorizado para resposta:
Produtos do JSON: [
  {
    "nome_produto": "Pneu de kart MG vermelho",
    "preco_medio": 720.00,
    "data_coleta": "2026-06-26T20:30:00"
  }
]

Transacoes do CSV: [
  {
    "data": "2026-06-10",
    "descricao": "Inscrição etapa regional",
    "categoria": "inscricao",
    "valor": 350.00,
    "tipo": "saida"
  },
  {
    "data": "2026-06-12",
    "descricao": "Revisão do motor",
    "categoria": "manutencao",
    "valor": 900.00,
    "tipo": "saida"
  }
]

Total de despesas de inscricao no CSV: 350.00
Nao use dados externos, estimativas livres ou conhecimento de mercado fora do contexto acima.
```

## Governança dos Dados

O KartBot foi projetado para favorecer rastreabilidade. Toda resposta financeira deve poder ser explicada por um registro presente no JSON ou no CSV. Se o dado não existir, o agente deve informar a limitação em vez de inventar um valor.

Para melhorar a qualidade da base, recomenda-se:

- atualizar o JSON periodicamente com o scraper;
- padronizar categorias no CSV, como `inscricao`, `manutencao`, `pneus`, `combustivel` e `transporte`;
- registrar todas as saídas com data, descrição, categoria, valor e tipo;
- revisar os resultados do scraper quando o Google Shopping retornar anúncios irrelevantes.
