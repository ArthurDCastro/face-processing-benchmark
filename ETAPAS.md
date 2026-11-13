# Etapas do projeto — Face Processing Benchmark

## Objetivo

Desenvolver uma avaliação experimental independente de métodos clássicos e modelos de aprendizado profundo para **detecção facial, centralização e recorte de imagens e segmentação de pessoas (remoção de fundo)**. O projeto busca comparar qualidade, robustez e custo computacional, além de investigar como a centralização e o recorte influenciam os resultados da segmentação.

> **Escopo:** pesquisa independente, sem depender de uma aplicação específica. A escolha dos métodos será baseada em critérios científicos, disponibilidade e viabilidade experimental.

## Etapa 1 — Seleção de métodos e modelos

- [ ] 1.1. Listar os métodos clássicos de detecção facial candidatos.
- [ ] 1.2. Listar os modelos de aprendizado profundo para detecção facial candidatos.
- [ ] 1.3. Selecionar os métodos de centralização e recorte a comparar.
- [ ] 1.4. Listar os métodos clássicos de segmentação de pessoas candidatos.
- [ ] 1.5. Listar os modelos de aprendizado profundo para segmentação de pessoas candidatos.
- [ ] 1.6. Localizar os artigos científicos e repositórios de cada candidato.
- [ ] 1.7. Verificar disponibilidade de código, pesos, dependências e licenças.
- [ ] 1.8. Montar uma tabela com candidatos, características e referências.
- [ ] 1.9. Definir e justificar a lista final de métodos e modelos.

**Entrega:** tabela de métodos selecionados, referências e justificativas.

## Etapa 2 — Preparação dos dados e do protocolo experimental

- [ ] 2.1. Pesquisar datasets públicos para avaliação de detecção facial.
- [ ] 2.2. Pesquisar datasets públicos de retratos com máscaras de segmentação.
- [ ] 2.3. Selecionar os datasets e verificar suas condições de uso.
- [ ] 2.4. Baixar e organizar as imagens e anotações.
- [ ] 2.5. Criar um script para validar imagens, máscaras e identificadores.
- [ ] 2.6. Definir as métricas de avaliação de cada tarefa.
- [ ] 2.7. Definir as configurações dos experimentos e os cenários de teste.
- [ ] 2.8. Criar os arquivos de configuração e a estrutura de diretórios.
- [ ] 2.9. Preparar um conjunto pequeno de imagens para validar os scripts.

**Entrega:** datasets organizados, métricas e protocolo experimental definidos.

## Etapa 3 — Implementação dos métodos

- [ ] 3.1. Criar o repositório e configurar o ambiente Python.
- [ ] 3.2. Implementar ou integrar os detectores faciais clássicos.
- [ ] 3.3. Implementar ou integrar os detectores faciais baseados em aprendizado profundo.
- [ ] 3.4. Implementar os métodos de centralização e recorte.
- [ ] 3.5. Implementar os métodos clássicos de segmentação de pessoas.
- [ ] 3.6. Integrar os modelos de aprendizado profundo para segmentação.
- [ ] 3.7. Padronizar as interfaces de entrada e saída dos algoritmos.
- [ ] 3.8. Implementar a transformação das máscaras de referência conforme o recorte e demais transformações geométricas.
- [ ] 3.9. Implementar o cálculo das métricas de avaliação.
- [ ] 3.10. Implementar a coleta de tempo de execução e memória.
- [ ] 3.11. Criar scripts independentes para executar cada método e experimento.
- [ ] 3.12. Testar cada implementação com o conjunto pequeno de validação.
- [ ] 3.13. Criar um script para executar os experimentos em lote.

**Entrega:** métodos funcionais, testes básicos e scripts independentes e reproduzíveis.

## Etapa 4 — Execução e geração dos resultados

- [ ] 4.1. Executar os experimentos de detecção facial.
- [ ] 4.2. Executar os experimentos de centralização e recorte.
- [ ] 4.3. Executar os experimentos de segmentação com métodos clássicos.
- [ ] 4.4. Executar os experimentos de segmentação com modelos de aprendizado profundo.
- [ ] 4.5. Executar os experimentos de influência da centralização e do recorte na segmentação, incluindo imagens originais como referência de comparação.
- [ ] 4.6. Executar os experimentos de desempenho computacional.
- [ ] 4.7. Executar os experimentos com combinações selecionadas de métodos.
- [ ] 4.8. Consolidar e validar os resultados obtidos, registrando falhas e configurações.
- [ ] 4.9. Gerar as estatísticas, tabelas e gráficos comparativos.
- [ ] 4.10. Selecionar e organizar exemplos visuais dos resultados.

**Entrega:** arquivos de resultados brutos, estatísticas, gráficos, tabelas e exemplos visuais.

## Etapa 5 — Análise e discussão dos resultados

- [ ] 5.1. Comparar a precisão e o desempenho dos detectores faciais.
- [ ] 5.2. Avaliar as diferenças entre os métodos de centralização e recorte.
- [ ] 5.3. Comparar os métodos clássicos e de aprendizado profundo na segmentação.
- [ ] 5.4. Analisar a influência da centralização e do recorte sobre a segmentação.
- [ ] 5.5. Avaliar diferenças estatísticas e a consistência dos resultados.
- [ ] 5.6. Identificar os melhores métodos para diferentes condições e objetivos.
- [ ] 5.7. Discutir limitações, falhas e possíveis explicações para os resultados.
- [ ] 5.8. Consolidar as conclusões dos experimentos.

**Entrega:** interpretação científica dos resultados, comparações fundamentadas e conclusões.

## Etapa 6 — Relatório e apresentação acadêmica

- [ ] 6.1. Criar a estrutura do relatório em LaTeX.
- [ ] 6.2. Redigir a introdução e os objetivos.
- [ ] 6.3. Redigir a fundamentação teórica dos métodos avaliados.
- [ ] 6.4. Redigir a seção de trabalhos relacionados.
- [ ] 6.5. Documentar os datasets e a metodologia experimental.
- [ ] 6.6. Inserir tabelas e gráficos dos resultados.
- [ ] 6.7. Redigir a discussão dos experimentos.
- [ ] 6.8. Redigir a conclusão e os trabalhos futuros.
- [ ] 6.9. Revisar as referências e a formatação.
- [ ] 6.10. Montar os slides da apresentação acadêmica.
- [ ] 6.11. Preparar exemplos visuais para a apresentação.
- [ ] 6.12. Revisar a apresentação e o relatório.
- [ ] 6.13. Finalizar o README com instruções para reproduzir os experimentos.

**Entrega:** relatório acadêmico, apresentação e repositório documentado.

---

## Resumo

| Etapa | Atividade principal | Entrega |
| --- | --- | --- |
| 1. Seleção | Escolher os métodos a avaliar | Lista justificada de métodos e modelos |
| 2. Preparação | Organizar os dados e definir o protocolo | Datasets e métricas |
| 3. Implementação | Implementar e integrar os métodos | Código e scripts funcionais |
| 4. Resultados | Executar os testes e gerar saídas | Dados, gráficos e tabelas |
| 5. Análise | Interpretar e comparar resultados | Discussão e conclusões |
| 6. Documentação | Produzir os materiais acadêmicos | Relatório, slides e README |

## Diretrizes de execução

- **Independência:** nenhum método depende da arquitetura de uma aplicação externa.
- **Comparabilidade:** utilizar os mesmos dados e condições sempre que a tarefa permitir.
- **Rastreabilidade:** guardar versão do método, parâmetros, configurações, identificador da imagem e falhas de execução.
- **Reprodutibilidade:** separar resultados brutos, scripts de geração, gráficos e interpretação.
- **Avaliação de pré-processamento:** transformar as máscaras de referência junto com as imagens; controlar a região avaliada para não atribuir ao método um ganho artificial causado apenas pelo recorte.
- **Seleção por objetivo:** identificar os melhores métodos por precisão, robustez e custo computacional, evitando declarar um vencedor absoluto sem especificar o critério.
