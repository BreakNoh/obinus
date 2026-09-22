![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![uv](https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white)

# obinus

**obinus** é uma coleção de raspadores de linhas de ônibus do território de **Santa Catarina** escrita em **Python**

## Dependências

- **Python** v3.14 ou posteriores
- **uv** v0.11.19 ou posteriores
- **git**

## Instalação

1. clone o repositório do projeto

```sh
git clone https://github.com/breaknoh/obinus
```

2. navegue para o diretório

```sh
cd obinus
```

3. instale as dependências

```sh
uv sync
```

## Uso

O uso dos raspadores é feito através de 2 comandos: `uv run empresa` e `uv run regiao`.  
Ao iniciar a raspagem será apresentado uma barra de progresso da raspagem e ao finalizar o processo os dados serão salvos no diretório `output/` na raiz do projeto. Caso já exista dados sobre a empresa **os dados antigos serão sobreescritos**.

```bash
uv run empresa
```

Usado para raspar dados de uma empresa específica. Pode ser usado passando o nome da empresa direto no comando (`uv run empresa <empresa>`) ou somente o comando para uma escolha interativa (`uv run empresa`)

```bash
uv run regiao
```

Usado para raspar dados de todas as empresas de uma região. Pode ser usado passando o nome da região direto no comando (`uv run regiao <regiao>`) ou somente o comando para uma escolha interativa (`uv run regiao`)

_obs:_ caso o nome da região ou empresa passado como parâmetro não corresponder a nenhuma reconhecida, o modo interativo será usado.

> Mais informações sobre os identificadores de empresas e regiões em [/docs/empresas.md](./docs/empresas.md)

## Capacidades

- Extrair **linhas**
- Extrair **sentidos**
- Extrair **horários**

**Capacidades planejadas:**

- [ ] Extrair **itinerários**
- [ ] Extrair **tarifas**
- [ ] Extrair **avisos**
- [ ] Mais métodos de exportação

## Formato dos dados

Os dados raspados são retornados no formato JSON no diretório `output`. No diretório, os dados de cada empresa são salvos em diretórios nomeados com o identificador da empresa (`output/<empresa>/`).  
No diretório da empresa são guardados os dados de cada linha em arquivos JSON separados nomeados de acordo com o slug da linha.
Também é salvo o arquivo `_self.json`, nele são guardados os dados da linha.

### `<linha>.json`

```ts
{
    "nome": <string>,
    "codigo": <string | null>,
    "detalhe": <string | null>,
    "tipo": <string>,
    "slug": <string>,
    "servicos": {
        <string> : {
            "sentido": <string>,
            "horarios": {
                "hora": <string>,
                "obs": {
                    "tipo": <string>,
                    "valor": <string>
                }[]
            }
        }[]
    }
}

```

_obs:_ as chaves do campo servicos da linha são strings númericas baseadas em bit flags, de acordo com o esquema abaixo:

| Bit | Dia da Semana |
| --- | ------------- |
| 0   | Domingo       |
| 1   | Segunda       |
| 2   | Terça         |
| 3   | Quarta        |
| 4   | Quinta        |
| 5   | Sexta         |
| 6   | Sábado        |

_Exemplo:_ dias uteis seriam `0b0111110` que em decimal seria `62`, então a chave dos serviços desses dias seria `"62"`.

### `_self.json`

```ts
{
    "nome": <string>,
    "fonte": <string>,
    "regioes": <string[]>,
    "slug": <string>,
    "linhas": {
        "nome_linha": <string>,
        "codigo_linha": <string | null>,
        "nome_empresa": <string>,
        "slug": <string>
    }[]
}

```

## Licença

Este projeto está licenciado sob a licença GNU GPLv3. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Aviso sobre os dados

Os dados raspados por este projeto pertencem às respectivas empresas de ônibus e fontes
originais. Este projeto não reivindica propriedade sobre esses dados e seu uso deve respeitar
os termos de uso dos sites de origem. As informações podem mudar sem aviso prévio e não há
garantia de precisão ou atualização.
