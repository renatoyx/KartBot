# Avaliação e Métricas

## Objetivo da Avaliação

A avaliação do KartBot verifica se o agente responde com precisão, respeita os dados disponíveis e ajuda na tomada de decisão financeira no contexto de kart.

O foco não é medir criatividade do modelo, mas confiabilidade: o KartBot deve ser útil justamente por limitar suas respostas ao JSON de preços e ao CSV de transações.

## Métricas de Qualidade

| Métrica | O que avalia | Como medir |
|---------|--------------|------------|
| Aderência ao contexto | Se o agente usa apenas dados do JSON e do CSV | Fazer perguntas com e sem dados disponíveis |
| Precisão de cálculo | Se somas, médias e totais estão corretos | Conferir manualmente os valores retornados |
| Clareza financeira | Se a resposta ajuda a decidir orçamento | Avaliar se o cálculo é explicado de forma objetiva |
| Robustez a perguntas fora do escopo | Se o agente recusa pedidos sem dados | Perguntar sobre clima, fornecedores ou eventos não registrados |
| Utilidade operacional | Se a resposta é aplicável para piloto ou equipe | Testar perguntas reais de custo de etapa, manutenção e compra |

## Cenários de Teste

### Teste 1: Custo de etapa

- Pergunta: "Quanto devo reservar para uma etapa?"
- Resposta esperada: soma do preço médio de um jogo de pneus novo com despesas de inscrição presentes no CSV.
- Critério de aprovação: cálculo correto e explicação da origem dos valores.

### Teste 2: Produto monitorado

- Pergunta: "Qual é o preço médio do pneu de kart MG vermelho?"
- Resposta esperada: valor do item conforme `data/produtos_financeiros.json`.
- Critério de aprovação: não usar valor externo ao JSON.

### Teste 3: Histórico mensal

- Pergunta: "Quanto foi gasto no mês?"
- Resposta esperada: soma das transações de saída do mês solicitado ou disponível no CSV.
- Critério de aprovação: total compatível com `TransacaoDAO.get_total_gasto_mes`.

### Teste 4: Manutenção

- Pergunta: "Quais despesas de manutenção existem?"
- Resposta esperada: lista de transações cuja categoria ou descrição indique manutenção.
- Critério de aprovação: retornar apenas registros existentes no CSV.

### Teste 5: Pergunta fora do escopo

- Pergunta: "Qual piloto vai vencer a próxima corrida?"
- Resposta esperada: recusa clara, informando que o contexto não contém esse tipo de dado.
- Critério de aprovação: não inventar previsão ou opinião.

## Escala de Avaliação Manual

Cada resposta pode ser avaliada de 1 a 5:

| Nota | Interpretação |
|------|---------------|
| 1 | Resposta incorreta ou inventada |
| 2 | Resposta parcialmente correta, mas confusa |
| 3 | Resposta útil, com lacunas de explicação |
| 4 | Resposta correta e clara |
| 5 | Resposta correta, clara e diretamente acionável |

## Resultados Esperados

**O que deve funcionar bem:**

- respostas sobre produtos presentes no JSON;
- cálculo de custo de etapa com pneus e inscrição;
- leitura de gastos no CSV;
- limitação explícita quando falta dado;
- explicação objetiva de cálculos financeiros.

**O que pode melhorar:**

- ampliar a base real de transações de kart;
- padronizar categorias de despesa;
- adicionar testes automatizados para os DAOs;
- registrar logs de chamadas ao modelo;
- criar dashboard com evolução mensal de custos.

## Métricas Técnicas Recomendadas

Além da avaliação qualitativa, a aplicação pode monitorar:

- tempo de resposta da API de LLM;
- taxa de erro nas chamadas HTTP;
- quantidade de perguntas recusadas por falta de contexto;
- número de produtos monitorados;
- data da última coleta de preços;
- divergência entre preço médio atual e preço médio anterior.

Essas métricas ajudam a transformar o KartBot em uma ferramenta operacional de acompanhamento financeiro, não apenas em um protótipo conversacional.
