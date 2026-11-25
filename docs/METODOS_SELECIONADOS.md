# Métodos selecionados — Face Processing Benchmark

**Status:** seleção preliminar concluída (Etapa 1).  
**Escopo:** estudo científico independente sobre detecção facial, centralização e recorte, segmentação de primeiro plano e *image matting*.

Este documento descreve os **oito métodos principais** (dois por categoria), suas características, suas diferenças em relação ao concorrente direto e as referências científicas. A escolha dos métodos **não representa um resultado experimental** nem pressupõe qual será o melhor.

## 1. Detecção facial — métodos clássicos

### 1.1 Viola–Jones (Haar Cascade)

- **Tipo:** detecção clássica baseada em características retangulares do tipo Haar, AdaBoost e uma cascata de classificadores.
- **Funcionamento:** percorre janelas da imagem, descartando rapidamente regiões improváveis e aprofundando a avaliação de candidatas a rosto.
- **Interesse no estudo:** linha de base clássica estabelecida, com implementação amplamente disponível no OpenCV.
- **Limitações a testar:** sensibilidade a rotação, poses fora do frontal e condições diferentes das usadas no treinamento da cascata.
- **Artigo:** Viola, P.; Jones, M. (2001). *Rapid Object Detection Using a Boosted Cascade of Simple Features*.
- **DOI:** https://doi.org/10.1109/CVPR.2001.990517

### 1.2 HOG + SVM

- **Tipo:** método clássico baseado em descritores HOG (*Histogram of Oriented Gradients*) e classificação com SVM (*Support Vector Machine*).
- **Funcionamento:** representa padrões locais de bordas e gradientes; um classificador treinado distingue janelas de rosto das demais regiões.
- **Interesse no estudo:** alternativa com representação por gradientes, diferente das características Haar e da classificação em cascata.
- **Limitações a testar:** custo da varredura multiescala, sensibilidade a pose e dependência da base usada no treinamento do classificador facial.
- **Artigo de referência do descritor:** Dalal, N.; Triggs, B. (2005). *Histograms of Oriented Gradients for Human Detection*.
- **DOI:** https://doi.org/10.1109/CVPR.2005.177
- **Nota bibliográfica:** o artigo original apresenta o HOG para **detecção de pessoas**, não uma implementação específica de detector facial. A versão do detector de rostos escolhida para os experimentos deverá ser identificada e documentada separadamente (por exemplo, o detector HOG do dlib).

**Comparação direta — Viola–Jones × HOG + SVM**

| Aspecto | Viola–Jones | HOG + SVM |
|---|---|---|
| Características | Padrões Haar de intensidade | Histogramas de orientação de gradientes |
| Classificação | Cascata de classificadores | SVM sobre descritores HOG |
| Vantagem investigada | Rejeição rápida de regiões negativas | Representação local de formas e contornos |
| Principal variável de controle | Cascata e parâmetros de varredura | Detector treinado, escala e parâmetros de varredura |

Não há vencedor presumido: precisão, robustez e tempo serão medidos nas mesmas imagens.

## 2. Detecção facial — aprendizado profundo

### 2.1 YuNet

- **Tipo:** detector facial baseado em rede neural convolucional leve e arquitetura *anchor-free*.
- **Funcionamento:** estima posições de rostos e pontos faciais diretamente a partir da imagem.
- **Interesse no estudo:** representação de um detector orientado a execução eficiente e implantação simplificada.
- **Limitações a testar:** detecção de rostos muito pequenos, oclusões, ângulos e diferentes resoluções.
- **Artigo:** Wu, W.; Peng, C.; Yu, S. (2023). *YuNet: A Tiny Millisecond-level Face Detector*.
- **DOI:** https://doi.org/10.1007/s11633-023-1423-y
- **Código/modelo:** https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet

### 2.2 SCRFD

- **Tipo:** família de detectores faciais convolucionais, concebida para melhorar a relação entre precisão e custo computacional por redistribuição de amostras e computação.
- **Funcionamento:** realiza detecção facial com arquiteturas disponíveis em diferentes escalas de complexidade.
- **Interesse no estudo:** comparar outro detector eficiente e selecionar uma variante específica, registrada no protocolo.
- **Limitações a testar:** variação de desempenho conforme o checkpoint, custo de inferência e resolução de entrada.
- **Artigo:** Guo, J. et al. (2022). *Sample and Computation Redistribution for Efficient Face Detection* (ICLR 2022).
- **DOI do preprint:** https://doi.org/10.48550/arXiv.2105.04714
- **Publicação da conferência:** https://openreview.net/forum?id=RhB1AdoFfGE
- **Código:** https://github.com/deepinsight/insightface/tree/master/detection/scrfd
- **Nota:** o DOI acima identifica o **preprint no arXiv**, não um DOI específico do artigo da ICLR.

**Comparação direta — YuNet × SCRFD**

| Aspecto | YuNet | SCRFD |
|---|---|---|
| Proposta | Detector especialmente compacto | Família de detectores com diferentes orçamentos computacionais |
| Integração típica | OpenCV | Implementações InsightFace/ONNX |
| Decisão experimental | Fixar versão do modelo | Fixar a variante e os pesos avaliados |
| Questão principal | Até onde vai a eficiência de um modelo leve? | Qual o ganho de qualidade por custo frente ao YuNet? |

## 3. Remoção de fundo — métodos clássicos

### 3.1 GrabCut

- **Tipo:** segmentação de primeiro plano e fundo com modelos probabilísticos de cor e otimização por cortes em grafos.
- **Funcionamento:** parte de uma região ou máscara inicial, modela cores de primeiro plano e fundo e refina a separação iterativamente.
- **Interesse no estudo:** baseline clássico consolidado para extração de primeiro plano.
- **Limitações a testar:** dependência da inicialização, dificuldade em bordas delicadas e fundos com cores semelhantes às da pessoa.
- **Artigo:** Rother, C.; Kolmogorov, V.; Blake, A. (2004). *GrabCut: Interactive Foreground Extraction Using Iterated Graph Cuts*.
- **DOI:** https://doi.org/10.1145/1015706.1015720

### 3.2 Closed-Form Matting

- **Tipo:** *image matting* clássico baseado em um modelo local de cores e na solução de um sistema linear para estimar uma máscara alfa.
- **Funcionamento:** a partir de restrições de primeiro plano e fundo, como uma *trimap*, calcula valores contínuos de opacidade para os pixels.
- **Interesse no estudo:** avaliar a extração de contornos finos e transições parciais, que não são naturalmente representadas por máscaras binárias.
- **Limitações a testar:** necessidade de restrições iniciais de primeiro plano/fundo, custo computacional e qualidade da trimap.
- **Artigo principal:** Levin, A.; Lischinski, D.; Weiss, Y. (2008). *A Closed-Form Solution to Natural Image Matting* (IEEE TPAMI).
- **DOI:** https://doi.org/10.1109/TPAMI.2007.1177
- **Versão anterior:** CVPR 2006 — https://doi.org/10.1109/CVPR.2006.18

**Comparação direta — GrabCut × Closed-Form Matting**

| Aspecto | GrabCut | Closed-Form Matting |
|---|---|---|
| Problema principal | Separar objeto e fundo | Estimar opacidade/transparência do primeiro plano |
| Saída nativa | Máscara de segmentação, em geral binária | Máscara alfa contínua |
| Inicialização | Retângulo ou máscara de rótulos | Restrições/trimap |
| Principal interesse | Delimitação global da pessoa | Qualidade das transições e dos contornos |

**Cuidados:** esses métodos não resolvem exatamente a mesma tarefa. Para compará-los, serão necessárias métricas de segmentação binária e, quando houver referências alfa, métricas de *matting*. A inicialização deverá ser automática e **não poderá usar a máscara verdadeira** das imagens de teste.

## 4. Remoção de fundo — aprendizado profundo

### 4.1 MODNet

- **Tipo:** rede neural para *portrait matting* sem trimap explícita.
- **Funcionamento:** combina componentes de compreensão semântica, detalhe e fusão para estimar a opacidade do primeiro plano em retratos.
- **Interesse no estudo:** avaliar uma arquitetura especializada em retratos, projetada com atenção à eficiência.
- **Limitações a testar:** generalização para fundos complexos, cabelos e perfis fora das condições habituais de retrato.
- **Artigo:** Ke, Z. et al. (2022). *MODNet: Real-Time Trimap-Free Portrait Matting via Objective Decomposition* (AAAI 2022).
- **DOI:** https://doi.org/10.1609/aaai.v36i1.19999
- **Código:** https://github.com/ZHKKKe/MODNet

### 4.2 BiRefNet (variante Portrait)

- **Tipo:** rede neural para segmentação de primeiro plano de alta resolução, com referências bilaterais para localização e refinamento.
- **Funcionamento:** combina informação global da imagem e detalhes de alta resolução para melhorar a delimitação do objeto.
- **Interesse no estudo:** comparar um modelo voltado à qualidade de segmentação e refinamento de contornos com a arquitetura específica de retratos do MODNet.
- **Limitações a testar:** custo computacional, dependência do checkpoint e qualidade de contorno conforme a saída disponibilizada pela variante.
- **Artigo da arquitetura:** Zheng, P. et al. (2024). *Bilateral Reference for High-Resolution Dichotomous Image Segmentation*.
- **DOI:** https://doi.org/10.26599/AIR.2024.9150038
- **Código:** https://github.com/ZhengPeng7/BiRefNet
- **Pesos Portrait:** https://huggingface.co/ZhengPeng7/BiRefNet-portrait
- **Nota bibliográfica:** o DOI se refere ao artigo da arquitetura BiRefNet; o checkpoint Portrait precisa ser identificado por versão/revisão nos experimentos. Uma saída contínua de probabilidade de segmentação não equivale, por definição, a uma estimativa de alfa fisicamente calibrada.

**Comparação direta — MODNet × BiRefNet Portrait**

| Aspecto | MODNet | BiRefNet Portrait |
|---|---|---|
| Foco original | *Portrait matting* | Segmentação de primeiro plano de alta qualidade; variante para retratos |
| Saída a verificar | Alfa contínuo | Mapa contínuo de segmentação/refinamento; verificar checkpoint |
| Principal hipótese | Melhor compromisso entre qualidade e custo | Potencial maior detalhamento com custo superior |
| Avaliação necessária | Contornos, alfa e desempenho | Contornos, segmentação e desempenho |

As diferenças de qualidade e custo acima são **hipóteses**, não conclusões. Serão investigadas usando o mesmo conjunto de imagens e ambiente de execução.

## 5. Transformações de centralização e recorte

Além dos oito métodos, serão comparadas **duas estratégias geométricas**, que não entram na contagem dos algoritmos de detecção/segmentação:

1. **Centralização com deslocamento e preenchimento (*padding*):** reposiciona a imagem para alinhar a face a uma posição-alvo e preenche áreas descobertas. Preserva os pixels originais, mas introduz regiões artificiais.
2. **Centralização por recorte (*cropping*):** seleciona uma região da imagem centrada ou enquadrada em torno da face. Evita adicionar pixels artificiais, mas remove conteúdo original.

**Controle:** imagem original, sem transformação. As mesmas operações geométricas devem ser aplicadas às máscaras de referência para produzir comparações válidas.

## 6. Resumo dos oito métodos

| Tarefa | Abordagem | Método 1 | Método 2 |
|---|---|---|---|
| Detecção facial | Clássica | Viola–Jones | HOG + SVM |
| Detecção facial | Aprendizado profundo | YuNet | SCRFD |
| Remoção de fundo / matting | Clássica | GrabCut | Closed-Form Matting |
| Remoção de fundo / matting | Aprendizado profundo | MODNet | BiRefNet Portrait |

## 7. Regras para as próximas etapas

- Fixar e documentar a **implementação exata**, versão, pesos e parâmetros de cada método.
- Confirmar licenças de código e de pesos antes de redistribuí-los.
- Evitar tratamento privilegiado de métodos que exijam inicialização (GrabCut e Closed-Form Matting): anotações de referência servem apenas para avaliação.
- Separar métricas de **detecção**, **segmentação binária**, **matting alfa** e **desempenho computacional**.
- Usar conjuntos de validação para escolhas de parâmetros e reservar as imagens de teste para a avaliação final.
- Relatar falhas de detecção, falhas de processamento e tempo/memória, não apenas os casos bem-sucedidos.

## 8. Adaptações e controles para comparações justas

Esta seção define **ajustes metodológicos necessários antes dos experimentos**. O objetivo não é tornar os métodos artificialmente iguais, mas assegurar que diferenças nos resultados possam ser atribuídas aos algoritmos, e não a vantagens indevidas de entrada, anotação, pré-processamento ou avaliação. Cada adaptação deve ficar registrada no protocolo experimental, com versão e parâmetros.

### 8.1 Regras comuns aos oito métodos

- **Mesmas amostras e divisões:** usar os mesmos conjuntos de teste, com identificadores fixos; ajustar parâmetros exclusivamente em um conjunto de validação separado.
- **Execução reprodutível:** registrar biblioteca, versão, checkpoint e hash dos pesos, parâmetros, dispositivo, sistema operacional e sementes aleatórias quando aplicáveis.
- **Entradas consistentes:** carregar todas as imagens da mesma fonte; documentar conversões RGB/BGR, orientação EXIF, resolução e normalização. Não aplicar melhorias específicas a um único algoritmo sem justificativa.
- **Saídas padronizadas:** detectar faces em caixas `(x, y, largura, altura)` na resolução original; produzir máscaras de segmentação em `[0, 1]` e no mesmo tamanho e sistema de coordenadas da imagem avaliada.
- **Métricas separadas por tarefa:** não combinar diretamente métricas de detecção de faces, segmentação binária, *matting* alfa e custo computacional numa pontuação única sem critério justificado.
- **Falhas explícitas:** registrar imagem sem face, múltiplas faces, exceção de inferência, máscara vazia e tempo excedido. Nunca excluir silenciosamente casos difíceis.

### 8.2 Detecção facial: Viola–Jones × HOG + SVM × YuNet × SCRFD

| Ajuste | Como aplicar | Por que é necessário |
|---|---|---|
| Versão do detector | Fixar a cascata Haar, a versão e pesos do HOG + SVM, o ONNX YuNet e uma variante/checkpoint SCRFD | Evita comparar implementações ou modelos diferentes sem rastreabilidade |
| Escala de entrada | Testar uma condição de entrada original ou de resolução comum; quando os modelos exigirem tamanhos internos específicos, registrar essas transformações | Limita o efeito da resolução e preserva as restrições naturais dos modelos |
| Conversão de caixas | Transformar todas as caixas para coordenadas da imagem original, incluindo correção de escala e *letterboxing* | Permite calcular erros e IoU no mesmo referencial |
| Limiar de confiança | Definir em validação quando existir; não inventar um limiar equivalente para detectores sem escore compatível | Escores dos modelos não são diretamente comparáveis |
| Seleção de face | Na avaliação de detecção, avaliar todas as faces anotadas; na avaliação de centralização com uma face-alvo, aplicar a mesma regra documentada (ex.: maior face) | Impede que a escolha da face favoreça um detector |
| Pós-processamento | Fixar NMS e parâmetros de varredura por implementação, documentando-os | O comportamento final depende desses parâmetros |

**Comparação principal:** taxa de detecção/recall, precisão, IoU das caixas, erro do centro facial e tempo por imagem. Em imagens com várias faces, usar um critério de correspondência consistente entre detecções e anotações. A comparação de desempenho deve registrar o tempo de pré-processamento, inferência e pós-processamento, além do tempo total.

### 8.3 Remoção de fundo: GrabCut × Closed-Form Matting

Esses métodos precisam de **informações iniciais diferentes**. O experimento principal será **totalmente automático**, sem intervenção humana por imagem e sem consultar a máscara de referência para gerar entradas auxiliares.

- **GrabCut:** gerar automaticamente uma região inicial ou máscara com rótulos de fundo provável/definido e primeiro plano provável/definido. Fixar a heurística, o número de iterações e os parâmetros por meio da validação. Guardar a inicialização produzida para auditoria.
- **Closed-Form Matting:** gerar automaticamente uma *trimap* com regiões de primeiro plano, fundo e área desconhecida. Registrar o algoritmo que gera a trimap, largura da região desconhecida e parâmetros do solucionador. Nunca construir a trimap a partir da máscara alfa de referência do conjunto de teste.
- **Origem da informação auxiliar:** quando possível, derivar inicializações de uma **mesma fonte automática de pistas** (por exemplo, posição/região estimada da pessoa), sem exigir que as estruturas finais sejam idênticas. Registrar o custo dessas pistas.
- **Dependência entre métodos:** evitar usar a saída final do GrabCut como trimap do Closed-Form Matting na comparação principal, pois isso tornaria o segundo método dependente do primeiro. Se essa combinação for interessante, avaliá-la em um experimento **separado de pipeline**.
- **Duas avaliações distintas:** (a) comparação end-to-end incluindo a geração automática das inicializações e (b) estudo de sensibilidade à qualidade das inicializações, mantendo as condições controladas e devidamente identificadas.

**Cuidado interpretativo:** GrabCut é primariamente uma segmentação binária; Closed-Form Matting estima uma máscara alfa. Compará-los apenas por IoU descartaria parte do objetivo do matting. Para uma comparação binária, aplicar um limiar fixo e comum aos mapas contínuos, definido previamente; para métricas alfa, usar apenas saídas com interpretação de alfa e dados de referência apropriados.

### 8.4 Remoção de fundo por IA: MODNet × BiRefNet Portrait

- **Pesos fixos:** escolher exatamente um checkpoint por arquitetura para a comparação principal, registrando origem, revisão e resolução esperada; variantes adicionais serão experimentos separados.
- **Pré-processamento prescrito:** respeitar normalização e tamanho de entrada exigidos por cada modelo, mas registrar todas as operações e retornar a saída ao espaço de coordenadas da imagem original.
- **Saídas comparáveis:** converter saídas para mapas contínuos em `[0, 1]`, preservando os valores originais para análise; somente depois aplicar um limiar único para métricas binárias.
- **Diferença semântica:** MODNet é um método de *portrait matting*. A saída contínua do BiRefNet Portrait não deve ser tratada automaticamente como alfa físico sem validação. Avaliações de SAD/MSE alfa devem apresentar essa ressalva e, preferencialmente, separar resultados por tipo de saída.
- **Inferência padronizada:** usar modo de avaliação, sem gradientes e com o mesmo tipo de dispositivo quando tecnicamente possível; registrar processamento em CPU/GPU e eventuais operações específicas obrigatórias.
- **Resolução:** analisar tanto a qualidade na resolução de saída reconstruída quanto a influência da redução interna, já que modelos podem ter exigências distintas.

### 8.5 Centralização, recorte e efeito na segmentação

O experimento deverá conter pelo menos três condições pareadas para **cada imagem**:

1. **Original:** sem deslocamento, recorte ou preenchimento.
2. **Deslocamento com preenchimento:** mesma pessoa e conteúdo original preservado, com regiões adicionais identificadas explicitamente.
3. **Recorte:** região ajustada à face, com a área efetivamente preservada registrada.

Regras:

- **Isolar geometria do detector:** primeiro aplicar as transformações usando as mesmas caixas faciais de referência; em uma avaliação posterior, usar caixas previstas e medir a propagação de erros da detecção.
- **Transformação sincronizada:** aplicar às máscaras de referência a mesma transformação geométrica da imagem, com interpolação apropriada (vizinho mais próximo para máscaras binárias; interpolação contínua para alfa).
- **Pixels sintéticos:** regiões de *padding* não têm anotação real; excluí-las das métricas principais por uma máscara de validade ou criar uma avaliação separada para essas regiões. Não presumir que preenchimento visual corresponda a fundo verdadeiro.
- **Área comum:** além da avaliação em cada imagem transformada, calcular métricas **na interseção das regiões originalmente válidas**, para evitar que a remoção de áreas difíceis pelo recorte infle artificialmente os resultados.
- **Tamanho e resolução:** registrar dimensões, proporção da face, área preservada e eventual redimensionamento. Se houver redimensionamento posterior, comparar também uma condição de resolução controlada.
- **Parâmetros fixos:** definir posição-alvo da face, proporção de saída e regras de recorte antes da avaliação final, sem ajustes individuais baseados na máscara de referência.

### 8.6 Métricas, desempenho e apresentação dos resultados

| Grupo | Métricas/registro | Critério de justiça |
|---|---|---|
| Detecção | Precisão, recall, IoU de caixas, erro de centro | Mesmas anotações, limiares de avaliação e regras de correspondência |
| Segmentação binária | IoU, Dice, Boundary F1 | Mesma região válida e limiar binário predefinido |
| Matting alfa | SAD, MSE e análise de contornos alfa | Dataset com alfa real; informar distinções semânticas das saídas |
| Desempenho | Latência total, latência por estágio, pico de RAM e VRAM quando aplicável | Mesmo hardware e condições de medição; incluir custo de pistas, trimaps e pré/pós-processamento |
| Robustez | Falhas e métricas por tipo de imagem | Mesmas imagens e critérios de estratificação |

- Relatar médias e dispersão, métricas **por imagem** e intervalos de confiança quando apropriado.
- Para comparações entre métodos, usar análise **pareada** sobre as mesmas imagens.
- Não atribuir superioridade automática ao método que utilize mais recursos: apresentar qualidade e custo separadamente (e, quando útil, uma fronteira de Pareto).
- Não ajustar parâmetros a partir dos resultados finais do teste.

### 8.7 Checklist de implementação dos controles

- [ ] Definir contratos únicos para caixas faciais, máscaras, metadados e falhas.
- [ ] Fixar versões, checkpoints, licenças e parâmetros dos oito métodos.
- [ ] Implementar e testar gerador automático de inicialização GrabCut.
- [ ] Implementar e testar gerador automático de trimap para Closed-Form Matting.
- [ ] Definir padronização de resolução, coordenadas e limiares de binarização.
- [ ] Implementar máscaras de validade para *padding* e recorte.
- [ ] Garantir sincronização das transformações aplicadas às máscaras de referência.
- [ ] Medir tempos totais e tempos separados por estágio, incluindo inicialização.
- [ ] Registrar resultados pareados por imagem e condição.
- [ ] Documentar quais comparações são diretas e quais exigem ressalvas por diferenças de tarefa.

**Regra de prioridade:** esses controles são requisitos para o protocolo e a implementação, não resultados antecipados. Se alguma comparação não puder ser realizada de modo equivalente, documentar a diferença em vez de forçar uma equivalência artificial.

---

*Documento de seleção metodológica. Resultados quantitativos serão acrescentados em documentos próprios após a execução dos experimentos.*
