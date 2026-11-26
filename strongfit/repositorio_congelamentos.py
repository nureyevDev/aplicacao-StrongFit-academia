def listar_matriculas_disponiveis(
    conexao,
):
    return conexao.execute(
        """
        SELECT
            m.id,
            m.aluno_id,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano,
            m.data_inicio,
            m.data_vencimento
        FROM matricula m
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE m.situacao = 'ativa'
          AND NOT EXISTS (
                SELECT 1
                FROM congelamento c
                WHERE c.matricula_id = m.id
                  AND c.data_fim_real IS NULL
          )
        ORDER BY a.nome COLLATE NOCASE
        """
    ).fetchall()


def obter_matricula(
    conexao,
    matricula_id,
):
    return conexao.execute(
        """
        SELECT
            m.id,
            m.aluno_id,
            m.plano_id,
            m.data_inicio,
            m.data_vencimento,
            m.valor_contratado,
            m.situacao,
            a.nome AS aluno,
            a.situacao AS situacao_aluno,
            p.nome AS plano
        FROM matricula m
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE m.id = ?
        """,
        (matricula_id,),
    ).fetchone()


def buscar_congelamento_aberto(
    conexao,
    matricula_id,
):
    return conexao.execute(
        """
        SELECT
            id,
            matricula_id,
            data_inicio,
            data_fim_prevista,
            data_fim_real,
            motivo,
            criado_em
        FROM congelamento
        WHERE matricula_id = ?
          AND data_fim_real IS NULL
        LIMIT 1
        """,
        (matricula_id,),
    ).fetchone()


def obter_congelamento(
    conexao,
    congelamento_id,
):
    return conexao.execute(
        """
        SELECT
            c.id,
            c.matricula_id,
            c.data_inicio,
            c.data_fim_prevista,
            c.data_fim_real,
            c.motivo,
            c.criado_em,
            m.aluno_id,
            m.situacao AS situacao_matricula,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano
        FROM congelamento c
        JOIN matricula m
            ON m.id = c.matricula_id
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE c.id = ?
        """,
        (congelamento_id,),
    ).fetchone()


def inserir_congelamento(
    conexao,
    matricula_id,
    data_inicio,
    data_fim_prevista,
    motivo,
):
    cursor = conexao.execute(
        """
        INSERT INTO congelamento (
            matricula_id,
            data_inicio,
            data_fim_prevista,
            motivo
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            matricula_id,
            data_inicio,
            data_fim_prevista,
            motivo,
        ),
    )

    return cursor.lastrowid


def encerrar_congelamento(
    conexao,
    congelamento_id,
    data_fim_real,
):
    conexao.execute(
        """
        UPDATE congelamento
        SET data_fim_real = ?
        WHERE id = ?
          AND data_fim_real IS NULL
        """,
        (
            data_fim_real,
            congelamento_id,
        ),
    )


def atualizar_situacao_matricula(
    conexao,
    matricula_id,
    situacao,
):
    conexao.execute(
        """
        UPDATE matricula
        SET situacao = ?
        WHERE id = ?
        """,
        (
            situacao,
            matricula_id,
        ),
    )


def atualizar_situacao_aluno(
    conexao,
    aluno_id,
    situacao,
):
    conexao.execute(
        """
        UPDATE aluno
        SET
            situacao = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            situacao,
            aluno_id,
        ),
    )


def listar_congelamentos(
    conexao,
    pesquisa="",
    somente_abertos=False,
):
    termo = f"%{pesquisa.strip()}%"

    sql = """
        SELECT
            c.id,
            c.matricula_id,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano,
            c.data_inicio,
            c.data_fim_prevista,
            c.data_fim_real,
            c.motivo,
            CASE
                WHEN c.data_fim_real IS NULL
                THEN 'aberto'
                ELSE 'encerrado'
            END AS situacao
        FROM congelamento c
        JOIN matricula m
            ON m.id = c.matricula_id
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE (
            a.nome LIKE ? COLLATE NOCASE
            OR a.cpf LIKE ?
            OR p.nome LIKE ? COLLATE NOCASE
            OR c.motivo LIKE ? COLLATE NOCASE
        )
    """

    parametros = [
        termo,
        termo,
        termo,
        termo,
    ]

    if somente_abertos:
        sql += " AND c.data_fim_real IS NULL"

    sql += """
        ORDER BY
            CASE
                WHEN c.data_fim_real IS NULL
                THEN 0
                ELSE 1
            END,
            c.data_inicio DESC,
            a.nome COLLATE NOCASE
    """

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()