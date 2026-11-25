# Métricas de avaliação

Este documento define as métricas dos três experimentos do projeto **face-processing-benchmark**. A avaliação é organizada pelos **resultados das tarefas**, e não pelos componentes internos dos algoritmos:

1. **Centralização facial:** posicionar corretamente o rosto na imagem.
2. **Remoção de fundo:** extrair a pessoa da imagem original.
3. **Influência da centralização e do recorte:** medir se o pré-processamento modifica a qualidade e o desempenho da remoção de fundo.

Os critérios, limiares e estratégias de agregação devem ser fixados **antes** de executar a avaliação final. Métricas de qualidade e de desempenho computacional serão apresentadas separadamente.

## Experimento 1 — Centralização facial

**Pergunta:** entre Viola-Jones, HOG + SVM, YuNet e SCRFD, qual produz a centralização facial mais correta e eficiente quando inserido no mesmo pipeline de transformação?

**Base:** LFW. O protocolo inicial reutiliza a construção de imagens sinteticamente descentralizadas, com deslocamento, escala e rotação controlados. A posição de referência é aproximada, porque o centro das imagens LFW alinhadas não equivale necessariamente ao centro anatômico preciso do rosto.

**Controle:** usar os mesmos exemplos, transformações e política de seleção de rosto para todos os detectores; isolar a contribuição do detector mantendo o algoritmo geométrico de centralização fixo em cada comparação.

### Métricas principais

| Métrica | Definição | Melhor resultado |
|---|---|---|
| Erro de centralização (px) | Distância entre a posição **de referência do rosto após a transformação** e a posição-alvo da saída | Menor |
| Erro de centralização normalizado | Erro em pixels dividido pela diagonal da imagem de saída | Menor |
| Taxa de centralização correta (%) | Percentual de entradas com saída válida e erro abaixo de um limiar predefinido | Maior |

Para o centro de referência transformado \((x_r,y_r)\) e a posição-alvo \((x_t,y_t)\):

\[
E_c = \sqrt{(x_r-x_t)^2+(y_r-y_t)^2}
\]

\[
E_n = \frac{E_c}{\sqrt{W_{out}^2+H_{out}^2}}
\]

\[
T_c = \frac{\#\{\text{entradas com saída válida e } E_n \leq \tau\}}{N_{total}}\times 100
\]

O limiar normalizado \(\tau\) será fixado no protocolo. Para **reproduzir os testes anteriores**, também será reportada separadamente a taxa com tolerância de **15 px em imagens 500 × 500**, sem confundir esse resultado com avaliações em outras resoluções.

**Atenção:** usar como referência o rosto transformado a partir da anotação/posição estimada na entrada, **não** o centro da detecção gerada pelo próprio modelo; isso evitaria erros artificiais iguais a zero.

### Métricas complementares

- **Taxa de detecção (%):** fração de entradas em que há uma face detectada; serve para explicar falhas, não para definir sozinha o melhor centralizador.
- **Taxa de saída válida (%):** fração de entradas que produzem imagem geometricamente válida, sem região vazia indevida ou dimensões inválidas.
- **Área original preservada (%):** fração da imagem original efetivamente mantida na saída, medida com mapeamento geométrico.
- **Área de preenchimento (%):** fração de pixels da saída sem correspondência com a imagem original; relevante para centralização com padding.
- **Escala relativa da face:** tamanho do rosto em relação à saída, para identificar enquadramentos não comparáveis.

Falhas de detecção, centralização ou recorte são **insucesso** nas taxas sobre todas as entradas. As distribuições dos erros podem ser apresentadas apenas para saídas válidas, desde que a quantidade de falhas seja informada explicitamente.

## Experimento 2 — Remoção de fundo em imagens originais

**Pergunta:** entre GrabCut, Closed-Form Matting, MODNet e BiRefNet Portrait, qual apresenta melhor qualidade de remoção de fundo e custo computacional?

**Bases:** PPM-100 para testes e validação da implementação; **P3M-500-NP para avaliação experimental final**. Nesta avaliação, as imagens são processadas no enquadramento original, **sem recorte ou centralização prévia**.

### Métricas principais de segmentação binária

| Métrica | Definição | Melhor resultado |
|---|---|---|
| IoU | Interseção sobre união das máscaras binárias | 1 |
| Dice | Duas vezes a interseção dividida pela soma das áreas | 1 |
| Boundary F1 | F1 de correspondência entre contornos com tolerância espacial definida | 1 |

\[
IoU = \frac{|P\cap G|}{|P\cup G|}, \qquad Dice = \frac{2|P\cap G|}{|P|+|G|}
\]

\(P\) é a máscara prevista binária e \(G\), a máscara de referência binária. Máscaras alfa serão binarizadas **com o mesmo limiar fixado previamente**, inclusive para métodos que produzem saídas contínuas. O Boundary F1 exige explicitar a tolerância (em pixels ou normalizada pela diagonal) e a regra de correspondência entre bordas.

### Métricas de alpha matting

| Métrica | Definição | Melhor resultado |
|---|---|---|
| SAD | Soma das diferenças absolutas de alfa | Menor |
| MSE | Média dos erros quadráticos de alfa | Menor |
| MAE (complementar) | Média das diferenças absolutas de alfa | Menor |
| Gradient Error (complementar) | Diferenças de gradiente na transparência | Menor |
| Connectivity Error (complementar) | Diferenças estruturais das regiões de transparência | Menor |

Com alfa de referência \(\alpha_i\) e alfa previsto \(\hat\alpha_i\), normalizados em \([0,1]\):

\[
SAD=\sum_{i=1}^{N}|\alpha_i-\hat\alpha_i|, \qquad
MSE=\frac{1}{N}\sum_{i=1}^{N}(\alpha_i-\hat\alpha_i)^2, \qquad
MAE=\frac{SAD}{N}
\]

Como o **SAD cresce com a quantidade de pixels**, registrar também MAE e resolução. As definições e normalizações de Gradient Error e Connectivity Error devem seguir uma implementação de referência fixa.

**Comparabilidade:** GrabCut produz tipicamente máscara binária; Closed-Form Matting e MODNet estimam alfa, enquanto a saída do checkpoint BiRefNet Portrait deverá ser caracterizada na implementação (uma probabilidade de primeiro plano não deve ser automaticamente interpretada como transparência fisicamente calibrada). Para calcular erros alfa em saídas binárias, informar que a máscara 0/1 foi utilizada como aproximação e discutir a limitação. Não usar máscaras verdadeiras para construir a inicialização ou trimap dos métodos clássicos.

## Experimento 3 — Remoção de fundo antes e depois da centralização

**Pergunta:** a centralização, com ou sem recorte, altera a qualidade e o custo da remoção de fundo em relação ao processamento da fotografia original?

**Base principal:** P3M-500-NP, com as mesmas imagens e os mesmos quatro métodos do Experimento 2.

### Condições

| Código | Entrada fornecida ao segmentador |
|---|---|
| C0 | Original, sem centralização ou recorte |
| C1 | Centralizada por deslocamento, sem recorte, com preenchimento nas áreas expostas |
| C2 | Centralizada com recorte, sem preenchimento |

As transformações de C1 e C2 devem ter **parâmetros e origem documentados**. Usar a mesma transformação geométrica em cada método de segmentação; não adaptar a centralização individualmente para favorecer segmentadores. Se o detector não conseguir centralizar uma imagem, registrar a falha e aplicar o protocolo de exclusão previamente definido para a comparação pareada, reportando o número de amostras excluídas.

### Métricas

Reutilizar integralmente as métricas de qualidade do **Experimento 2** (IoU, Dice, Boundary F1, SAD, MSE e MAE, quando adequadas), mais as métricas de tempo e memória definidas abaixo.

O resultado central será a **diferença pareada por imagem e método**:

\[
\Delta M_{C1}=M(C1)-M(C0), \qquad \Delta M_{C2}=M(C2)-M(C0)
\]

Para IoU/Dice/Boundary F1, diferença positiva indica melhoria. Para SAD/MSE/MAE, diferença negativa indica melhoria.

Reportar:

- Média, mediana e dispersão das diferenças pareadas.
- Percentual de imagens que melhoraram, pioraram ou permaneceram praticamente iguais (tolerância declarada).
- Intervalos de confiança e, se apropriado, testes estatísticos pareados.
- Tempo e memória por condição, acompanhados das **dimensões de entrada** e da **área de pixels processados**.

### Controle contra conclusões enganosas

1. **Máscara de referência transformada:** aplicar à máscara alfa de referência exatamente a transformação geométrica da imagem correspondente, com interpolação e convenções registradas.
2. **Região comparável:** além do resultado na saída inteira, calcular uma análise controlada na **região original preservada comum às condições**, após reprojetar máscaras para coordenadas comparáveis, evitando que o recorte pareça melhorar só por remover áreas difíceis.
3. **Padding:** distinguir área de imagem original de área preenchida; avaliar o preenchimento separadamente ou excluir sua região das métricas controladas, segundo regra predefinida.
4. **Resolução:** relatar o número de pixels processados, pois a redução de tempo em C2 pode resultar simplesmente de uma imagem menor. Se houver redimensionamento obrigatório por modelo, registrar as dimensões efetivas da inferência.
5. **Seleção de amostras:** usar o mesmo subconjunto de imagens para diferenças pareadas e divulgar a cobertura de cada condição.

## Desempenho computacional — aplicável aos três experimentos

| Métrica | Medida | Observação |
|---|---|---|
| Tempo por imagem (ms) | Mediana, média e dispersão | Separar carregamento/inicialização de inferência e pós-processamento |
| Memória máxima (MB) | Pico de RAM durante execução | Registrar método e ferramenta de medição |
| VRAM máxima (MB), se houver GPU | Pico de memória de vídeo | Não confundir com RAM |
| Tempo do pipeline completo (ms) | Detecção + transformação + segmentação | Principalmente para o Experimento 3 |
| Tamanho do modelo (MB) | Espaço ocupado pelos pesos | Apenas para modelos com pesos |

Fixar hardware, versões, dispositivo (CPU/GPU), número de threads, resolução, aquecimento (*warm-up*) e quantidade de repetições. Sincronizar a GPU nas medições temporais. Os resultados de tempo devem ser apresentados **com e sem** o custo do pré-processamento quando esse custo afetar a interpretação.

## Resumo das métricas por experimento

| Experimento | Qualidade principal | Desempenho |
|---|---|---|
| **1 — Centralização** | Erro (px), erro normalizado, taxa de sucesso | Tempo, RAM |
| **2 — Remoção de fundo** | IoU, Dice, Boundary F1, SAD, MSE | Tempo, RAM/VRAM |
| **3 — Antes × depois** | Diferenças pareadas das métricas do Exp. 2; avaliação em região comum | Diferenças de tempo, RAM/VRAM, resolução |

## Decisões a fixar antes da avaliação final

- Limiar de centralização correta e seu critério normalizado.
- Limiar de binarização das máscaras alfa.
- Tolerância espacial do Boundary F1.
- Estratégia de preenchimento e parâmetros do recorte.
- Regras de geração automática da inicialização do GrabCut e da trimap do Closed-Form Matting.
- Política de falhas e denominadores das métricas.
- Resolução de entrada, tratamento de máscaras e configurações dos modelos.
- Repetições, aquecimento e método de medida de memória/tempo.
- Estratégia de análise estatística e tratamento de múltiplas comparações.

Essas escolhas serão detalhadas na definição dos cenários experimentais e congeladas antes da execução com o P3M-500-NP.
