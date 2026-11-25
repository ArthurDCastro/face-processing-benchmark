# Protocolo experimental

Este documento define os cenários, parâmetros, saídas e visualizações planejados para o projeto **face-processing-benchmark**. O estudo é organizado em três experimentos: **E1 — centralização facial**, **E2 — remoção de fundo** e **E3 — influência da centralização e do recorte na remoção de fundo**.

> **Status:** protocolo inicial. Parâmetros sujeitos a ajustes técnicos durante os testes preliminares, antes de executar a avaliação final em P3M-500-NP. Todo ajuste deverá ser registrado e versionado.

As definições matemáticas das métricas ficam em [`METRICAS_AVALIACAO.md`](METRICAS_AVALIACAO.md); este documento trata de **como executar**, **quais resultados guardar** e **quais gráficos e tabelas produzir**.

## 1. Visão geral

| Experimento | Objetivo | Métodos | Dataset | Saída principal |
|---|---|---|---|---|
| **E1 — Centralização facial** | Verificar qual detector conduz à centralização mais precisa e eficiente | Viola-Jones, HOG + SVM, YuNet e SCRFD | LFW (amostra inicial de 1.000 imagens) | Erros de centralização, sucesso e custo computacional |
| **E2 — Remoção de fundo** | Comparar qualidade e desempenho dos métodos nas imagens originais | GrabCut, Closed-Form Matting, MODNet e BiRefNet Portrait | PPM-100 (testes), P3M-500-NP (avaliação final) | Métricas binárias, alfa e custo computacional |
| **E3 — Efeito do pré-processamento** | Verificar se a centralização e o recorte alteram a qualidade e o desempenho da remoção de fundo | Os quatro métodos de E2, sob três condições de entrada | P3M-500-NP | Diferenças pareadas em relação à imagem original |

**Princípios comuns:** usar as mesmas amostras para concorrentes diretos; nunca ajustar os métodos olhando os resultados finais; preservar dados originais; registrar falhas; guardar resultados por imagem, não apenas médias; fixar versões, parâmetros e sementes.

## 2. E1 — Centralização facial

### 2.1 Objetivo e métodos

Avaliar o resultado **final da centralização do rosto**, e não apenas a detecção de face. Comparar **Viola-Jones**, **HOG + SVM**, **YuNet** e **SCRFD** aplicados à mesma estratégia geométrica. A taxa de detecção é uma medida diagnóstica complementar.

**Dataset:** LFW. Selecionar inicialmente 1.000 fotografias com semente fixa; registrar os identificadores das imagens amostradas. Como a LFW usual não oferece caixas faciais de referência precisas, a localização do rosto usada neste protocolo é **aproximada**. Não apresentar essas medições como avaliação padrão de precisão de detecção por bounding boxes.

### 2.2 Cenários

| ID | Variação | Configuração proposta | Objetivo |
|---|---|---|---|
| **E1-S1** | Posição | Centro e deslocamentos aleatórios com posições registradas | Sensibilidade ao deslocamento |
| **E1-S2** | Inclinação | 0°, −15°, +15°, −30° e +30° | Sensibilidade à rotação |
| **E1-S3** | Escala | 70%, 100% e 130% | Sensibilidade ao tamanho aparente |
| **E1-S4** | Condições combinadas | Posição, inclinação e escala sorteadas | Robustez sob variações simultâneas |

Gerar **uma única versão transformada de cada fotografia por combinação definida** e reutilizar exatamente a mesma entrada para os quatro métodos. Evitar o produto cartesiano completo de todos os cenários sem justificativa; registrar quantas amostras cada cenário contém.

### 2.3 Parâmetros iniciais

| Parâmetro | Valor ou regra |
|---|---|
| Amostra inicial | 1.000 imagens LFW |
| Tela sintética | 500 × 500 px |
| Posição-alvo | Centro geométrico (50%, 50%) |
| Semente | 42 |
| Limiar histórico de sucesso | Erro de centralização ≤ 15 px, **válido para a tela de 500 × 500** |
| Comparação entre resoluções | Usar também erro de centralização normalizado |
| Faces múltiplas | Selecionar a maior face detectada; registrar ocorrências e eventuais falhas |
| Estratégia geométrica na comparação dos detectores | **A mesma para os quatro métodos**; começar pela centralização por recorte, mantendo parâmetros idênticos |
| Falha de detecção ou recorte inválido | Registrar como falha; contabilizar como insucesso na taxa geral |

**Referência e medição:** transformar a posição de referência juntamente com a imagem sintética e medir sua distância até a posição-alvo **após a operação de centralização**. Não calcular o erro apenas pelo centro previsto pelo próprio detector, pois isso favoreceria artificialmente qualquer método que centralize sua própria previsão.

**Limitação geométrica:** um rosto próximo da borda pode impossibilitar o recorte desejado, sobretudo com restrições de proporção ou escala. Registrar separadamente `detection_failure`, `crop_failure` e `centering_error`.

### 2.4 Resultados a armazenar

Uma linha por **imagem × cenário × detector**. Campos mínimos sugeridos:

`image_id`, `scenario_id`, `detector`, `seed`, `rotation_deg`, `scale`, `offset_x`, `offset_y`, `detected`, `crop_valid`, `error_px`, `error_normalized`, `success_15px`, `retained_area_ratio`, `inference_ms`, `total_ms`, `peak_ram_mb`, `status`, `error_reason`.

### 2.5 Tabelas a gerar

| ID | Tabela | Linhas / colunas |
|---|---|---|
| **T1.1** | Resumo geral por detector | Detector; imagens; falhas; taxa de sucesso; erro médio/mediano normalizado; tempo mediano; RAM de pico |
| **T1.2** | Desempenho por cenário | Cenário × detector; taxa de sucesso; erro mediano; taxa de detecção |
| **T1.3** | Desempenho por rotação e escala | Rotação/escala × detector; sucesso e erro, incluindo tamanho da amostra |
| **T1.4** | Validade e preservação do recorte | Detector; recortes inválidos; área média preservada |

### 2.6 Gráficos a gerar

| ID | Gráfico | Eixos / finalidade |
|---|---|---|
| **G1.1** | Boxplot ou violino do erro normalizado | X: detector; Y: erro normalizado; mostrar dispersão e outliers |
| **G1.2** | Barras de sucesso por cenário | X: cenário; Y: % de sucesso; agrupamento por detector |
| **G1.3** | Curvas de sensibilidade à rotação | X: ângulo; Y: erro mediano ou % de sucesso; uma série por detector |
| **G1.4** | Curvas de sensibilidade à escala | X: escala; Y: erro mediano ou % de sucesso; uma série por detector |
| **G1.5** | Qualidade × tempo | X: tempo mediano; Y: taxa de sucesso; um ponto por detector |
| **G1.6** | Prancha visual de centralização | Para as mesmas imagens: entrada, saídas dos quatro detectores, posição-alvo e referência |

**Regra para gráficos de erro:** indicar se os erros incluem apenas sucessos de detecção; sempre apresentar ao lado a taxa de falhas, para evitar conclusões enviesadas por descarte dos casos difíceis.

## 3. E2 — Remoção de fundo em imagens originais

### 3.1 Objetivo e métodos

Comparar **GrabCut**, **Closed-Form Matting**, **MODNet** e **BiRefNet Portrait** sem centralização ou recorte prévios.

- **PPM-100:** testes funcionais, revisão de interfaces, verificação dos formatos de saída e ajustes técnicos permitidos.
- **P3M-500-NP:** conjunto reservado à avaliação científica final (500 imagens). Não escolher hiperparâmetros a partir de seu desempenho final.

### 3.2 Cenários e parâmetros iniciais

| Item | Definição |
|---|---|
| **E2-S1 — Qualidade** | Uma inferência por imagem e método, utilizando a imagem original |
| **E2-S2 — Desempenho** | Cinco execuções por configuração, após aquecimento, em ambiente controlado |
| Saída alfa | Padronizar valores numéricos para [0, 1], preservando saídas contínuas |
| Saída binária | Limiar de 0,5, fixo para todos os métodos |
| Resolução | Usar original se o método suportar; registrar redimensionamento interno e reamostragem da saída |
| GrabCut | Inicialização automática, determinística e sem acesso à máscara de referência |
| Closed-Form Matting | Trimap automática, determinística e sem acesso à máscara de referência |
| Modelos de IA | Checkpoints pré-treinados identificados, sem fine-tuning no dataset final |
| Tempo de execução | Separar carregamento do modelo, preparação, inferência, pós-processamento e tempo total |

**Comparabilidade:** GrabCut fornece essencialmente uma máscara binária, enquanto métodos de matting produzem ou estimam saídas contínuas. Reportar **IoU, Dice e Boundary F1** para todos após binarização padronizada. Reportar **SAD e MSE** das saídas alfa, identificando explicitamente quando uma máscara binária foi tratada como alfa 0/1. Verificar a semântica efetiva da saída do checkpoint BiRefNet, pois mapa de probabilidade e alfa de matting não são automaticamente equivalentes.

**Custo completo:** incluir a inicialização do GrabCut e a geração da trimap no tempo e na memória da solução clássica correspondente.

### 3.3 Resultados a armazenar

Uma linha por **imagem × método**, mais um arquivo de repetições para desempenho. Campos mínimos:

`image_id`, `method`, `dataset`, `image_width`, `image_height`, `internal_width`, `internal_height`, `iou`, `dice`, `boundary_f1`, `sad`, `mse`, `preprocess_ms`, `inference_ms`, `postprocess_ms`, `total_ms`, `peak_ram_mb`, `peak_vram_mb`, `status`, `error_reason`, `checkpoint_id`, `config_hash`.

### 3.4 Tabelas a gerar

| ID | Tabela | Linhas / colunas |
|---|---|---|
| **T2.1** | Qualidade geral por método | Método; imagens válidas/falhas; IoU, Dice, Boundary F1, SAD, MSE (média, mediana e dispersão) |
| **T2.2** | Desempenho computacional | Método; tempo mediano total; etapas; RAM/VRAM de pico; tamanho do checkpoint quando aplicável |
| **T2.3** | Qualidade por características das imagens | Método × faixas de resolução / proporção / complexidade do fundo, se essas categorias forem definidas de modo reproduzível |
| **T2.4** | Falhas e cobertura | Método; número/tipo de falhas; imagens avaliadas; tratamento adotado |

### 3.5 Gráficos a gerar

| ID | Gráfico | Eixos / finalidade |
|---|---|---|
| **G2.1** | Boxplot de IoU por método | X: método; Y: IoU por imagem |
| **G2.2** | Boxplot de Boundary F1 por método | X: método; Y: Boundary F1 por imagem |
| **G2.3** | Comparativo de SAD e MSE | Gráficos separados ou painéis claramente rotulados; menor é melhor |
| **G2.4** | Distribuição do tempo total | X: método; Y: tempo por imagem, com dispersão |
| **G2.5** | Qualidade × custo | X: tempo ou memória; Y: IoU ou Boundary F1; pontos por método |
| **G2.6** | Pranchas visuais | Mesma imagem; original, referência alfa e saída dos quatro métodos; incluir cabelos, bordas e casos de falha |

**Regra de resolução:** não comparar SAD bruto de imagens com quantidades diferentes de pixels como se fossem equivalentes; indicar convenção, tamanho da máscara e, quando necessário, um erro médio por pixel complementar.

## 4. E3 — Influência da centralização e do recorte na remoção de fundo

### 4.1 Objetivo e configuração

Determinar se **centralizar e/ou recortar** uma imagem altera a qualidade e o custo da remoção de fundo. Utilizar **as mesmas 500 imagens P3M-500-NP** e os mesmos quatro métodos de E2.

O detector usado para preparar as entradas será **um único método fixo**, escolhido com base no resultado do E1 **sem consultar o desempenho final de segmentação do P3M-500-NP**. Registrar a versão, os parâmetros e os casos em que falhar. Essa escolha evita acrescentar quatro detectores como nova variável fatorial.

### 4.2 Condições

| Código | Condição | Transformação | Observação |
|---|---|---|---|
| **C0** | Original | Nenhuma | Baseline; pode reutilizar as saídas de E2 |
| **C1** | Centralizada, sem recorte deliberado | Translação + preenchimento nas áreas descobertas | A saída pode perder conteúdo nas bordas se mantiver tamanho fixo; medir separadamente |
| **C2** | Centralizada e recortada | Seleção da maior região válida na proporção definida | Sem preenchimento; registrar redução de área e resolução |

**Parâmetros:** alvo no centro geométrico; manter a proporção de origem para C2, salvo decisão documentada; usar regras fixas de preenchimento e recorte para todas as imagens. Aumentar a tela ou reduzir a imagem para preservar integralmente o conteúdo seria **outra estratégia** e não deve ser misturada a C1 sem ser declarada.

### 4.3 Volume e reaproveitamento

- Matriz: **500 imagens × 3 condições × 4 métodos = 6.000 combinações**.
- **2.000 combinações C0** são equivalentes às de E2, se os parâmetros e versões coincidirem; reutilizar os resultados para evitar trabalho duplicado.
- Portanto, são **4.000 processamentos adicionais de segmentação** para C1 e C2, antes de repetições de desempenho e eventuais falhas.

### 4.4 Controle da validade das comparações

1. Gerar e salvar as transformações geométricas de cada imagem (`transform_id`, matriz, origem, dimensões, área mantida).
2. Aplicar a **mesma transformação geométrica** às máscaras de referência, usando interpolação apropriada para alfa.
3. Identificar **regiões com pixels originais válidos** e **regiões artificiais** para que o padding não contamine a medida principal.
4. Para comparar C0, C1 e C2 em qualidade, calcular métricas também em uma **região comum correspondente** da imagem de origem. Isso evita atribuir ao recorte uma melhoria causada apenas pela exclusão de áreas difíceis.
5. Relatar separadamente o desempenho na saída completa de cada condição (representa o uso real) e na região comum (comparação pareada de qualidade).
6. Registrar imagens em que o detector falha ou a transformação não é viável; não remover casos silenciosamente.
7. Tratar custo computacional de forma explícita: distinguir **tempo só da segmentação** e **tempo completo de centralização + segmentação**. Comparar resolução e quantidade de pixels processados.

### 4.5 Resultados a armazenar

Uma linha por **imagem × método × condição**. Campos mínimos:

`image_id`, `method`, `condition`, `detector_used`, `transform_id`, `source_pixels_retained_ratio`, `artificial_pixels_ratio`, `output_width`, `output_height`, `valid_region_pixels`, `iou_full`, `iou_common`, `dice_full`, `dice_common`, `boundary_f1_full`, `boundary_f1_common`, `sad_common`, `mse_common`, `segmentation_ms`, `preprocessing_ms`, `pipeline_ms`, `peak_ram_mb`, `status`, `error_reason`.

### 4.6 Tabelas a gerar

| ID | Tabela | Linhas / colunas |
|---|---|---|
| **T3.1** | Qualidade por método e condição | Método × C0/C1/C2; IoU, Dice, Boundary F1 na região comum |
| **T3.2** | Mudança de qualidade em relação à original | Método × C1−C0 e C2−C0; diferença média/mediana, IC 95%, imagens que melhoraram/pioraram |
| **T3.3** | Desempenho por condição | Método × condição; tempo de segmentação, tempo do pipeline, RAM/VRAM |
| **T3.4** | Efeitos geométricos | Condição; área preservada, pixels artificiais, resoluções e falhas |
| **T3.5** | Resultado nas saídas completas | Método × condição; qualidade calculada sobre a saída de cada cenário, com ressalva sobre domínios de pixels distintos |

### 4.7 Gráficos a gerar

| ID | Gráfico | Eixos / finalidade |
|---|---|---|
| **G3.1** | Barras ou pontos de IoU por condição | X: C0/C1/C2; Y: IoU na região comum; séries por método |
| **G3.2** | Distribuição das diferenças pareadas | X: método; Y: ΔIoU = condição − C0; separar C1 e C2 |
| **G3.3** | Diferenças de Boundary F1 | X: método; Y: ΔBoundary F1; mostrar IC 95% |
| **G3.4** | Variação de SAD/MSE | Comparar ΔSAD e ΔMSE, indicando que redução representa melhoria |
| **G3.5** | Tempo por condição | X: C0/C1/C2; Y: tempo de segmentação **e**, separadamente, tempo total do pipeline |
| **G3.6** | Qualidade × área preservada | X: fração de área preservada; Y: ΔIoU/ΔBoundary F1; verificar dependência do tamanho do recorte |
| **G3.7** | Pranchas antes/depois | Para a mesma fotografia: C0, C1, C2, máscaras geradas e referência transformada |

A diferença pareada é calculada sobre **a mesma imagem e o mesmo método**. Para métricas maiores-melhores: `Δ = métrica(C1 ou C2) − métrica(C0)`. Para SAD e MSE, Δ negativo indica melhoria. Relatar intervalos de confiança e métodos estatísticos especificados antes de examinar as conclusões finais.

## 5. Regras gerais de medição e reprodutibilidade

- **Semente:** 42 como valor inicial; salvar sempre a lista de arquivos selecionados e os parâmetros sorteados.
- **Ambiente:** registrar sistema operacional, CPU, GPU, RAM, versões Python/OpenCV/PyTorch e versões dos modelos.
- **Hardware:** não comparar tempos obtidos em máquinas diferentes sem identificar essa diferença.
- **Aquecimento:** fazer execuções de aquecimento antes das cinco repetições previstas para tempo; sincronizar GPU antes/depois da medição quando necessário.
- **Tempo:** salvar medições individuais, mediana e variabilidade; não confundir carga inicial de modelo com inferência por imagem.
- **Memória:** registrar pico de RAM e VRAM quando aplicável, especificando ferramenta e escopo de medição.
- **Falhas:** salvar status e motivo por amostra; incluir denominadores nas taxas e tabelas.
- **Configurações:** salvar arquivos YAML/JSON usados em cada execução e hash ou identificador da configuração.
- **Dados originais:** nunca sobrescrever arquivos em `datasets/*/raw/`.
- **Parâmetros de métodos:** congelar antes da avaliação final em P3M-500-NP; ajustes motivados pelos resultados finais são exploratórios e devem ser identificados como tal.
- **Visualizações:** sempre usar os mesmos exemplos nas pranchas comparativas e documentar critérios de escolha dos casos (típicos, melhores, piores e falhas).

## 6. Organização recomendada das saídas

```text
results/
├── e1_centering/
│   └── <run_id>/
│       ├── config.json
│       ├── per_image.csv
│       ├── summary.csv
│       ├── tables/
│       ├── figures/
│       └── logs/
├── e2_background_removal/
│   └── <run_id>/
│       ├── config.json
│       ├── per_image.csv
│       ├── timing_repeats.csv
│       ├── summary.csv
│       ├── tables/
│       ├── figures/
│       └── logs/
└── e3_preprocessing_effect/
    └── <run_id>/
        ├── config.json
        ├── transformations.csv
        ├── per_image_condition.csv
        ├── paired_differences.csv
        ├── timing_repeats.csv
        ├── tables/
        ├── figures/
        └── logs/
```

`<run_id>` identifica cada execução de forma única. Os nomes de imagens e máscaras geradas devem incluir `image_id`, método e condição para impedir substituições acidentais.

## 7. Lista de entregáveis visuais

**Obrigatórios para o relatório:** T1.1, T1.2, G1.1, G1.2, G1.6; T2.1, T2.2, G2.1, G2.2, G2.4, G2.6; T3.1, T3.2, T3.3, G3.1, G3.2, G3.5, G3.7.

**Complementares:** os demais gráficos e tabelas descritos nas seções de cada experimento. Eles devem ser gerados pelos scripts, mas sua inclusão no relatório dependerá da relevância dos resultados e do espaço disponível.

**Não gerar resultados fictícios:** scripts podem criar diretórios e cabeçalhos vazios, mas só devem produzir tabelas e gráficos quantitativos após executar os métodos e calcular as métricas reais.

## 8. Pendências antes de congelar o protocolo

- [ ] Confirmar a política de redimensionamento interno e restauração das saídas por método.
- [ ] Definir os detalhes determinísticos de inicialização de GrabCut e geração de trimap.
- [ ] Fixar o procedimento de referência de centro facial aproximado para LFW.
- [ ] Definir tolerância do Boundary F1 e convenções de SAD/MSE (incluindo normalização e domínio válido).
- [ ] Definir o preenchimento de C1, a regra exata do recorte C2 e o tratamento dos casos inviáveis.
- [ ] Definir como a região comum será mapeada e avaliada nos três cenários de E3.
- [ ] Confirmar ambiente de execução, checkpoints e hashes de configuração.
- [ ] Realizar testes preliminares sem usar as métricas finais do P3M-500-NP para ajustar métodos.

Após resolver essas pendências, versionar uma configuração de referência e utilizá-la sem alterações na execução final.
