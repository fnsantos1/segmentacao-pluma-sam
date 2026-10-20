# Segmentação de pluma de fumaça com SAM

Continuação do notebook inicial da atividade, com a mesma stack (Ultralytics). O que mudou foi a
forma de acionar o SAM e a forma de avaliar o resultado.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fnsantos1/segmentacao-pluma-sam/blob/main/Segmentacao_Pluma_SAM.ipynb)

## O que estava quebrado no notebook inicial

| Célula | O que acontecia | Causa |
|---|---|---|
| 13 | `FileNotFoundError: 'sam_b.pt'` | `SAM3SemanticPredictor` espera pesos do SAM 3, cujo download deu 404. `sam_b.pt` não aceita prompt de texto. |
| 14 | `(no detections)` e nenhuma máscara gerada | o detector `YOLOv8m-smoke-detection` não encontrou a pluma |
| 12 | "4 cars, 1 truck" | `yolo26n` é COCO, não tem classe de fumaça |
| 7 | `copyfile("pluma.jpg", "pluma.png")` | só renomeia, o arquivo continua JPEG |

Aqui o SAM é acionado por prompt geométrico (caixa e pontos), com `SAM2Predictor`, e `set_image()` é
chamado uma vez só.

## Antes de publicar

A célula 4 do notebook inicial tem uma chave da API do CDS/Copernicus escrita no código. Em
repositório público isso é uma chave vazada. Revogue essa e gere outra no painel do CDS, e leia a nova
de variável de ambiente (`os.environ["CDSAPI_KEY"]`). Este repositório não tem a chave nem a parte de
ERA5/netCDF, que é outra frente do projeto.

## Imagem

A imagem do notebook inicial (`MyDrive/pluma.jpg`) não está mais disponível. A análise usa uma foto de
domínio público (incêndio no sul da Califórnia, outubro de 2007, Wikimedia Commons), que tem os três
distratores citados no enunciado ao mesmo tempo: céu azul, casas e uma faixa de haze esbranquiçada
quase indistinguível da base da pluma. Há também uma placa de trânsito ocluindo parte da pluma.

Para trocar de imagem, mude `CFG["IMAGEM"]` e reescreva `PROMPTS` com as coordenadas da sua pluma.
A Etapa 1 imprime a imagem com eixos em pixel.

## Os três prompts

| | Prompt | Hipótese testada |
|---|---|---|
| A | só a caixa | o retângulo basta? Ele contém muito céu junto da pluma. |
| B | só pontos positivos | sem limite espacial, até onde a região espalha por semelhança? |
| C | caixa + 5 positivos + 8 negativos | declarar o que não é pluma resolve a ambiguidade? |

## Etapas

1. Instalação, imagem, prompts calibrados, referência e visualização com eixos.
2. Predição com os três prompts.
3. Original com prompts, máscara binária e sobreposição, lado a lado.
4. Métricas (IoU, Dice, precisão, recall, área, componentes, compacidade, invasão de céu, haze e
   edificação, IoU entre configurações e separabilidade dentro contra fora), mapa de erro e efeito do
   contraste.
5. Conclusões.

Para rodar, use `Executar tudo` no menu `Ambiente de execução`. Com GPU usa `sam2_b.pt`, sem GPU usa
`sam2_t.pt`.

## Limitações

A máscara de referência é um polígono traçado à mão e aproximado. Na base da pluma não existe
fronteira objetiva entre fumaça e haze, então os valores de IoU e Dice servem para comparar as
configurações entre si. Os resultados também vêm de uma única imagem; uma avaliação robusta exigiria
N imagens, com média e desvio.
