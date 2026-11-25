def inserir_mensalidade(
    conexao,
    matricula_id,
    competencia,
    data_vencimento,
    valor,
):
    cursor = conexao.execute(
        """
        INSERT INTO mensalidade (
            matricula_id,
            competencia,
            data_vencimento,
            valor,
            situacao
        )
        VALUES (?, ?, ?, ?, 'pendente')
        """,
        (
            matricula_id,
            competencia,
            data_vencimento,
            valor,
        ),
    )

    return cursor.lastrowid


def obter_mensalidade(
    conexao,
    mensalidade_id,
):
    return conexao.execute(
        """
        SELECT
            men.id,
            men.matricula_id,
            men.competencia,
            men.data_vencimento,
            men.valor,
            men.situacao,
            mat.aluno_id,
            mat.plano_id,
            mat.situacao AS situacao_matricula,
            alu.nome AS aluno,
            alu.cpf,
            alu.situacao AS situacao_aluno,
            pla.nome AS plano
        FROM mensalidade men
        JOIN matricula mat
            ON mat.id = men.matricula_id
        JOIN aluno alu
            ON alu.id = mat.aluno_id
        JOIN plano pla
            ON pla.id = mat.plano_id
        WHERE men.id = ?
        """,
        (mensalidade_id,),
    ).fetchone()


def buscar_mensalidade_da_matricula(
    conexao,
    matricula_id,
    competencia,
):
    return conexao.execute(
        """
        SELECT
            id,
            matricula_id,
            competencia,
            data_vencimento,
            valor,
            situacao
        FROM mensalidade
        WHERE matricula_id = ?
          AND competencia = ?
        """,
        (
            matricula_id,
            competencia,
        ),
    ).fetchone()


def listar_mensalidades(
    conexao,
    pesquisa="",
    situacao=None,
):
    termo = f"%{pesquisa.strip()}%"

    sql = """
        SELECT
            men.id,
            alu.nome AS aluno,
            alu.cpf,
            pla.nome AS plano,
            men.competencia,
            men.data_vencimento,
            men.valor,
            men.situacao,
            (
                SELECT pag.data_pagamento
                FROM pagamento pag
                WHERE pag.mensalidade_id = men.id
                ORDER BY pag.id DESC
                LIMIT 1
            ) AS data_pagamento
        FROM mensalidade men
        JOIN matricula mat
            ON mat.id = men.matricula_id
        JOIN aluno alu
            ON alu.id = mat.aluno_id
        JOIN plano pla
            ON pla.id = mat.plano_id
        WHERE (
            alu.nome LIKE ? COLLATE NOCASE
            OR pla.nome LIKE ? COLLATE NOCASE
            OR men.competencia LIKE ?
        )
    """

    parametros = [
        termo,
        termo,
        termo,
    ]

    if situacao:
        sql += " AND men.situacao = ?"
        parametros.append(situacao)

    sql += """
        ORDER BY
            men.data_vencimento DESC,
            alu.nome COLLATE NOCASE
    """

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def inserir_pagamento(
    conexao,
    mensalidade_id,
    usuario_id,
    data_pagamento,
    valor,
    forma_pagamento,
    observacao,
):
    cursor = conexao.execute(
        """
        INSERT INTO pagamento (
            mensalidade_id,
            usuario_id,
            data_pagamento,
            valor,
            forma_pagamento,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            mensalidade_id,
            usuario_id,
            data_pagamento,
            valor,
            forma_pagamento,
            observacao,
        ),
    )

    return cursor.lastrowid


def buscar_pagamento_da_mensalidade(
    conexao,
    mensalidade_id,
):
    return conexao.execute(
        """
        SELECT
            id,
            mensalidade_id,
            data_pagamento,
            valor,
            forma_pagamento,
            observacao
        FROM pagamento
        WHERE mensalidade_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (mensalidade_id,),
    ).fetchone()


def listar_pagamentos(
    conexao,
    pesquisa="",
):
    termo = f"%{pesquisa.strip()}%"

    return conexao.execute(
        """
        SELECT
            pag.id,
            alu.nome AS aluno,
            alu.cpf,
            pla.nome AS plano,
            men.competencia,
            pag.data_pagamento,
            pag.valor,
            pag.forma_pagamento,
            pag.observacao
        FROM pagamento pag
        JOIN mensalidade men
            ON men.id = pag.mensalidade_id
        JOIN matricula mat
            ON mat.id = men.matricula_id
        JOIN aluno alu
            ON alu.id = mat.aluno_id
        JOIN plano pla
            ON pla.id = mat.plano_id
        WHERE (
            alu.nome LIKE ? COLLATE NOCASE
            OR pla.nome LIKE ? COLLATE NOCASE
            OR pag.forma_pagamento LIKE ? COLLATE NOCASE
        )
        ORDER BY pag.data_pagamento DESC
        """,
        (
            termo,
            termo,
            termo,
        ),
    ).fetchall()


def atualizar_situacao_mensalidade(
    conexao,
    mensalidade_id,
    situacao,
):
    conexao.execute(
        """
        UPDATE mensalidade
        SET situacao = ?
        WHERE id = ?
        """,
        (
            situacao,
            mensalidade_id,
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


def contar_mensalidades_por_situacao(
    conexao,
):
    linhas = conexao.execute(
        """
        SELECT
            situacao,
            COUNT(*) AS quantidade
        FROM mensalidade
        GROUP BY situacao
        """
    ).fetchall()

    return {
        linha["situacao"]: linha["quantidade"]
        for linha in linhas
    }


def total_recebido(
    conexao,
):
    linha = conexao.execute(
        """
        SELECT
            COALESCE(
                SUM(valor),
                0
            ) AS total
        FROM pagamento
        """
    ).fetchone()

    return linha["total"]