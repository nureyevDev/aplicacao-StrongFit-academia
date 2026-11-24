import calendar
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation

from strongfit import repositorio_matriculas as repo
from strongfit.erros import RegraNegocioErro


def adicionar_meses(
    data_inicial,
    quantidade_meses,
):
    mes_base = (
        data_inicial.month
        - 1
        + quantidade_meses
    )

    ano = (
        data_inicial.year
        + mes_base // 12
    )

    mes = mes_base % 12 + 1

    ultimo_dia = calendar.monthrange(
        ano,
        mes,
    )[1]

    dia = min(
        data_inicial.day,
        ultimo_dia,
    )

    return date(
        ano,
        mes,
        dia,
    )


def criar_matricula(
    conexao,
    aluno_id,
    plano_id,
    data_inicio,
    valor_contratado=None,
):
    if aluno_id is None:
        raise RegraNegocioErro(
            "Selecione um aluno."
        )

    if plano_id is None:
        raise RegraNegocioErro(
            "Selecione um plano."
        )

    plano = conexao.execute(
        """
        SELECT
            id,
            nome,
            duracao_meses,
            valor,
            ativo
        FROM plano
        WHERE id = ?
        """,
        (plano_id,),
    ).fetchone()

    if plano is None:
        raise RegraNegocioErro(
            "O plano selecionado não existe."
        )

    if not plano["ativo"]:
        raise RegraNegocioErro(
            "O plano selecionado está inativo."
        )

    aluno = conexao.execute(
        """
        SELECT id, nome, situacao
        FROM aluno
        WHERE id = ?
        """,
        (aluno_id,),
    ).fetchone()

    if aluno is None:
        raise RegraNegocioErro(
            "O aluno selecionado não existe."
        )

    if aluno["situacao"] == "inativo":
        raise RegraNegocioErro(
            "Não é possível matricular um aluno inativo."
        )

    existente = (
        repo.buscar_matricula_aberta_do_aluno(
            conexao,
            aluno_id,
        )
    )

    if existente is not None:
        raise RegraNegocioErro(
            "Este aluno já possui uma matrícula ativa "
            "ou congelada."
        )

    if not isinstance(
        data_inicio,
        date,
    ):
        try:
            data_inicio = date.fromisoformat(
                str(data_inicio)
            )
        except ValueError as erro:
            raise RegraNegocioErro(
                "Informe uma data inicial válida."
            ) from erro

    if valor_contratado is None:
        valor_contratado = plano["valor"]

    try:
        valor = Decimal(
            str(valor_contratado)
            .replace(",", ".")
        ).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as erro:
        raise RegraNegocioErro(
            "Informe um valor contratado válido."
        ) from erro

    if valor < 0:
        raise RegraNegocioErro(
            "O valor contratado não pode ser negativo."
        )

    vencimento = adicionar_meses(
        data_inicio,
        plano["duracao_meses"],
    )

    try:
        with conexao:
            matricula_id = repo.inserir_matricula(
                conexao,
                aluno_id,
                plano_id,
                data_inicio.isoformat(),
                vencimento.isoformat(),
                float(valor),
            )

            repo.atualizar_situacao_aluno(
                conexao,
                aluno_id,
                "ativo",
            )

            return matricula_id

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "O aluno já possui uma matrícula ativa "
            "ou os dados não puderam ser gravados."
        ) from erro


def encerrar_matricula(
    conexao,
    matricula_id,
):
    matricula = repo.obter_matricula(
        conexao,
        matricula_id,
    )

    if matricula is None:
        raise RegraNegocioErro(
            "A matrícula selecionada não existe."
        )

    if matricula["situacao"] == "encerrada":
        raise RegraNegocioErro(
            "A matrícula já está encerrada."
        )

    with conexao:
        repo.encerrar_matricula(
            conexao,
            matricula_id,
        )

        repo.atualizar_situacao_aluno(
            conexao,
            matricula["aluno_id"],
            "inativo",
        )