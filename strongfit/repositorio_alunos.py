def inserir_aluno(
    conexao,
    nome,
    cpf,
    data_nascimento,
    telefone,
    email,
    endereco,
    situacao,
):
    cursor = conexao.execute(
        """
        INSERT INTO aluno (
            nome,
            cpf,
            data_nascimento,
            telefone,
            email,
            endereco,
            situacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            cpf,
            data_nascimento,
            telefone,
            email,
            endereco,
            situacao,
        ),
    )

    return cursor.lastrowid


def atualizar_aluno(
    conexao,
    aluno_id,
    nome,
    cpf,
    data_nascimento,
    telefone,
    email,
    endereco,
    situacao,
):
    conexao.execute(
        """
        UPDATE aluno
        SET
            nome = ?,
            cpf = ?,
            data_nascimento = ?,
            telefone = ?,
            email = ?,
            endereco = ?,
            situacao = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            nome,
            cpf,
            data_nascimento,
            telefone,
            email,
            endereco,
            situacao,
            aluno_id,
        ),
    )


def obter_aluno(conexao, aluno_id):
    return conexao.execute(
        """
        SELECT
            id,
            nome,
            cpf,
            data_nascimento,
            telefone,
            email,
            endereco,
            situacao,
            criado_em,
            atualizado_em
        FROM aluno
        WHERE id = ?
        """,
        (aluno_id,),
    ).fetchone()


def buscar_aluno_por_cpf(
    conexao,
    cpf,
):
    return conexao.execute(
        """
        SELECT
            id,
            nome,
            cpf,
            data_nascimento,
            telefone,
            email,
            endereco,
            situacao
        FROM aluno
        WHERE cpf = ?
        """,
        (cpf,),
    ).fetchone()


def listar_alunos(
    conexao,
    pesquisa="",
    situacao=None,
):
    termo = f"%{pesquisa.strip()}%"

    sql = """
        SELECT
            a.id,
            a.nome,
            a.cpf,
            a.telefone,
            a.email,
            a.situacao,
            (
                SELECT m.data_vencimento
                FROM matricula m
                WHERE m.aluno_id = a.id
                  AND m.situacao IN (
                      'ativa',
                      'congelada'
                  )
                ORDER BY m.id DESC
                LIMIT 1
            ) AS proximo_vencimento
        FROM aluno a
        WHERE a.nome LIKE ? COLLATE NOCASE
    """

    parametros = [termo]

    if situacao:
        sql += " AND a.situacao = ?"
        parametros.append(situacao)

    sql += " ORDER BY a.nome COLLATE NOCASE"

    return conexao.execute(
        sql,
        parametros,
    ).fetchall()


def excluir_aluno(
    conexao,
    aluno_id,
):
    conexao.execute(
        """
        DELETE FROM aluno
        WHERE id = ?
        """,
        (aluno_id,),
    )


def contar_alunos_por_situacao(
    conexao,
):
    linhas = conexao.execute(
        """
        SELECT
            situacao,
            COUNT(*) AS quantidade
        FROM aluno
        GROUP BY situacao
        """
    ).fetchall()

    return {
        linha["situacao"]: linha["quantidade"]
        for linha in linhas
    }