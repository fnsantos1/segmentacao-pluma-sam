# Segmentação de pluma de fumaça com SAM (Segment Anything Model)

Notebook da atividade: avaliar a máscara que o SAM produz para uma **pluma de fumaça**, melhorar
código, *prompts* e apresentação da máscara, e **justificar** cada melhoria com medições.

> Substitua `SEU_USUARIO/SEU_REPO` pelos seus dados depois de subir o repositório.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU_USUARIO/SEU_REPO/blob/main/Segmentacao_Pluma_SAM.ipynb)

---

## Onde está cada item pedido no enunciado

| Enunciado | Etapa do notebook |
|---|---|
| Observar a máscara gerada pelo SAM | 1 (modo automático) e 4 (por configuração) |
| A máscara cobre a pluma? | 5 — `recall` e `cobertura pluma (%)` |
| Inclui regiões que não pertencem a ela? | 5 — `vazamento ceu / nuvem_haze / edificacao (%)` e `precisão` |
| Deixa partes da fumaça de fora? | 5 — `1 − recall` e mapa de erro (falso negativo em azul) |
| Testar caixa delimitadora e pontos positivos/negativos | 3 |
| Pelo menos três configurações de *prompts* | 3 — seis configurações (A–F) |
| Figura lado a lado: original / binária / sobreposta | 4 — uma por configuração + grade comparativa |
| Características da imagem que dificultaram | 2 (diagnóstico) e 6 (experimentos) |
| Efeito de iluminação, contraste e semelhança fumaça×nuvem | 6.1, 6.2 e 6.3 |
| Avaliação no código | 5 (tabela/CSV) e 7 (relatório automático em texto) |

## As seis configurações de *prompt*

| | *Prompt* | Hipótese testada |
|---|---|---|
| A | só caixa | o retângulo sozinho basta? |
| B | só pontos positivos | sem limite espacial, até onde a região cresce? |
| C | caixa + positivos | positivos resolvem a escala dentro da caixa |
| D | caixa + positivos + **negativos** | dizer o que **não** é pluma resolve a ambiguidade |
| E | D + refinamento iterativo (`mask_input`) | realimentar os *logits* estabiliza a borda |
| F | E + morfologia + máscara suave | apresentação sem inventar região nova |

## Como rodar

1. Abra o notebook no Colab (badge acima) e selecione **GPU** em
   `Ambiente de execução → Alterar o tipo de ambiente de execução`.
   Sem GPU ele cai automaticamente para o modelo `vit_b`.
2. `Ambiente de execução → Executar tudo`. A primeira execução baixa o *checkpoint* do SAM
   (2,4 GB para `vit_h`; 375 MB para `vit_b`).
3. Tudo que vale ajustar está no dicionário `CFG`, na Etapa 0.2.

### Usar a sua própria imagem

Ponha `CFG["IMAGEM"] = "upload"` (ou um caminho/URL) e **ajuste os *prompts*** no catálogo da
Etapa 0.4. As coordenadas são **frações** da largura/altura (`0.0`–`1.0`), então valem para qualquer
resolução; a Etapa 0.4 imprime a imagem com uma grade rotulada em pixel **e** em fração justamente
para você ler as coordenadas.

## Imagens de teste (domínio público, Wikimedia Commons)

| Chave | Imagem | Por que foi escolhida |
|---|---|---|
| `socal` | *Smoke plume from SoCal wildfire, outubro/2007* | Tem os três distratores do enunciado ao mesmo tempo — céu, *haze* parecido com nuvem e edifícios — além de uma placa que **oclui** a pluma. |
| `yellowstone` | *Wildfire in Yellowstone NP produces Pyrocumulus clouds* | Caso extremo de semelhança fumaça×nuvem: o incêndio **gera** nuvens de verdade. |

## Resumo da conclusão

O SAM é agnóstico a classe: ele não tem o conceito "fumaça", apenas devolve a região mais coerente
indicada pelo *prompt*. Como a pluma tem **borda difusa**, **baixa saturação** e luminância parecida
com a de nuvens e do *haze* do horizonte, o *prompt* precisa declarar explicitamente o que **não** é
pluma — por isso os **pontos negativos** são a melhoria de maior impacto. O refinamento iterativo e
a morfologia melhoram a borda e a fragmentação; a máscara suave corrige a apresentação, já que fumaça
é semitransparente e nenhum limiar binário é "correto" na borda.

## Arquivos

```
Segmentacao_Pluma_SAM.ipynb   notebook da atividade (é isto que se entrega)
README.md                     este arquivo
saida/                        gerada ao rodar: figuras, máscaras PNG, métricas CSV, relatório TXT
```

## Limitações declaradas

* A máscara de **referência** da imagem `socal` é um polígono traçado à mão e **aproximado** — na
  base da pluma não existe fronteira objetiva entre fumaça e *haze*. Os valores de IoU/Dice servem
  para comparar as configurações **entre si**, não como medida absoluta.
* Resultados vêm de **uma** imagem por execução. Uma avaliação robusta exigiria N imagens com
  média ± desvio.
