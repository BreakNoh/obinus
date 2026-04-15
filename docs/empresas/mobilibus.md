# API Mobilibus

- [x] implementada

**Endpoint API** \
https://mobilibus.com/api

## Detalhamento

**Requisição Lista Linhas** (json) \
/routes \
?project_id={{ID_PROJETO}} \
&v={{VERSAO}} \

_Retorno linhas_ \

```ts, json
[
    {
        routeId: number,
        agencyId: number,
        shortName: string, // codigo da rota
        longName: string, // nome da rota
        desc: string, // detalhe sobre a rota
        type: number,
        color: string,
        textColor: string,
        price: number,
    },
];
```

**Listas Horários de linha** \
/timetable \
?project_id={{ID_PROJETO}}\
&route_id={{ID_ROTA}} \
&v={{VERSAO}} \

_Retorno horários_ \

```ts, json
[
    {
        routeId: number,
        shortName: string, // codigo da linha
        longName: string, // nome da linha
        desc: string, // detalhe da linha
        type: number,
        color: string,
        textColor: string,
        ac: boolean,
        price: number | null,
        timetable: {
            // horarios
            directions: [
                {
                    directionId: number,
                    desc: string, // sentido
                    services: [
                        {
                            serviceId: number,
                            desc: string, // dia
                            days: [boolean],
                            departures: [
                                {
                                    dep: string, // hora saida
                                    arr: string, // hora chegada
                                    wa: number,
                                    seq: number,
                                },
                            ],
                        },
                    ],
                },
            ],
            trips: [
                {
                    tripId: number,
                    tripDesc: string,
                    shortName: string | null,
                    directionId: number,
                    seq: number,
                },
            ],
        },
    },
];
```
