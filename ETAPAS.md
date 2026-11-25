# Etapas do projeto — Face Processing Benchmark

## Objetivo

Desenvolver uma avaliação experimental independente de métodos clássicos e modelos de aprendizado profundo para **detecção facial, centralização e recorte de imagens e segmentação de pessoas (remoção de fundo)**. O projeto busca comparar qualidade, robustez e custo computacional, além de investigar como a centralização e o recorte influenciam os resultados da segmentação.

> **Escopo:** pesquisa independente, sem depender de uma aplicação específica. A escolha dos métodos será baseada em critérios científicos, disponibilidade e viabilidade experimental.

## Etapa 1 — Seleção de métodos e modelos

- [x] 1.1. Listar os métodos clássicos de detecção facial candidatos.
- [x] 1.2. Listar os modelos de aprendizado profundo para detecção facial candidatos.
- [x] 1.3. Selecionar os métodos de centralização e recorte a comparar.
- [x] 1.4. Listar os métodos clássicos de segmentação de pessoas candidatos.
- [x] 1.5. Listar os modelos de aprendizado profundo para segmentação de pessoas candidatos.
- [x] 1.6. Localizar os artigos científicos e repositórios de cada candidato.
- [ ] 1.7. Verificar disponibilidade de código, pesos, dependências e licenças.
- [x] 1.8. Montar uma tabela com candidatos, características e referências.
- [x] 1.9. Definir e justificar os oito métodos principais. A escolha das variantes e dos pesos segue no item 1.7.

**Entrega:** [métodos selecionados, referências e justificativas](docs/METODOS_SELECIONADOS.md).

## Etapa 2 — Preparação dos dados e do protocolo experimental

- [x] 2.1. Pesquisar datasets públicos para avaliação de detecção facial.
- [x] 2.2. Pesquisar datasets públicos de retratos com máscaras de segmentação.
- [x] 2.3. Selecionar LFW funneled, PPM-100 e P3M-500-NP.
- [ ] 2.3.1. Confirmar os termos de uso e as permissões de redistribuição.
- [x] 2.4. Organizar as imagens e anotações locais e gerar os três manifestos.
- [x] 2.5. Criar o validador. Os relatórios locais registram 13.233 imagens LFW, 100 pares PPM-100 e 500 pares P3M-500-NP válidos.
- [x] 2.6. Documentar as métricas de avaliação de cada tarefa.
- [x] 2.7. Documentar os cenários e o protocolo inicial de E1, E2 e E3.
- [x] 2.8. Criar os seis YAMLs experimentais e registrar decisões em aberto com `null` e `TODO`.
- [x] 2.9. Gerar listas técnicas de 20 imagens LFW e 20 pares PPM-100 com semente 42.
- [ ] 2.10. Fixar a seleção de 1.000 imagens LFW do E1 e registrar os IDs amostrados.
- [ ] 2.11. Resolver os parâmetros em aberto do protocolo e congelar a configuração antes da avaliação final. O detector do E3 será escolhido após E1.
- [x] 2.12. Adequar o `.gitignore` ao layout por dataset.
- [ ] 2.13. Confirmar quais metadados podem ser versionados.

**Entrega:** datasets organizados, métricas documentadas e protocolo inicial configurado.
[Preparação dos dados](docs/DOWNLOAD_DATASETS.md) · [Métricas](docs/METRICAS_AVALIACAO.md) ·
[Protocolo experimental](docs/PROTOCOLO_EXPERIMENTAL.md) ·
[Configurações](docs/CONFIGURACAO_EXPERIMENTOS.md)

## Etapa 3 — Implementação dos métodos

- [x] 3.1. Criar o repositório e configurar o ambiente Python.
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
- [ ] 3.14. Atualizar o carregador para o esquema experimental v2 e adaptar os testes atuais do esquema v1.

**Entrega:** métodos funcionais, testes básicos e scripts independentes e reproduzíveis.

## Etapa 4 — Execução e geração dos resultados

- [ ] 4.1. Executar o E1 na LFW e registrar os diagnósticos de detecção.
- [ ] 4.2. Consolidar as métricas pós-centralização do E1 e escolher o detector fixo do E3.
- [ ] 4.3. Validar tecnicamente E2 e E3 com PPM-100 e congelar os parâmetros da avaliação final.
- [ ] 4.4. Executar E2 com os quatro métodos nas imagens originais do P3M-500-NP.
- [ ] 4.5. Executar E3 nas mesmas imagens do P3M-500-NP, com comparação pareada de C0, C1 e C2.
- [ ] 4.6. Coletar as medições de desempenho previstas em E1, E2 e E3.
- [ ] 4.7. Verificar a elegibilidade para reutilizar C0 de E2 em E3.
- [ ] 4.8. Consolidar e validar os resultados obtidos, registrando falhas e configurações.
- [ ] 4.9. Gerar as estatísticas, tabelas e gráficos comparativos.
- [ ] 4.10. Selecionar e organizar exemplos visuais dos resultados.

**Entrega:** arquivos de resultados brutos, estatísticas, gráficos, tabelas e exemplos visuais.

## Etapa 5 — Análise e discussão dos resultados

- [ ] 5.1. Comparar a precisão da centralização e o custo computacional dos detectores em E1.
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
