# Especificação para o Codex — Configurações experimentais

Este documento orienta o **Codex a criar os arquivos de configuração** do repositório `face-processing-benchmark`. **Este documento não é um arquivo de configuração**: os arquivos YAML deverão ser gerados pelo Codex no repositório, respeitando os documentos científicos já aprovados.

## 1. Objetivo e fontes de verdade

Centralizar parâmetros de datasets, métodos e experimentos, evitando valores fixos no código e garantindo reprodutibilidade. Antes de criar arquivos, o Codex deve consultar, nesta ordem, os documentos que existirem no repositório:

1. `docs/PROTOCOLO_EXPERIMENTAL.md`: cenários, condições, volume e resultados esperados.
2. `docs/METRICAS_AVALIACAO.md`: definições, fórmulas e interpretação das métricas.
3. `docs/METODOS_SELECIONADOS.md`: lista final e adaptações de comparabilidade.
4. `docs/DATASETS_SELECIONADOS.md` e `docs/DOWNLOAD_DATASETS.md`: finalidade e organização dos datasets.
5. `docs/ESTRUTURA_REPOSITORIO.md`: convenções da arquitetura.

Se algum documento estiver na raiz, utilizar seu caminho real. Em caso de divergência, **não inventar um valor**; registrar a incompatibilidade e manter a configuração pendente.

## 2. Arquivos a serem criados pelo Codex

```text
configs/
├── common.yaml
├── datasets.yaml
├── methods.yaml
└── experiments/
    ├── e1_centering.yaml
    ├── e2_background_removal.yaml
    └── e3_preprocessing_effect.yaml
```

| Arquivo                        | Responsabilidade                                                                                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `common.yaml`                  | Semente, hardware/dispositivo configurável, logging, repetições, saída de resultados e políticas compartilhadas                       |
| `datasets.yaml`                | Cadastro de LFW, PPM-100 e P3M-500-NP, caminhos relativos, manifestos, finalidade e quantidade esperada                               |
| `methods.yaml`                 | Cadastro dos oito métodos, identificadores estáveis, implementação, checkpoint e parâmetros próprios                                  |
| `e1_centering.yaml`            | Centralização facial na LFW: quatro detectores, cenários e critérios de avaliação                                                     |
| `e2_background_removal.yaml`   | Remoção de fundo em imagens **originais**: quatro métodos, testes com PPM-100 e avaliação final com P3M-500-NP                        |
| `e3_preprocessing_effect.yaml` | Comparação pareada entre C0 (original), C1 (centralizada com padding) e C2 (centralizada por recorte), usando os quatro segmentadores |

Não gerar arquivos duplicados para parâmetros que já estejam definidos em `common.yaml` ou `methods.yaml`. Cada experimento deve referenciar métodos e datasets por seus IDs, não copiar suas configurações.

## 3. Conteúdo obrigatório

### 3.1 Configurações comuns

- Semente aleatória inicial: `42`, explicitamente declarada.
- Caminhos de datasets, checkpoints e saídas **relativos à raiz do repositório**, não ao diretório corrente do terminal; não utilizar caminhos locais absolutos ou exemplos como `/caminho/datasets`.
- Diretório de saída por experimento e execução (`run_id`), com metadados da configuração efetiva.
- Registro de falhas por imagem, sem omissões silenciosas.
- Execução em CPU/GPU configurável, sem presumir que haja GPU.
- Cinco repetições de medição de desempenho após aquecimento, conforme protocolo; registrar também tempos individuais e custo das etapas auxiliares.
- Arquivos de resultados por amostra em formato estruturado (CSV/JSON), conforme protocolo.

### 3.2 Datasets

- `lfw`: 1.000 imagens inicialmente, para E1; posicionamento sintético e referência facial **aproximada**.
- `ppm100`: 100 imagens com máscaras, para testes técnicos e validação de E2 e E3.
- `p3m500np`: 500 imagens com máscaras, reservadas para **avaliação final** de E2 e E3.
- Usar a estrutura realmente criada por `prepare_datasets.py` e `validate_datasets.py`, inclusive os manifestos em `processed/`; não mover nem modificar `raw/`.
- O Codex deve conferir os nomes reais das pastas/colunas do manifesto antes de fixar caminhos ou chaves YAML.

### 3.3 Métodos

Cadastrar exatamente os oito métodos principais:

| Objetivo                  | Métodos                      |
| ------------------------- | ---------------------------- |
| Centralização — clássicos | Viola-Jones; HOG + SVM       |
| Centralização — IA        | YuNet; SCRFD                 |
| Remoção — clássicos       | GrabCut; Closed-Form Matting |
| Remoção — IA              | MODNet; BiRefNet Portrait    |

- Diferenciar IDs estáveis, nomes de apresentação, tipo, implementação e parâmetros.
- Caminho/versão de checkpoint deve ser explicitamente configurável para métodos com pesos.
- GrabCut deve ter **inicialização automática**; Closed-Form Matting deve ter **trimap automática**, ambas sem acesso à máscara de referência na inferência.
- Não criar checkpoints fictícios nem declarar um método como implementado só por existir no cadastro.
- Registrar a semântica da saída (binária, máscara contínua, alfa) e qualquer conversão necessária para avaliação.

### 3.4 E1 — Centralização facial

- Usar LFW e quatro detectores.
- Cenários: deslocamento; rotação (0°, ±15°, ±30°); escala (70%, 100%, 130%); condições combinadas.
- Imagens sintéticas de 500 × 500 pixels, posição-alvo no centro e semente fixa.
- Critério histórico de acerto: até 15 px; também registrar erro normalizado.
- Priorizar métricas **após a centralização**, não somente a qualidade da caixa detectada.
- Registrar detecção ausente, recorte inválido, erro, dimensões e área preservada.
- **Não gerar produto cartesiano de todas as variações por padrão**: o número de amostras por cenário deve seguir o protocolo, ou ficar pendente quando ainda não definido.

### 3.5 E2 — Remoção de fundo

- Executar os quatro segmentadores sobre **imagens originais**, sem centralização ou recorte.
- Separar modo de testes (`ppm100`) e avaliação final (`p3m500np`); nunca ajustar parâmetros usando resultados finais.
- Registrar IoU, Dice, Boundary F1 e, quando aplicável, SAD/MSE e métricas complementares definidas no documento de métricas.
- Máscaras normalizadas em [0,1] e limiar de binarização inicial de 0,5.
- Registrar resolução original, resolução interna do modelo, redimensionamento, tempo, memória e falhas.

### 3.6 E3 — Influência da centralização e do recorte

- Dataset final: P3M-500-NP, quatro segmentadores e três condições:
  - **C0:** original.
  - **C1:** centralização com preenchimento.
  - **C2:** centralização por recorte.
- Fixar um único detector de centralização, **escolhido com base em E1**, sem escolher o vencedor usando P3M-500-NP. Até a escolha, usar `null`/pendência explícita.
- Aplicar à referência as transformações geométricas correspondentes às imagens, preservando o controle de pixels originais versus artificiais.
- Comparar as mesmas regiões originais correspondentes em C0/C1/C2 e registrar também métricas na saída inteira como análise secundária.
- Comparar qualidade, tempo da segmentação, tempo do pipeline e memória.
- Prever até 6.000 processamentos de segmentação (500 imagens × 3 condições × 4 métodos), com possibilidade de **reutilizar C0 de E2** apenas quando entradas, versões, configurações e checkpoints forem idênticos.

## 4. Resultados e visualizações

Nos YAMLs, registrar **somente os identificadores** das tabelas e gráficos solicitados no `PROTOCOLO_EXPERIMENTAL.md`, sem implementar a geração nem criar dados. Preservar a nomenclatura `T1.1` a `T1.4`, `G1.1` a `G1.6`, `T2.1` a `T2.4`, `G2.1` a `G2.6`, `T3.1` a `T3.5` e `G3.1` a `G3.7`, conforme a descrição oficial de cada artefato.

## 5. Parâmetros ainda indefinidos

Não escolher arbitrariamente os seguintes valores: variante/checkpoint e hash de SCRFD, MODNet e BiRefNet; caminhos de modelos ausentes; inicialização de GrabCut; geração da trimap; tolerância do Boundary F1; amostras exatas por cenário; método de intervalos de confiança; tamanho de lote/resolução interna específica de cada modelo; detector do E3.

Para valores que impeçam executar determinada tarefa, usar `null` (ou equivalente) **com comentário `TODO` explicativo** e prever validação clara no carregador. Não usar números fictícios ou valores silenciosos de fallback. É permitido criar campos e convenções, desde que documentados.

## 6. Regras de implementação

1. Produzir YAML válido, legível e comentado, com chaves e comentários em inglês; a documentação explicativa pode permanecer em português.
2. Usar nomes e IDs consistentes entre arquivos; evitar redefinições contraditórias.
3. Manter os arquivos versionáveis no Git, sem segredos ou diretórios pessoais.
4. Conferir a sintaxe de todos os YAMLs por parser e verificar referências cruzadas entre métodos/datasets/experimentos.
5. Quando houver carregador de configuração existente no projeto, respeitá-lo; caso não haja, **não implementar o pipeline científico nesta tarefa**. No máximo, adicionar uma verificação leve de esquema/referências ou documentar validações pendentes.
6. Não baixar datasets ou checkpoints, não executar modelos nem gerar resultados científicos nesta tarefa.
7. Não sobrescrever configurações existentes sem comparar as diferenças e preservar escolhas já confirmadas.

## 7. Critérios de aceite para o Codex

- [ ] Os seis YAMLs foram criados nos caminhos previstos.
- [ ] Os YAMLs refletem os três experimentos e os oito métodos, sem adicionar métodos.
- [ ] Todos os datasets usam caminhos relativos compatíveis com o repositório.
- [ ] Nenhuma máscara de referência é utilizada como entrada para gerar a previsão.
- [ ] As configurações distinguem testes técnicos de avaliação final.
- [ ] Os parâmetros pendentes estão identificados e não receberam valores inventados.
- [ ] Os seis YAMLs são sintaticamente válidos e as referências cruzadas são coerentes.
- [ ] Nenhum algoritmo, dataset, checkpoint ou resultado foi criado artificialmente.
