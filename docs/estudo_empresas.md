# Estudo dados empresas

Esse é um estudo sobre como os dados são organizados em cada empresa. Ele vai servir para saber qual a melhor estratégia usar pa implementar a extração de dados além dos horários.

# Consórcio Fênix

URL: https://www.consorciofenix.com.br

## /horarios

Tipo do arquivo: HTML

| Seletor                           | Dado                    | Observação                                          |
| --------------------------------- | ----------------------- | --------------------------------------------------- |
| `div.wrap-horarios div.row > div` | Coluna das categorias   |                                                     |
| `... h4`                          | Categoria linha         |                                                     |
| `... > div li > a`                | Url, código, nome linha | o código e nome estão no formato `{códgo} - {nome}` |

## /horarios/{linha}

Tipo do arquivo: HTML

| Seletor                                 | Dado                           | Observação                          |
| --------------------------------------- | ------------------------------ | ----------------------------------- |
| `(div.row.content-horarios)  h3 strong` | Código linha                   |                                     |
| `... h3 span`                           | Nome linha                     |                                     |
| `... div.col-lg-3:has(b) :is(b, span)`  | Categoria, modficacao, tarifas | Fluxo dado, valor, dado, valor ,... |
| `div#wrapAlertas > div`                 | Alertas linha                  | Atributo alert-\* diz o tipo        |
