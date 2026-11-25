# Datasets selecionados

**Projeto:** `face-processing-benchmark`  
**Etapa:** 2 — Preparação experimental  
**Status:** seleção definida; aquisição, integridade e preparação ainda pendentes.

## 1. Objetivo deste documento

Registrar as bases de imagens escolhidas, a justificativa de cada escolha e como serão utilizadas nos experimentos de **detecção facial, centralização, recorte e segmentação de pessoas**. O projeto reúne as implementações e avaliações desenvolvidas pela dupla; a avaliação inicial de centralização facial integra este mesmo trabalho.

As três bases têm funções complementares e **não devem ser tratadas como um único conjunto homogêneo**.

## 2. Resumo das escolhas

| Dataset | Volume previsto | Papel no projeto | Dados de referência relevantes |
| --- | ---: | --- | --- |
| **LFW — Labeled Faces in the Wild** | **1.000 imagens selecionadas** (de um conjunto maior) | Avaliar a localização aproximada e a centralização facial em cenários sintéticos de deslocamento, escala e rotação | Fotografias faciais alinhadas; **não** há, no protocolo escolhido, caixas faciais manuais de referência |
| **PPM-100 — Photography Portrait Matting** | **100 imagens** | Desenvolver, depurar e verificar a avaliação de remoção de fundo | Imagens de retratos e máscaras alfa de referência |
| **P3M-500-NP — Privacy-Preserving Portrait Matting, Non-Privacy** | **500 imagens** | Executar a avaliação final de segmentação e estudar o efeito da centralização e do recorte | Retratos sem desfoque de privacidade e máscaras alfa de referência |

> **Regra central:** usar PPM-100 para testes de funcionamento e preparação; reservar P3M-500-NP para resultados experimentais finais. Para a avaliação facial, manter LFW como uma trilha específica de experimentos.

## 3. LFW — Labeled Faces in the Wild

### Características

Base de fotografias faciais coletadas em condições reais, amplamente usada em estudos de reconhecimento facial. O acervo completo contém **13.233 imagens de 5.749 pessoas**. Neste projeto, inicialmente será utilizada uma **amostra reprodutível de 1.000 imagens**, seguindo o protocolo de avaliação já desenvolvido pela dupla.

### Uso no projeto

- Avaliar os detectores **Viola-Jones, HOG + SVM, YuNet e SCRFD** no cenário de imagens artificialmente descentralizadas.
- Aplicar deslocamento, variação de escala e rotação controlados, armazenando os parâmetros e a semente aleatória.
- Medir a presença de detecção, distância do centro detectado ao centro **estimado** da face, taxa de acerto segundo tolerância definida e custo computacional.
- Avaliar as duas estratégias geométricas de centralização: **preenchimento (padding)** e **recorte (cropping)**.

### Limitações

- A LFW padrão não fornece, neste protocolo, caixas de referência faciais precisas para medir IoU de detecção; o centro aproximado da imagem alinhada é usado como proxy da posição da face.
- Portanto, os resultados **não devem ser apresentados como benchmark completo de detecção facial com ground truth manual**.
- O alinhamento e a seleção original das imagens podem introduzir vieses; registrar a origem e a variante da LFW utilizada (por exemplo, `lfw_funneled`).
- Imagens sinteticamente deslocadas não substituem fotografias reais com faces nas bordas e diferentes composições.

### Fonte

- [Página do dataset e documentação de carregamento — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_lfw_people.html)
- [Artigo / documentação original da LFW](https://vis-www.cs.umass.edu/lfw/)

## 4. PPM-100 — Photography Portrait Matting

### Características

Conjunto de **100 fotografias de retratos** com máscaras alfa de referência para estudar a extração de pessoas do fundo, incluindo regiões de contorno delicadas.

### Uso no projeto

- Testar a leitura de imagens e de máscaras alfa, seus tamanhos, formatos e correspondência por identificador.
- Verificar as implementações de **GrabCut, Closed-Form Matting, MODNet e BiRefNet Portrait**.
- Depurar geração automática de máscaras/trimaps auxiliares, métricas, tratamento de erros e transformação geométrica da referência.
- Executar testes pequenos e comparar visualmente resultados para validar o pipeline, **sem considerar esses testes como os resultados finais do artigo**.

### Limitações e cuidados

- O conjunto tem apenas 100 imagens, o que limita a variedade de situações.
- As máscaras alfa representam transparência; comparar saídas contínuas e binárias exige métricas e procedimentos explicitamente definidos.
- Parâmetros técnicos poderão ser definidos durante o desenvolvimento, mas deverão ser **congelados antes da avaliação em P3M-500-NP**.
- Verificar os termos de uso dos arquivos antes de redistribuí-los: o repositório do PPM informa **CC BY-NC-SA 4.0 para as máscaras alfa anotadas**.

### Fonte

- [Repositório oficial — PPM](https://github.com/ZHKKKe/PPM)

## 5. P3M-500-NP — Non-Privacy Portrait Matting

### Características

Subconjunto de avaliação com **500 imagens de retratos sem a ofuscação dos rostos** e máscaras alfa de referência. Faz parte do benchmark P3M, associado à pesquisa *Privacy-Preserving Portrait Matting*. É distinto do conjunto de treinamento P3M com rostos ofuscados.

### Uso no projeto

- Realizar os **experimentos finais de remoção de fundo** com os quatro métodos selecionados.
- Comparar cada método em imagens originais, centralizadas com preenchimento e centralizadas com recorte.
- Medir qualidade de segmentação/alpha matting e desempenho computacional, segundo o protocolo previamente fixado.
- Produzir os resultados por imagem, as tabelas, os gráficos e a discussão acadêmica.

### Limitações e cuidados

- O P3M-500-NP é um conjunto de **avaliação**; não utilizá-lo para escolher limiares, corrigir o algoritmo para imagens específicas ou selecionar hiperparâmetros com base em seus resultados.
- As máscaras alfa não substituem anotações faciais precisas: qualquer estudo de erro absoluto de centralização nesse dataset precisa de referência facial independente ou de um protocolo explicitamente aproximado.
- Registrar a distribuição de resolução, o modo de obtenção e os termos de uso da fonte efetivamente baixada. Confirmar as permissões antes de publicar imagens ou máscaras no repositório.
- Executar cada método sobre as mesmas imagens e, em comparações após recorte, alinhar a máscara de referência às transformações aplicadas; informar também a área preservada.

### Fontes

- [Repositório oficial — P3M-Net](https://github.com/ViTAE-Transformer/P3M-Net)
- [Repositório do projeto P3M](https://github.com/JizhiziLi/P3M)
- [Artigo — Rethinking Portrait Matting with Privacy Preserving](https://doi.org/10.1007/s11263-023-01797-8)

## 6. Separação das avaliações

| Questão experimental | Dataset principal | Observação |
| --- | --- | --- |
| Como os quatro detectores localizam faces deslocadas e rotacionadas? | **LFW** | Referência geométrica aproximada; não é avaliação de caixas faciais anotadas |
| Os algoritmos e scripts de segmentação funcionam e produzem métricas coerentes? | **PPM-100** | Testes de desenvolvimento e validação técnica |
| Qual método de remoção de fundo apresenta melhor resultado nas imagens de retrato? | **P3M-500-NP** | Avaliação final, com parâmetros congelados |
| A centralização e o recorte afetam a segmentação? | **P3M-500-NP** | Comparação pareada por imagem, com as referências transformadas de forma correspondente |
| Quanto custam computacionalmente os métodos? | **LFW** para detecção e **P3M-500-NP** para segmentação | Registrar hardware, versões, resolução, tempo e memória |

## 7. Protocolo de uso e prevenção de vazamento

1. **Não misturar bases** ao calcular uma única média sem identificação e justificativa. Apresentar resultados por dataset e por tarefa.
2. **Manter originais intocados.** Todas as imagens e máscaras derivadas devem ficar em diretórios separados.
3. **Identificar cada amostra.** Registrar `dataset`, `image_id`, caminho da imagem, caminho da anotação e operações aplicadas.
4. **Congelar parâmetros antes do teste final.** Ajustes poderão ocorrer nos testes com PPM-100; não realizar tuning com os resultados do P3M-500-NP.
5. **Padronizar a avaliação.** Mesmas imagens, critérios de pré-processamento e política de falhas para todos os métodos comparados.
6. **Preservar a correspondência geométrica.** Aplicar às máscaras de referência as mesmas transformações feitas nas imagens, sem introduzir informação privilegiada na entrada dos métodos.
7. **Registrar a referência correta.** Na LFW, o alvo facial é aproximado; no PPM-100 e P3M-500-NP, a máscara alfa anotada serve de referência para matting.
8. **Registrar proveniência e licença.** Incluir link da fonte, versão/data de obtenção, termos de uso e checksums quando disponíveis.
9. **Evitar divulgação indevida.** Documentar o procedimento de download em vez de presumir autorização para versionar imagens de pessoas no GitHub.
10. **Fixar a amostragem.** Para a LFW, registrar semente e lista exata das 1.000 imagens selecionadas.

## 8. Organização lógica sugerida

A árvore abaixo descreve a **separação lógica** dos dados. Os nomes definitivos de pastas e os scripts responsáveis devem seguir o documento de estrutura do repositório.

```text
datasets/
├── lfw/
│   ├── raw/
│   └── processed/
├── ppm100/
│   ├── raw/
│   └── processed/
└── p3m500np/
    ├── raw/
    └── processed/
```

- `raw/`: arquivos originais obtidos da fonte, sem alterações.
- `processed/`: imagens, máscaras ou metadados derivados por scripts reproduzíveis.
- Resultados de inferência, métricas, gráficos e tabelas **não** devem ser misturados com os arquivos originais dos datasets; devem ficar na área própria de resultados do projeto.

## 9. Checklist de preparação

- [x] Selecionar LFW para a avaliação inicial de centralização facial.
- [x] Selecionar PPM-100 para testes e validação técnica da segmentação.
- [x] Selecionar P3M-500-NP para os experimentos finais de segmentação.
- [ ] Confirmar as fontes de download e os termos de utilização dos arquivos.
- [ ] Baixar as três bases e preservar os arquivos originais.
- [ ] Conferir a quantidade de imagens e a integridade das anotações.
- [ ] Criar e salvar a amostra fixa de 1.000 imagens LFW.
- [ ] Implementar verificação automática da correspondência imagem–máscara.
- [ ] Documentar resolução, formato, problemas e exclusões identificados.
- [ ] Congelar as configurações antes da avaliação final em P3M-500-NP.

---

**Decisão do projeto:** LFW para a trilha experimental de centralização; PPM-100 para testes técnicos; P3M-500-NP para os resultados científicos finais de segmentação e dos efeitos de centralização/recorte. A avaliação de centralização já desenvolvida pela dupla será aproveitada e expandida dentro desta pesquisa.
