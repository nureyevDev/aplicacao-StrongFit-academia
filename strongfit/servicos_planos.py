import sqlite3
from decimal import Decimal, InvalidOperation

from strongfit import repositorio_planos as repo
from strongfit.erros import RegraNegocioErro


def normalizar_nome(valor):
    return " ".join(
        (valor or "").split()
    )


def normalizar_valor(valor):
    try:
        numero = Decimal(
            str(valor).replace(",", ".")
        )

    except (InvalidOperation, ValueError):
        raise RegraNegocioErro(
            "Informe um valor válido para o plano."
        )

    if numero < 0:
        raise RegraNegocioErro(
            "O valor do plano não pode ser negativo."
        )

    return numero.quantize(Decimal("0.01"))


def validar_dados(
    nome,
    duracao_meses,
    valor,
    ativo,
):
    nome = normalizar_nome(nome)

    if not nome:
        raise RegraNegocioErro(
            "Informe o nome do plano."
        )

    try:
        duracao_meses = int(
            duracao_meses
        )

    except (TypeError, ValueError):
        raise RegraNegocioErro(
            "Informe uma duração válida."
        )

    if duracao_meses < 1:
        raise RegraNegocioErro(
            "A duração deve ser de pelo menos 1 mês."
        )

    if duracao_meses > 120:
        raise RegraNegocioErro(
            "A duração não pode ultrapassar 120 meses."
        )

    valor = normalizar_valor(valor)

    return (
        nome,
        duracao_meses,
        float(valor),
        bool(ativo),
    )


def cadastrar_plano(
    conexao,
    nome,
    duracao_meses,
    valor,
    ativo=True,
):
    dados = validar_dados(
        nome,
        duracao_meses,
        valor,
        ativo,
    )

    existente = repo.buscar_plano_por_nome(
        conexao,
        dados[0],
    )

    if existente is not None:
        raise RegraNegocioErro(
            f"Já existe o plano {existente['nome']}."
        )

    try:
        with conexao:
            return repo.inserir_plano(
                conexao,
                *dados,
            )

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível cadastrar o plano."
        ) from erro


def editar_plano(
    conexao,
    plano_id,
    nome,
    duracao_meses,
    valor,
    ativo,
):
    plano = repo.obter_plano(
        conexao,
        plano_id,
    )

    if plano is None:
        raise RegraNegocioErro(
            "O plano selecionado não existe."
        )

    dados = validar_dados(
        nome,
        duracao_meses,
        valor,
        ativo,
    )

    existente = repo.buscar_plano_por_nome(
        conexao,
        dados[0],
    )

    if (
        existente is not None
        and existente["id"] != plano_id
    ):
        raise RegraNegocioErro(
            f"Já existe o plano {existente['nome']}."
        )

    try:
        with conexao:
            repo.atualizar_plano(
                conexao,
                plano_id,
                *dados,
            )

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível atualizar o plano."
        ) from erro


def definir_plano_ativo(
    conexao,
    plano_id,
    ativo,
):
    plano = repo.obter_plano(
        conexao,
        plano_id,
    )

    if plano is None:
        raise RegraNegocioErro(
            "O plano selecionado não existe."
        )

    with conexao:
        repo.alterar_situacao_plano(
            conexao,
            plano_id,
            ativo,
        )
        
def excluir_plano(
    conexao,
    plano_id,
):
    plano = repo.obter_plano(
        conexao,
        plano_id,
    )

    if plano is None:
        raise RegraNegocioErro(
            "O plano selecionado não existe."
        )

    total_matriculas = (
        repo.contar_matriculas_do_plano(
            conexao,
            plano_id,
        )
    )

    if total_matriculas > 0:
        raise RegraNegocioErro(
            "Este plano possui matrículas registradas "
            "e não pode ser excluído. Inative o plano."
        )

    try:
        with conexao:
            repo.excluir_plano(
                conexao,
                plano_id,
            )

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível excluir o plano. "
            "Verifique se ele possui dados vinculados."
        ) from erro