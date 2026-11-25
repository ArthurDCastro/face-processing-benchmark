# Modelos

O YuNet usa o modelo oficial `face_detection_yunet_2023mar.onnx` em
`models/checkpoints/`. A versão, o SHA-256 e os parâmetros estão em
[`configs/methods.yaml`](../configs/methods.yaml). O OpenCV Zoo distribui este
modelo sob a [licença MIT](https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/LICENSE).
As instruções para obter o arquivo estão no
[README do projeto](../README.md#teste-isolado-do-yunet).

O diretório `checkpoints/` é ignorado pelo Git. Importações e verificações de
configuração devem ocorrer sem inicializar modelos ou baixar pesos. Para novos
checkpoints, registre fonte, versão, licença, SHA-256 e instruções de obtenção.

## SCRFD-500MF

O checkpoint `det_500m.onnx` vem do pacote oficial `buffalo_sc.zip` da
[release `model-zoo` do InsightFace](https://github.com/deepinsight/insightface/releases/tag/model-zoo).
O SHA-256 do ONNX está em [`configs/methods.yaml`](../configs/methods.yaml) e é
verificado antes de abrir a sessão ONNX Runtime. Apenas o detector é extraído
do pacote.

O código de referência é MIT. Os pesos oficiais são disponibilizados para
pesquisa não comercial. Uso comercial requer uma licença separada do
InsightFace. [Política de licença do InsightFace](https://github.com/deepinsight/insightface#license)

Em uma cópia nova do repositório, a partir da raiz:

```bash
mkdir -p models/checkpoints
curl -fL 'https://github.com/deepinsight/insightface/releases/download/model-zoo/buffalo_sc.zip' -o /tmp/fpb-buffalo-sc.zip
unzip -p /tmp/fpb-buffalo-sc.zip det_500m.onnx > models/checkpoints/det_500m.onnx
```
