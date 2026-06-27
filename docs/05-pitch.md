# Pitch do KartBot

## Roteiro de 3 Minutos

### 1. O Problema

No automobilismo, controlar orçamento é tão importante quanto acertar o setup do kart. Pilotos e equipes precisam lidar com pneus, inscrições, manutenção, peças, transporte e treinos. Esses custos muitas vezes ficam espalhados em planilhas, mensagens e cotações manuais.

O resultado é previsibilidade baixa: o piloto sabe que vai gastar, mas nem sempre sabe quanto, onde o orçamento está escapando ou qual decisão pesa mais antes de uma etapa.

### 2. A Solução

O KartBot é um consultor financeiro com IA Generativa para equipes de kart. Ele cruza preços médios de mercado com o histórico financeiro do piloto ou da equipe e responde em uma interface de chat.

A arquitetura combina três partes:

- Selenium e Regex para automatizar a coleta de preços no Google Shopping;
- padrão DAO para organizar a leitura do JSON de produtos e do CSV de transações;
- Streamlit para oferecer uma interface conversacional simples e rápida.

O agente usa um prompt restritivo: ele só pode responder com os dados do JSON e do CSV. Se perguntarem sobre o custo de uma etapa, ele soma a média de um jogo de pneus novo com as despesas de inscrição registradas.

### 3. Demonstração

Na demonstração, o fluxo ideal é:

1. Mostrar o scraper buscando produtos como pneus, capacetes, viseiras e acessórios.
2. Abrir o JSON gerado com os preços médios.
3. Mostrar o CSV de transações da equipe.
4. Abrir o Streamlit e perguntar: "Quanto devo reservar para uma etapa?"
5. Mostrar o KartBot respondendo com cálculo baseado apenas nos dados locais.
6. Fazer uma pergunta fora da base, como "qual o custo de um item não monitorado?", e mostrar o agente recusando inventar valor.

### 4. Diferencial e Impacto

O diferencial do KartBot é levar inteligência financeira para um ambiente onde a tomada de decisão costuma ser rápida, prática e pressionada por orçamento.

Para pilotos amadores, ele ajuda a entender o custo real de competir. Para equipes profissionais, cria uma base mais organizada para planejamento, comparação de gastos e controle operacional.

O impacto é direto: menos achismo, mais rastreabilidade e decisões financeiras mais consistentes dentro do esporte.

## Texto Corrido para Apresentação

```text
O KartBot nasceu para resolver uma dor comum no kart: controlar o custo real de competir.

Em uma etapa, o piloto precisa considerar pneus, inscrição, manutenção, peças e outros gastos. Só que essas informações normalmente ficam espalhadas em planilhas, mensagens e cotações feitas manualmente. Isso torna o orçamento imprevisível.

A solução é um consultor financeiro com IA Generativa especializado em equipes de kart. O KartBot coleta preços de mercado usando Selenium em modo headless, extrai valores com Regex e salva os preços médios em um JSON. Depois, uma camada DAO lê esse JSON e também o histórico financeiro em CSV. Por fim, uma interface em Streamlit permite conversar com o agente.

O ponto mais importante é a segurança da resposta: o KartBot usa apenas os dados fornecidos. Se eu perguntar o custo de uma etapa, ele soma a média de um jogo de pneus novo com as despesas de inscrição presentes no CSV. Se o dado não existir, ele informa a limitação em vez de inventar.

Com isso, pilotos amadores ganham previsibilidade e equipes profissionais ganham uma base mais organizada para tomada de decisão. O KartBot transforma dados simples em controle financeiro prático para o automobilismo.
```

## Checklist do Pitch

- [x] Duração máxima de 3 minutos
- [x] Problema claramente definido
- [x] Solução demonstrável na prática
- [x] Diferencial técnico explicado
- [x] Impacto para kart amador e profissional
- [ ] Vídeo gravado e publicado

## Link do Vídeo

Link a ser adicionado após a gravação do pitch.
