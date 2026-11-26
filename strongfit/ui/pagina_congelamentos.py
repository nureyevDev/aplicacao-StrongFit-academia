from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_congelamentos as repo
from strongfit import servicos_congelamentos
from strongfit.erros import RegraNegocioErro


class PaginaCongelamentos(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.congelamento_selecionado_id = None

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
            "Congelamento de planos"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Suspenda temporariamente uma matrícula "
            "sem considerar o aluno inadimplente."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(16)

        conteudo.addWidget(
            self.criar_formulario(),
            2,
        )

        conteudo.addWidget(
            self.criar_lista(),
            4,
        )

        layout_principal.addLayout(
            conteudo,
            1,
        )

        self.mensagem = QLabel(
            "Selecione uma matrícula ativa para congelar."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)

        layout_principal.addWidget(
            self.mensagem
        )

    def criar_formulario(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        titulo = QLabel(
            "Novo congelamento"
        )
        titulo.setObjectName(
            "tituloSecao"
        )
        layout.addWidget(titulo)

        formulario = QFormLayout()
        formulario.setSpacing(11)

        self.combo_matricula = QComboBox()

        self.data_inicio = QDateEdit(
            QDate.currentDate()
        )
        self.data_inicio.setCalendarPopup(
            True
        )
        self.data_inicio.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.data_fim_prevista = QDateEdit(
            QDate.currentDate().addDays(30)
        )
        self.data_fim_prevista.setCalendarPopup(
            True
        )
        self.data_fim_prevista.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.combo_motivo = QComboBox()
        self.combo_motivo.addItem(
            "Selecione",
            None,
        )
        self.combo_motivo.addItem(
            "Viagem",
            "Viagem",
        )
        self.combo_motivo.addItem(
            "Atestado médico",
            "Atestado médico",
        )
        self.combo_motivo.addItem(
            "Outros",
            "Outros",
        )

        self.campo_motivo_detalhado = QTextEdit()
        self.campo_motivo_detalhado.setPlaceholderText(
            "Detalhes do motivo"
        )
        self.campo_motivo_detalhado.setMaximumHeight(
            100
        )

        formulario.addRow(
            "Matrícula *",
            self.combo_matricula,
        )
        formulario.addRow(
            "Início *",
            self.data_inicio,
        )
        formulario.addRow(
            "Previsão de retorno",
            self.data_fim_prevista,
        )
        formulario.addRow(
            "Motivo *",
            self.combo_motivo,
        )
        formulario.addRow(
            "Detalhes",
            self.campo_motivo_detalhado,
        )

        layout.addLayout(formulario)

        self.botao_congelar = QPushButton(
            "Registrar congelamento"
        )
        self.botao_congelar.setObjectName(
            "botaoPrimario"
        )
        self.botao_congelar.clicked.connect(
            self.registrar_congelamento
        )

        self.botao_limpar = QPushButton(
            "Limpar"
        )
        self.botao_limpar.clicked.connect(
            self.limpar_formulario
        )

        botoes = QHBoxLayout()
        botoes.addWidget(
            self.botao_congelar
        )
        botoes.addWidget(
            self.botao_limpar
        )

        layout.addLayout(botoes)
        layout.addStretch()

        return frame

    def criar_lista(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        topo = QHBoxLayout()

        titulo = QLabel(
            "Congelamentos registrados"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar aluno, plano ou motivo"
        )

        self.check_somente_abertos = QCheckBox(
            "Somente abertos"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa
        )
        topo.addWidget(
            self.check_somente_abertos
        )

        self.tabela = QTableWidget(
            0,
            8,
        )

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Aluno",
                "CPF",
                "Plano",
                "Início",
                "Previsão",
                "Motivo",
                "Situação",
            ]
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )
        self.tabela.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )
        self.tabela.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )
        self.tabela.setAlternatingRowColors(
            True
        )
        self.tabela.verticalHeader().setVisible(
            False
        )

        cabecalho = (
            self.tabela.horizontalHeader()
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
            6,
            QHeaderView.ResizeMode.Stretch,
        )

        for coluna in (
            2,
            3,
            4,
            5,
            7,
        ):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        self.botao_encerrar = QPushButton(
            "Encerrar congelamento selecionado"
        )
        self.botao_encerrar.setObjectName(
            "botaoPerigo"
        )
        self.botao_encerrar.clicked.connect(
            self.encerrar_congelamento
        )

        self.campo_pesquisa.textChanged.connect(
            self.atualizar_tabela
        )
        self.check_somente_abertos.toggled.connect(
            self.atualizar_tabela
        )
        self.tabela.itemSelectionChanged.connect(
            self.selecionar_congelamento
        )

        acoes = QHBoxLayout()
        acoes.addStretch()
        acoes.addWidget(
            self.botao_encerrar
        )

        layout.addLayout(topo)
        layout.addWidget(self.tabela)
        layout.addLayout(acoes)

        return frame

    def carregar_matriculas(self):
        matriculas = (
            repo.listar_matriculas_disponiveis(
                self.conexao
            )
        )

        atual = self.combo_matricula.currentData()

        self.combo_matricula.clear()
        self.combo_matricula.addItem(
            "Selecione uma matrícula",
            None,
        )

        for matricula in matriculas:
            texto = (
                f"{matricula['aluno']} | "
                f"{matricula['plano']}"
            )

            if matricula["cpf"]:
                texto += (
                    f" | {matricula['cpf']}"
                )

            self.combo_matricula.addItem(
                texto,
                matricula["id"],
            )

        indice = (
            self.combo_matricula.findData(
                atual
            )
        )

        self.combo_matricula.setCurrentIndex(
            max(indice, 0)
        )

    def registrar_congelamento(self):
        motivo_base = (
            self.combo_motivo.currentData()
        )

        detalhes = " ".join(
            self.campo_motivo_detalhado
            .toPlainText()
            .split()
        )

        if motivo_base == "Outros":
            motivo = detalhes
        elif motivo_base and detalhes:
            motivo = (
                f"{motivo_base}: {detalhes}"
            )
        else:
            motivo = motivo_base or ""

        try:
            servicos_congelamentos.registrar_congelamento(
                self.conexao,
                self.combo_matricula.currentData(),
                self.data_inicio
                .date()
                .toPython(),
                self.data_fim_prevista
                .date()
                .toPython(),
                motivo,
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.limpar_formulario()
        self.atualizar_tudo()

        self.mensagem.setText(
            "Congelamento registrado com sucesso."
        )

    def atualizar_tabela(self):
        linhas = repo.listar_congelamentos(
            self.conexao,
            self.campo_pesquisa.text(),
            self.check_somente_abertos.isChecked(),
        )

        self.tabela.setRowCount(
            len(linhas)
        )

        for linha, congelamento in enumerate(
            linhas
        ):
            valores = [
                congelamento["id"],
                congelamento["aluno"],
                congelamento["cpf"] or "",
                congelamento["plano"],
                self.formatar_data(
                    congelamento["data_inicio"]
                ),
                self.formatar_data(
                    congelamento[
                        "data_fim_prevista"
                    ]
                ),
                congelamento["motivo"],
                congelamento["situacao"].title(),
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna in (
                    0,
                    4,
                    5,
                    7,
                ):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela.clearSelection()
        self.congelamento_selecionado_id = None

    def selecionar_congelamento(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            self.congelamento_selecionado_id = None
            return

        self.congelamento_selecionado_id = int(
            self.tabela.item(
                linha,
                0,
            ).text()
        )

    def encerrar_congelamento(self):
        if (
            self.congelamento_selecionado_id
            is None
        ):
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Selecione um congelamento.",
            )
            return

        congelamento = repo.obter_congelamento(
            self.conexao,
            self.congelamento_selecionado_id,
        )

        if congelamento is None:
            return

        if congelamento["data_fim_real"]:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Este congelamento já foi encerrado.",
            )
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar encerramento",
            (
                f"Encerrar o congelamento de "
                f"{congelamento['aluno']}?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            servicos_congelamentos.encerrar_congelamento(
                self.conexao,
                self.congelamento_selecionado_id,
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
            "Congelamento encerrado com sucesso."
        )

    def limpar_formulario(self):
        self.combo_matricula.setCurrentIndex(0)
        self.data_inicio.setDate(
            QDate.currentDate()
        )
        self.data_fim_prevista.setDate(
            QDate.currentDate().addDays(30)
        )
        self.combo_motivo.setCurrentIndex(0)
        self.campo_motivo_detalhado.clear()
        self.tabela.clearSelection()
        self.congelamento_selecionado_id = None

    def atualizar_tudo(self):
        self.carregar_matriculas()
        self.atualizar_tabela()

    @staticmethod
    def formatar_data(data_iso):
        if not data_iso:
            return ""

        partes = (
            str(data_iso)
            .split(" ")[0]
            .split("-")
        )

        if len(partes) != 3:
            return str(data_iso)

        return "/".join(
            reversed(partes)
        )