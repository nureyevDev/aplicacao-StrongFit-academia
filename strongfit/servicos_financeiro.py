import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from strongfit import repositorio_financeiro as repo
from strongfit.erros import RegraNegocioErro


FORMAS_PAGAMENTO = {
    "pix",
    "dinheiro",
}


def gerar_competencia(
    data_vencimento,
):
    if isinstance(
        data_vencimento,
        str,
    ):
        data_vencimento = date.fromisoformat(
            data_vencimento
        )

    return data_vencimento.strftime(
        "%Y-%m"
    )


def criar_mensalidade_inicial(
    conexao,
    matricula_id,
    data_vencimento,
    valor,
):
    competencia = gerar_competencia(
        data_vencimento
    )

    existente = (
        repo.buscar_mensalidade_da_matricula(
            conexao,
            matricula_id,
            competencia,
        )
    )

    if existente is not None:
        return existente["id"]

    return repo.inserir_mensalidade(
        conexao,
        matricula_id,
        competencia,
        data_vencimento,
        valor,
    )


def normalizar_valor(valor):
    try:
        numero = Decimal(
            str(valor).replace(",", ".")
        ).quantize(
            Decimal("0.01")
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as erro:
        raise RegraNegocioErro(
            "Informe um valor válido."
        ) from erro

    if numero <= 0:
        raise RegraNegocioErro(
            "O valor do pagamento deve ser maior que zero."
        )

    return numero


def registrar_pagamento(
    conexao,
    mensalidade_id,
    valor,
    forma_pagamento,
    observacao="",
    usuario_id=None,
    momento=None,
):
    mensalidade = repo.obter_mensalidade(
        conexao,
        mensalidade_id,
    )

    if mensalidade is None:
        raise RegraNegocioErro(
            "A mensalidade selecionada não existe."
        )

    if mensalidade["situacao"] == "cancelada":
        raise RegraNegocioErro(
            "Não é possível pagar uma mensalidade cancelada."
        )

    if mensalidade["situacao"] == "paga":
        raise RegraNegocioErro(
            "Esta mensalidade já foi paga."
        )

    pagamento_existente = (
        repo.buscar_pagamento_da_mensalidade(
            conexao,
            mensalidade_id,
        )
    )

    if pagamento_existente is not None:
        raise RegraNegocioErro(
            "Já existe um pagamento para esta mensalidade."
        )

    forma = (
        forma_pagamento
        or ""
    ).strip().lower()

    if forma not in FORMAS_PAGAMENTO:
        raise RegraNegocioErro(
            "Selecione Pix ou Dinheiro."
        )

    valor_pagamento = normalizar_valor(
        valor
    )

    valor_mensalidade = Decimal(
        str(mensalidade["valor"])
    ).quantize(
        Decimal("0.01")
    )

    if valor_pagamento != valor_mensalidade:
        raise RegraNegocioErro(
            "O valor pago deve ser igual ao valor "
            "da mensalidade."
        )

    data_pagamento = momento

    if data_pagamento is None:
        data_pagamento = datetime.now()

    if isinstance(
        data_pagamento,
        datetime,
    ):
        data_pagamento = (
            data_pagamento.isoformat(
                sep=" ",
                timespec="seconds",
            )
        )

    try:
        with conexao:
            pagamento_id = repo.inserir_pagamento(
                conexao,
                mensalidade_id,
                usuario_id,
                data_pagamento,
                float(valor_pagamento),
                forma,
                (observacao or "").strip(),
            )

            repo.atualizar_situacao_mensalidade(
                conexao,
                mensalidade_id,
                "paga",
            )

            repo.atualizar_situacao_aluno(
                conexao,
                mensalidade["aluno_id"],
                "ativo",
            )

            return pagamento_id

    except sqlite3.IntegrityError as erro:
        raise RegraNegocioErro(
            "Não foi possível registrar o pagamento."
        ) from erro