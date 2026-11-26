import sqlite3
from datetime import date

from strongfit import repositorio_congelamentos as repo
from strongfit.erros import RegraNegocioErro


MOTIVOS_PADRAO = {
    "viagem",
    "atestado médico",
    "outros",
}


def normalizar_texto(valor):
    return " ".join(
        (valor or "").split()
    )


def registrar_congelamento(
    conexao,
    matricula_id,
    data_inicio,
    data_fim_prevista,
    motivo,
):
    if matricula_id is None:
        raise RegraNegocioErro(
            "Selecione uma matrícula ativa."
        )

    matricula = repo.obter_matricula(
        conexao,
        matricula_id,
    )

    if matricula is None:
        raise RegraNegocioErro(
            "A matrícula selecionada não existe."
        )

    if matricula["situacao"] != "ativa":
        raise RegraNegocioErro(
            "Somente matrículas ativas podem ser congeladas."
        )

    congelamento_aberto = (
        repo.buscar_congelamento_aberto(
            conexao,
            matricula_id,
        )
    )

    if congelamento_aberto is not None:
        raise RegraNegocioErro(
            "Esta matrícula já possui um congelamento aberto."
        )

    motivo = normalizar_texto(motivo)

    if not motivo:
        raise RegraNegocioErro(
            "Informe o motivo do congelamento."
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

    if data_fim_prevista:
        if not isinstance(
            data_fim_prevista,
            date,
        ):
            try:
                data_fim_prevista = (
                    date.fromisoformat(
                        str(data_fim_prevista)
                    )
                )
            except ValueError as erro:
                raise RegraNegocioErro(
                    "Informe uma previsão de retorno válida."
                ) from erro

        if data_fim_prevista < data_inicio:
            raise RegraNegocioErro(
                "A previsão de retorno não pode ser "
                "anterior ao início do congelamento."
            )

        fim_previsto = (
            data_fim_prevista.isoformat()
        )

    else:
        fim_previsto = None

    try:
        with conexao:
            congelamento_id = (
                repo.inserir_congelamento(
                    conexao,
                    matricula_id,
                    data_inicio.isoformat(),
                    fim_previsto,
                    motivo,
                )
            )

            repo.atualizar_situacao_matricula(
                conexao,
                matricula_id,
                "congelada",
            )

            repo.atualizar_situacao_aluno(
                conexao,
                matricula["aluno_id"],
                "congelado",
            )

            return congelamento_id

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível registrar o congelamento."
        ) from erro


def encerrar_congelamento(
    conexao,
    congelamento_id,
    data_fim_real=None,
):
    congelamento = repo.obter_congelamento(
        conexao,
        congelamento_id,
    )

    if congelamento is None:
        raise RegraNegocioErro(
            "O congelamento selecionado não existe."
        )

    if congelamento["data_fim_real"]:
        raise RegraNegocioErro(
            "Este congelamento já foi encerrado."
        )

    data_fim_real = (
        data_fim_real
        or date.today()
    )

    if not isinstance(
        data_fim_real,
        date,
    ):
        try:
            data_fim_real = date.fromisoformat(
                str(data_fim_real)
            )
        except ValueError as erro:
            raise RegraNegocioErro(
                "Informe uma data final válida."
            ) from erro

    data_inicio = date.fromisoformat(
        congelamento["data_inicio"]
    )

    if data_fim_real < data_inicio:
        raise RegraNegocioErro(
            "A data final não pode ser anterior "
            "ao início do congelamento."
        )

    with conexao:
        repo.encerrar_congelamento(
            conexao,
            congelamento_id,
            data_fim_real.isoformat(),
        )

        repo.atualizar_situacao_matricula(
            conexao,
            congelamento["matricula_id"],
            "ativa",
        )

        repo.atualizar_situacao_aluno(
            conexao,
            congelamento["aluno_id"],
            "ativo",
        )