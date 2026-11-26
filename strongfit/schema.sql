PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL
        CHECK (perfil IN ('recepcao', 'gerente', 'proprietario')),
    ativo INTEGER NOT NULL DEFAULT 1
        CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS aluno (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE,
    data_nascimento TEXT,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    situacao TEXT NOT NULL DEFAULT 'ativo'
        CHECK (
            situacao IN (
                'ativo',
                'inadimplente',
                'congelado',
                'inativo'
            )
        ),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS plano (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    duracao_meses INTEGER NOT NULL
        CHECK (duracao_meses > 0),
    valor NUMERIC NOT NULL
        CHECK (valor >= 0),
    ativo INTEGER NOT NULL DEFAULT 1
        CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS matricula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    plano_id INTEGER NOT NULL,
    data_inicio TEXT NOT NULL,
    data_vencimento TEXT NOT NULL,
    valor_contratado NUMERIC NOT NULL
        CHECK (valor_contratado >= 0),
    situacao TEXT NOT NULL DEFAULT 'ativa'
        CHECK (
            situacao IN (
                'ativa',
                'vencida',
                'congelada',
                'encerrada'
            )
        ),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (aluno_id)
        REFERENCES aluno(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (plano_id)
        REFERENCES plano(id)
        ON DELETE RESTRICT
);


CREATE UNIQUE INDEX IF NOT EXISTS
idx_matricula_ativa_por_aluno
ON matricula(aluno_id)
WHERE situacao IN ('ativa', 'congelada');


CREATE TABLE IF NOT EXISTS mensalidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula_id INTEGER NOT NULL,
    competencia TEXT NOT NULL,
    data_vencimento TEXT NOT NULL,
    valor NUMERIC NOT NULL
        CHECK (valor >= 0),
    situacao TEXT NOT NULL DEFAULT 'pendente'
        CHECK (
            situacao IN (
                'pendente',
                'paga',
                'atrasada',
                'cancelada'
            )
        ),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (matricula_id)
        REFERENCES matricula(id)
        ON DELETE RESTRICT,

    UNIQUE (matricula_id, competencia)
);


CREATE TABLE IF NOT EXISTS pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mensalidade_id INTEGER NOT NULL,
    usuario_id INTEGER,
    data_pagamento TEXT NOT NULL,
    valor NUMERIC NOT NULL
        CHECK (valor > 0),
    forma_pagamento TEXT NOT NULL,
    observacao TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (mensalidade_id)
        REFERENCES mensalidade(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS
idx_mensalidade_vencimento
ON mensalidade(data_vencimento);

CREATE INDEX IF NOT EXISTS
idx_mensalidade_situacao
ON mensalidade(situacao);

CREATE INDEX IF NOT EXISTS
idx_pagamento_data
ON pagamento(data_pagamento);

CREATE TABLE IF NOT EXISTS congelamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula_id INTEGER NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim_prevista TEXT,
    data_fim_real TEXT,
    motivo TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (matricula_id)
        REFERENCES matricula(id)
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS
idx_congelamento_aberto_por_matricula
ON congelamento(matricula_id)
WHERE data_fim_real IS NULL;

CREATE TABLE IF NOT EXISTS observacao_aluno (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    usuario_id INTEGER,
    texto TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (aluno_id)
        REFERENCES aluno(id)
        ON DELETE CASCADE,

    FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS configuracao (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_aluno_nome
ON aluno(nome);


CREATE INDEX IF NOT EXISTS idx_aluno_situacao
ON aluno(situacao);


CREATE INDEX IF NOT EXISTS idx_mensalidade_vencimento
ON mensalidade(data_vencimento);


CREATE INDEX IF NOT EXISTS idx_mensalidade_situacao
ON mensalidade(situacao);


CREATE INDEX IF NOT EXISTS idx_pagamento_data
ON pagamento(data_pagamento);


CREATE INDEX IF NOT EXISTS idx_observacao_aluno
ON observacao_aluno(aluno_id, criado_em);