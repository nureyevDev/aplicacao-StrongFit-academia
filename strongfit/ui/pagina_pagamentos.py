from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_financeiro as repo
from strongfit import servicos_financeiro
from strongfit.erros import RegraNegocioErro


class PaginaPagamentos(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.mensalidade_selecionada_id = None

        self.montar_interface()
        self.atualizar_tudo()

    def montar_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(
            22,
            22,
            22,
            22,
        )
        layout_principal.setSpacing(14)

        titulo = QLabel(
            "Gestão financeira"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Consulte mensalidades e registre "
            "pagamentos dos alunos."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        self.abas = QTabWidget()

        self.abas.addTab(
            self.criar_aba_mensalidades(),
            "Mensalidades",
        )

        self.abas.addTab(
            self.criar_aba_historico(),
            "Histórico de pagamentos",
        )

        self.abas.currentChanged.connect(
            lambda _indice: self.atualizar_tudo()
        )

        layout_principal.addWidget(
            self.abas,
            1,
        )

        self.mensagem = QLabel(
            "Selecione uma mensalidade para registrar o pagamento."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)

        layout_principal.addWidget(
            self.mensagem
        )

    def criar_aba_mensalidades(self):
        aba = QWidget()

        layout = QHBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )
        layout.setSpacing(16)

        layout.addWidget(
            self.criar_formulario_pagamento(),
            2,
        )

        layout.addWidget(
            self.criar_lista_mensalidades(),
            4,
        )

        return aba

    def criar_formulario_pagamento(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        titulo = QLabel(
            "Registrar pagamento"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        layout.addWidget(titulo)

        self.rotulo_aluno = QLabel(
            "Nenhuma mensalidade selecionada"
        )
        self.rotulo_aluno.setObjectName(
            "destaque"
        )
        self.rotulo_aluno.setWordWrap(True)

        layout.addWidget(
            self.rotulo_aluno
        )

        formulario = QFormLayout()

        self.campo_valor = QDoubleSpinBox()
        self.campo_valor.setRange(
            0,
            999999.99,
        )
        self.campo_valor.setDecimals(2)
        self.campo_valor.setPrefix(
            "R$ "
        )

        self.combo_forma = QComboBox()
        self.combo_forma.addItem(
            "Selecione",
            None,
        )
        self.combo_forma.addItem(
            "Pix",
            "pix",
        )
        self.combo_forma.addItem(
            "Dinheiro",
            "dinheiro",
        )

        self.data_pagamento = QDateTimeEdit(
            QDateTime.currentDateTime()
        )
        self.data_pagamento.setCalendarPopup(
            True
        )
        self.data_pagamento.setDisplayFormat(
            "dd/MM/yyyy HH:mm"
        )

        self.campo_observacao = QTextEdit()
        self.campo_observacao.setPlaceholderText(
            "Observação opcional"
        )
        self.campo_observacao.setMaximumHeight(
            90
        )

        formulario.addRow(
            "Valor",
            self.campo_valor,
        )
        formulario.addRow(
            "Forma",
            self.combo_forma,
        )
        formulario.addRow(
            "Data",
            self.data_pagamento,
        )
        formulario.addRow(
            "Observação",
            self.campo_observacao,
        )

        layout.addLayout(formulario)

        self.botao_pagar = QPushButton(
            "Registrar pagamento"
        )
        self.botao_pagar.setObjectName(
            "botaoPrimario"
        )
        self.botao_pagar.setEnabled(False)

        self.botao_pagar.clicked.connect(
            self.registrar_pagamento
        )

        self.botao_limpar = QPushButton(
            "Limpar seleção"
        )
        self.botao_limpar.clicked.connect(
            self.limpar_selecao
        )

        botoes = QHBoxLayout()
        botoes.addWidget(
            self.botao_pagar
        )
        botoes.addWidget(
            self.botao_limpar
        )

        layout.addLayout(botoes)
        layout.addStretch()

        return frame

    def criar_lista_mensalidades(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        topo = QHBoxLayout()

        titulo = QLabel(
            "Mensalidades"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar aluno ou plano"
        )

        self.filtro_situacao = QComboBox()
        self.filtro_situacao.addItem(
            "Todas",
            None,
        )
        self.filtro_situacao.addItem(
            "Pendentes",
            "pendente",
        )
        self.filtro_situacao.addItem(
            "Pagas",
            "paga",
        )
        self.filtro_situacao.addItem(
            "Atrasadas",
            "atrasada",
        )
        self.filtro_situacao.addItem(
            "Canceladas",
            "cancelada",
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa
        )
        topo.addWidget(
            self.filtro_situacao
        )

        self.tabela_mensalidades = QTableWidget(
            0,
            8,
        )

        self.tabela_mensalidades.setHorizontalHeaderLabels(
            [
                "ID",
                "Aluno",
                "Plano",
                "Competência",
                "Vencimento",
                "Valor",
                "Situação",
                "Pagamento",
            ]
        )

        self.configurar_tabela(
            self.tabela_mensalidades
        )

        cabecalho = (
            self.tabela_mensalidades
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents,
        )
        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in range(2, 8):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        self.tabela_mensalidades.itemSelectionChanged.connect(
            self.selecionar_mensalidade
        )

        self.campo_pesquisa.textChanged.connect(
            self.atualizar_mensalidades
        )

        self.filtro_situacao.currentIndexChanged.connect(
            self.atualizar_mensalidades
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_mensalidades
        )

        return frame

    def criar_aba_historico(self):
        aba = QWidget()

        layout = QVBoxLayout(aba)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        topo = QHBoxLayout()

        titulo = QLabel(
            "Pagamentos realizados"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa_historico = QLineEdit()
        self.campo_pesquisa_historico.setPlaceholderText(
            "Pesquisar aluno, plano ou forma"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa_historico
        )

        self.tabela_pagamentos = QTableWidget(
            0,
            8,
        )

        self.tabela_pagamentos.setHorizontalHeaderLabels(
            [
                "ID",
                "Aluno",
                "Plano",
                "Competência",
                "Data",
                "Valor",
                "Forma",
                "Observação",
            ]
        )

        self.configurar_tabela(
            self.tabela_pagamentos
        )

        cabecalho = (
            self.tabela_pagamentos
            .horizontalHeader()
        )

        cabecalho.setSectionResizeMode(
            0,
            QHeaderView
            .ResizeMode
            .ResizeToContents,
        )
        cabecalho.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        cabecalho.setSectionResizeMode(
            7,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in range(2, 7):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        self.campo_pesquisa_historico.textChanged.connect(
            self.atualizar_historico
        )

        layout.addLayout(topo)
        layout.addWidget(
            self.tabela_pagamentos
        )

        return aba

    @staticmethod
    def configurar_tabela(tabela):
        tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )
        tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )
        tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )
        tabela.setAlternatingRowColors(
            True
        )
        tabela.verticalHeader().setVisible(
            False
        )

    def atualizar_mensalidades(self):
        linhas = repo.listar_mensalidades(
            self.conexao,
            self.campo_pesquisa.text(),
            self.filtro_situacao.currentData(),
        )

        self.tabela_mensalidades.setRowCount(
            len(linhas)
        )

        for linha, mensalidade in enumerate(
            linhas
        ):
            valores = [
                mensalidade["id"],
                mensalidade["aluno"],
                mensalidade["plano"],
                mensalidade["competencia"],
                self.formatar_data(
                    mensalidade["data_vencimento"]
                ),
                self.formatar_moeda(
                    mensalidade["valor"]
                ),
                mensalidade["situacao"].title(),
                (
                    self.formatar_data_hora(
                        mensalidade["data_pagamento"]
                    )
                    if mensalidade["data_pagamento"]
                    else ""
                ),
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna in (
                    0,
                    3,
                    4,
                    5,
                    6,
                    7,
                ):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabela_mensalidades.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela_mensalidades.clearSelection()
        self.limpar_selecao()

    def atualizar_historico(self):
        linhas = repo.listar_pagamentos(
            self.conexao,
            self.campo_pesquisa_historico.text(),
        )

        self.tabela_pagamentos.setRowCount(
            len(linhas)
        )

        for linha, pagamento in enumerate(
            linhas
        ):
            valores = [
                pagamento["id"],
                pagamento["aluno"],
                pagamento["plano"],
                pagamento["competencia"],
                self.formatar_data_hora(
                    pagamento["data_pagamento"]
                ),
                self.formatar_moeda(
                    pagamento["valor"]
                ),
                pagamento[
                    "forma_pagamento"
                ].title(),
                pagamento["observacao"] or "",
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela_pagamentos.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    ),
                )

    def selecionar_mensalidade(self):
        linha = (
            self.tabela_mensalidades
            .currentRow()
        )

        if linha < 0:
            return

        mensalidade_id = int(
            self.tabela_mensalidades.item(
                linha,
                0,
            ).text()
        )

        mensalidade = repo.obter_mensalidade(
            self.conexao,
            mensalidade_id,
        )

        if mensalidade is None:
            return

        self.mensalidade_selecionada_id = (
            mensalidade_id
        )

        self.campo_valor.setValue(
            float(mensalidade["valor"])
        )

        self.rotulo_aluno.setText(
            (
                f"{mensalidade['aluno']}\n"
                f"Plano: {mensalidade['plano']}\n"
                f"Vencimento: "
                f"{self.formatar_data(mensalidade['data_vencimento'])}"
            )
        )

        pode_pagar = (
            mensalidade["situacao"]
            in (
                "pendente",
                "atrasada",
            )
        )

        self.botao_pagar.setEnabled(
            pode_pagar
        )

        if not pode_pagar:
            self.mensagem.setText(
                "A mensalidade selecionada não pode "
                "receber um novo pagamento."
            )

    def registrar_pagamento(self):
        if (
            self.mensalidade_selecionada_id
            is None
        ):
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Selecione uma mensalidade.",
            )
            return

        try:
            servicos_financeiro.registrar_pagamento(
                self.conexao,
                self.mensalidade_selecionada_id,
                self.campo_valor.value(),
                self.combo_forma.currentData(),
                self.campo_observacao
                .toPlainText(),
                momento=(
                    self.data_pagamento
                    .dateTime()
                    .toPython()
                ),
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.atualizar_tudo()

        self.mensagem.setText(
            "Pagamento registrado com sucesso."
        )

    def limpar_selecao(self):
        self.mensalidade_selecionada_id = None

        self.rotulo_aluno.setText(
            "Nenhuma mensalidade selecionada"
        )

        self.campo_valor.setValue(0)
        self.combo_forma.setCurrentIndex(0)
        self.data_pagamento.setDateTime(
            QDateTime.currentDateTime()
        )
        self.campo_observacao.clear()
        self.botao_pagar.setEnabled(False)

        if hasattr(
            self,
            "tabela_mensalidades",
        ):
            self.tabela_mensalidades.clearSelection()

    def atualizar_tudo(self):
        self.atualizar_mensalidades()
        self.atualizar_historico()

    @staticmethod
    def formatar_data(data_iso):
        if not data_iso:
            return ""

        return (
            str(data_iso)
            .split(" ")[0]
            .split("-")
        )[::-1]

    @staticmethod
    def formatar_data_hora(valor):
        if not valor:
            return ""

        texto = str(valor)
        data, _, hora = texto.partition(" ")

        partes = data.split("-")

        if len(partes) == 3:
            data = "/".join(
                reversed(partes)
            )

        return (
            f"{data} {hora[:5]}"
            .strip()
        )

    @staticmethod
    def formatar_moeda(valor):
        numero = float(valor)

        formatado = (
            f"{numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {formatado}"