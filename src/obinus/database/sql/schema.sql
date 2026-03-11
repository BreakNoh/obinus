PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS linhas(
	id INTEGER PRIMARY KEY AUTOINCREMENT,

	empresa TEXT NOT NULL,

	codigo TEXT NOT NULL,
	nome TEXT NOT NULL,
	detalhe TEXT ,
	url TEXT ,

	eh_executivo BOOLEAN DEFAULT 0

	-- FOREIGN KEY(id_empresa) REFERENCES empresas(id)
);

CREATE TABLE IF NOT EXISTS horarios(
	id INTEGER PRIMARY KEY AUTOINCREMENT,

	empresa TEXT NOT NULL,
	linha TEXT NOT NULL,
	
	dia TEXT NOT NULL,
	sentido TEXT,
	hora TEXT NOT NULL

	-- FOREIGN KEY(id_empresa) REFERENCES empresas(id),
	-- FOREIGN KEY(id_linha) REFERENCES linhas(id)
);
