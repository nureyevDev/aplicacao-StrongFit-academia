def listar_alunos_disponiveis(conexao):
    return conexao.execute(
        """
        SELECT
            a.id,
            a.nome,
            a.cpf
        FROM aluno a
        WHERE a.situacao != 'inativo'
          AND NOT EXISTS (
                SELECT 1
                FROM matricula m
                WHERE m.aluno_id = a.id
                  AND m.situacao IN (
                      'ativa',
                      'congelada'
                  )
          )
        ORDER BY a.nome COLLATE NOCASE
        """
    ).fetchall()


def listar_planos_ativos(conexao):
    return conexao.execute(
        """
        SELECT
            id,
            nome,
            duracao_meses,
            valor
        FROM plano
        WHERE ativo = 1
        ORDER BY nome COLLATE NOCASE
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


def buscar_matricula_aberta_do_aluno(
    conexao,
    aluno_id,
):
    return conexao.execute(
        """
        SELECT
            id,
            aluno_id,
            plano_id,
            data_inicio,
            data_vencimento,
            valor_contratado,
            situacao
        FROM matricula
        WHERE aluno_id = ?
          AND situacao IN (
              'ativa',
              'congelada'
          )
        LIMIT 1
        """,
        (aluno_id,),
    ).fetchone()


def inserir_matricula(
    conexao,
    aluno_id,
    plano_id,
    data_inicio,
    data_vencimento,
    valor_contratado,
):
    cursor = conexao.execute(
        """
        INSERT INTO matricula (
            aluno_id,
            plano_id,
            data_inicio,
            data_vencimento,
            valor_contratado,
            situacao
        )
        VALUES (?, ?, ?, ?, ?, 'ativa')
        """,
        (
            aluno_id,
            plano_id,
            data_inicio,
            data_vencimento,
            valor_contratado,
        ),
    )

    return cursor.lastrowid


def listar_matriculas(
    conexao,
    pesquisa="",
    situacao=None,
):
    termo = f"%{pesquisa.strip()}%"

    sql = """
        SELECT
            m.id,
            a.nome AS aluno,
            a.cpf,
            p.nome AS plano,
            m.data_inicio,
            m.data_vencimento,
            m.valor_contratado,
            m.situacao
        FROM matricula m
        JOIN aluno a
            ON a.id = m.aluno_id
        JOIN plano p
            ON p.id = m.plano_id
        WHERE (
            a.nome LIKE ? COLLATE NOCASE
            OR p.nome LIKE ? COLLATE NOCASE
        )
    """

    parametros = [
        termo,
        termo,
    ]

    if situacao:
        sql += " AND m.situacao = ?"
        parametros.append(situacao)

    sql += """
        ORDER BY
            m.data_inicio DESC,
            a.nome COLLATE NOCASE
    """

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def encerrar_matricula(
    conexao,
    matricula_id,
):
    conexao.execute(
        """
        UPDATE matricula
        SET situacao = 'encerrada'
        WHERE id = ?
        """,
        (matricula_id,),
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