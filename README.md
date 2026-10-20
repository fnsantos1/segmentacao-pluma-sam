# Segmentação de pluma de fumaça com SAM (Segment Anything Model)

Notebook da atividade: avaliar a máscara que o SAM produz para uma **pluma de fumaça**, testar
diferentes *prompts*, melhorar a apresentação da máscara e **justificar** as melhorias com medições.

> Substitua `SEU_USUARIO/SEU_REPO` pelos seus dados depois de subir o repositório.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU_USUARIO/SEU_REPO/blob/main/Segmentacao_Pluma_SAM.ipynb)

---

## Onde está cada item do enunciado

| Enunciado | Etapa |
|---|---|
| A máscara cobre a pluma? | 4.1 — `recall` e `cobertura pluma (%)` |
| Inclui regiões que não pertencem a ela? | 4.1 — `vazamento ceu / nuvem_haze / edificacao (%)` e `precisão` |
| Deixa partes da fumaça de fora? | 4.1 — `1 − recall` e mapa de erro (falso negativo em azul) |
| Caixa delimitadora e pontos positivos/negativos | 2 |
| Pelo menos três configurações de *prompts* | 2 — três configurações (A, B, C) |
| Original / máscara binária / máscara sobreposta lado a lado | 3 — uma figura por configuração + grade comparativa |
| O que dificultou a segmentação | 1 (diagnóstico fotométrico) e 5 |
| Efeito de iluminação, contraste e semelhança fumaça×nuvem | 1 (Bhattacharyya) e 4.2 (contraste reduzido) |
| Avaliação no código | 4.1 (tabela + CSV) |

## As três configurações de *prompt*

| | *Prompt* | Hipótese testada |
|---|---|---|
| A | só caixa delimitadora | o retângulo basta? Ele contém muito céu junto da pluma. |
| B | só 3 pontos positivos | sem limite espacial, até onde a região espalha? |
| C | caixa + 5 positivos + 8 negativos | dizer o que **não** é pluma resolve a ambiguidade? |

A melhoria central é **C**: como pluma e nuvem/*haze* têm estatística parecida (medido na Etapa 1),
o distrator está *dentro* da caixa, e o ponto negativo é o único elemento do *prompt* capaz de
excluí-lo.

## Como rodar

1. Abra no Colab (badge acima) e selecione **GPU** em
   `Ambiente de execução → Alterar o tipo de ambiente de execução`.
   Sem GPU ele cai para o modelo `vit_b`, mais leve.
2. `Ambiente de execução → Executar tudo`. A primeira execução baixa o *checkpoint* do SAM
   (2,4 GB no `vit_h`, 375 MB no `vit_b`).
3. O que vale ajustar está no dicionário `CFG`, na Etapa 0.

### Usar a sua própria imagem

Ponha `CFG["IMAGEM"] = "upload"` (ou um caminho/URL) e **ajuste os *prompts*** no catálogo da
Etapa 0. As coordenadas são **frações** da largura/altura (`0.0`–`1.0`), então valem para qualquer
resolução; a Etapa 0 imprime a imagem com uma grade rotulada em pixel **e** em fração para você ler
as coordenadas.

## Imagens de teste (domínio público, Wikimedia Commons)

| Chave | Imagem | Por que foi escolhida |
|---|---|---|
| `socal` | *Smoke plume from SoCal wildfire, outubro/2007* | Tem os três distratores do enunciado ao mesmo tempo — céu, *haze* parecido com nuvem e edifícios — e uma placa que **oclui** a pluma. |
| `yellowstone` | *Wildfire in Yellowstone NP produces Pyrocumulus clouds* | Caso extremo de semelhança fumaça×nuvem: o incêndio **gera** nuvens de verdade. |

## Resumo da conclusão

O SAM é agnóstico a classe: ele não tem o conceito "fumaça", apenas devolve a região coerente
indicada pelo *prompt*. Como a pluma tem **borda difusa**, **baixa saturação** e luminância parecida
com a de nuvens e do *haze* do horizonte, o *prompt* precisa declarar explicitamente o que **não** é
pluma — por isso os **pontos negativos** são a melhoria de maior impacto. A Etapa 4.2 mostra ainda
que a mesma cena, com o mesmo *prompt*, dá outra máscara só por causa de uma mudança de contraste.

## Arquivos

```
Segmentacao_Pluma_SAM.ipynb   notebook da atividade (é isto que se entrega)
README.md                     este arquivo
saida/                        gerada ao rodar: figuras, máscaras PNG e métricas em CSV
fonte/                        apoio da construção do notebook (fora do versionamento)
```

Há também uma **versão estendida** no primeiro commit do repositório, com seis configurações de
*prompt* (incluindo refinamento iterativo via `mask_input` e máscara suave por filtro guiado), o
*baseline* do `SamAutomaticMaskGenerator`, testes de perturbação da caixa e de ponto positivo na
nuvem, e um relatório automático em texto. Para recuperá-la:

```bash
git show ca7efa3:Segmentacao_Pluma_SAM.ipynb > Segmentacao_Pluma_SAM_completo.ipynb
```

## Limitações declaradas

* A máscara de **referência** da imagem `socal` é um polígono traçado à mão e **aproximado** — na
  base da pluma não existe fronteira objetiva entre fumaça e *haze*. Os valores de IoU/Dice servem
  para comparar as configurações **entre si**, não como medida absoluta.
* Resultados vêm de **uma** imagem por execução. Uma avaliação robusta exigiria N imagens com
  média ± desvio.
