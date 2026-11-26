from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_alunos as repo
from strongfit import repositorio_observacoes as repo_observacoes
from strongfit import servicos_alunos
from strongfit import servicos_observacoes
from strongfit.erros import RegraNegocioErro


class PaginaAlunos(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.aluno_selecionado_id = None
        self.observacao_selecionada_id = None

        self.montar_interface()
        self.atualizar_tabela()

    
    def registrar_observacao(self):
        try:
            servicos_observacoes.registrar_observacao(
                self.conexao,
                self.aluno_selecionado_id,
                self.campo_observacao
                .toPlainText(),
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.campo_observacao.clear()
        self.atualizar_observacoes()

        self.mensagem.setText(
            "Observação registrada com sucesso."
        )
        
    def atualizar_observacoes(self):
        if self.aluno_selecionado_id is None:
            self.tabela_observacoes.setRowCount(
                0
            )
            return

        linhas = (
            repo_observacoes
            .listar_observacoes_do_aluno(
                self.conexao,
                self.aluno_selecionado_id,
                self.campo_pesquisa_observacao
                .text(),
            )
        )

        self.tabela_observacoes.setRowCount(
            len(linhas)
        )

        for linha, observacao in enumerate(
            linhas
        ):
            valores = [
                observacao["id"],
                self.formatar_data_hora(
                    observacao["criado_em"]
                ),
                observacao["usuario"],
                observacao["texto"],
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                if coluna in (0, 1):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.tabela_observacoes.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela_observacoes.clearSelection()
        self.observacao_selecionada_id = None
        self.botao_excluir_observacao.setEnabled(
            False
        )
    
    def selecionar_observacao(self):
        linha = (
            self.tabela_observacoes
            .currentRow()
        )

        if linha < 0:
            self.observacao_selecionada_id = (
                None
            )
            self.botao_excluir_observacao.setEnabled(
                False
            )
            return

        self.observacao_selecionada_id = int(
            self.tabela_observacoes.item(
                linha,
                0,
            ).text()
        )

        self.botao_excluir_observacao.setEnabled(
            True
        )
    
    def excluir_observacao(self):
        if (
            self.observacao_selecionada_id
            is None
        ):
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                "Selecione uma observação.",
            )
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            (
                "Deseja excluir a observação "
                "selecionada?\n\n"
                "Essa operação não poderá "
                "ser desfeita."
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
            servicos_observacoes.remover_observacao(
                self.conexao,
                self.observacao_selecionada_id,
            )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.atualizar_observacoes()

        self.mensagem.setText(
            "Observação excluída com sucesso."
        )
        
    def atualizar_contador_observacao(self):
        tamanho = len(
            self.campo_observacao
            .toPlainText()
        )

        self.contador_observacao.setText(
            f"{tamanho}/1000 caracteres"
        )

        ultrapassou = tamanho > 1000

        self.botao_salvar_observacao.setEnabled(
            (
                self.aluno_selecionado_id
                is not None
            )
            and not ultrapassou
        )

        if ultrapassou:
            self.contador_observacao.setStyleSheet(
                "color: #a6403a;"
            )
        else:
            self.contador_observacao.setStyleSheet(
                ""
            )    
       
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
        
    
    def montar_interface(self):
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        layout_externo.setSpacing(0)

        area_rolagem = QScrollArea()
        area_rolagem.setObjectName(
            "areaPaginaAlunos"
        )
        area_rolagem.setWidgetResizable(True)
        area_rolagem.setFrameShape(
            QFrame.Shape.NoFrame
        )
        area_rolagem.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        area_rolagem.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        conteudo_pagina = QWidget()
        conteudo_pagina.setObjectName(
            "conteudoPaginaAlunos"
        )
        conteudo_pagina.setMinimumWidth(950)

        layout_principal = QVBoxLayout(
            conteudo_pagina
        )
        layout_principal.setContentsMargins(
            22,
            22,
            22,
            22,
        )
        layout_principal.setSpacing(14)

        titulo = QLabel(
            "Gestão de alunos"
        )
        titulo.setObjectName(
            "tituloPagina"
        )

        subtitulo = QLabel(
            "Cadastre, consulte e atualize "
            "os dados dos alunos."
        )
        subtitulo.setObjectName(
            "subtituloPagina"
        )

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        divisor = QSplitter(
            Qt.Orientation.Vertical
        )

        # Impede que uma das áreas seja totalmente comprimida.
        divisor.setChildrenCollapsible(False)

        area_superior = QWidget()
        area_superior.setObjectName(
            "areaSuperiorAlunos"
        )
        area_superior.setMinimumHeight(470)

        conteudo_superior = QHBoxLayout(
            area_superior
        )
        conteudo_superior.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        conteudo_superior.setSpacing(16)

        self.cartao_formulario = (
            self.criar_formulario()
        )
        self.cartao_lista = self.criar_lista()

        self.cartao_formulario.setMinimumWidth(
            410
        )
        self.cartao_formulario.setMinimumHeight(
            450
        )
        self.cartao_formulario.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        self.cartao_lista.setMinimumWidth(600)
        self.cartao_lista.setMinimumHeight(450)
        self.cartao_lista.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        conteudo_superior.addWidget(
            self.cartao_formulario,
            2,
        )
        conteudo_superior.addWidget(
            self.cartao_lista,
            3,
        )

        self.area_observacoes = (
            self.criar_area_observacoes()
        )
        self.area_observacoes.setMinimumHeight(
            300
        )
        self.area_observacoes.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        divisor.addWidget(area_superior)
        divisor.addWidget(
            self.area_observacoes
        )

        divisor.setStretchFactor(0, 3)
        divisor.setStretchFactor(1, 2)

        divisor.setSizes(
            [
                470,
                320,
            ]
        )

        layout_principal.addWidget(
            divisor,
            1,
        )

        self.mensagem = QLabel(
            "Preencha os dados para cadastrar."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )
        self.mensagem.setWordWrap(True)
        self.mensagem.setMinimumHeight(48)

        layout_principal.addWidget(
            self.mensagem
        )

        area_rolagem.setWidget(
            conteudo_pagina
        )

        layout_externo.addWidget(
            area_rolagem
        )

    def criar_formulario(self):
        frame = QFrame()
        frame.setObjectName("cartao")
        frame.setMinimumHeight(450)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )
        layout.setSpacing(12)

        titulo = QLabel(
            "Dados do aluno"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        layout.addWidget(titulo)

        formulario = QFormLayout()
        formulario.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        formulario.setHorizontalSpacing(14)
        formulario.setVerticalSpacing(10)

        formulario.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy
            .AllNonFixedFieldsGrow
        )

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText(
            "Nome completo"
        )

        self.campo_cpf = QLineEdit()
        self.campo_cpf.setPlaceholderText(
            "Somente números"
        )
        self.campo_cpf.setMaxLength(14)

        self.data_nascimento = QDateEdit()
        self.data_nascimento.setCalendarPopup(
            True
        )
        self.data_nascimento.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.data_nascimento.setDate(
            QDate(2000, 1, 1)
        )

        self.campo_telefone = QLineEdit()
        self.campo_telefone.setPlaceholderText(
            "(00) 00000-0000"
        )

        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText(
            "aluno@exemplo.com"
        )

        self.campo_endereco = QLineEdit()
        self.campo_endereco.setPlaceholderText(
            "Rua, número e bairro"
        )

        self.combo_situacao = QComboBox()
        self.combo_situacao.addItem(
            "Ativo",
            "ativo",
        )
        self.combo_situacao.addItem(
            "Inadimplente",
            "inadimplente",
        )
        self.combo_situacao.addItem(
            "Congelado",
            "congelado",
        )
        self.combo_situacao.addItem(
            "Inativo",
            "inativo",
        )
        
        campos = [
            self.campo_nome,
            self.campo_cpf,
            self.data_nascimento,
            self.campo_telefone,
            self.campo_email,
            self.campo_endereco,
            self.combo_situacao,
        ]

        for campo in campos:
            campo.setMinimumHeight(36)

        formulario.addRow(
            "Nome *",
            self.campo_nome,
        )
        formulario.addRow(
            "CPF",
            self.campo_cpf,
        )
        formulario.addRow(
            "Nascimento",
            self.data_nascimento,
        )
        formulario.addRow(
            "Telefone",
            self.campo_telefone,
        )
        formulario.addRow(
            "E-mail",
            self.campo_email,
        )
        formulario.addRow(
            "Endereço",
            self.campo_endereco,
        )
        formulario.addRow(
            "Situação",
            self.combo_situacao,
        )

        layout.addLayout(formulario)

        botoes = QHBoxLayout()

        self.botao_salvar = QPushButton(
            "Cadastrar"
        )
        self.botao_salvar.setObjectName(
            "botaoPrimario"
        )

        self.botao_limpar = QPushButton(
            "Limpar"
        )

        
        self.botao_salvar.clicked.connect(
            self.salvar_aluno
        )
        
        self.botao_salvar.setMinimumHeight(44)
        
        self.botao_limpar.setMinimumHeight(44)

        self.botao_limpar.clicked.connect(
            self.limpar_formulario
        )

        botoes.addWidget(
            self.botao_salvar
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
        frame.setMinimumHeight(450)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )
        layout.setSpacing(12)
        
        topo = QHBoxLayout()

        titulo = QLabel(
            "Alunos cadastrados"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar por nome"
        )

        self.filtro_situacao = QComboBox()
        self.filtro_situacao.addItem(
            "Todas as situações",
            None,
        )
        self.filtro_situacao.addItem(
            "Ativos",
            "ativo",
        )
        self.filtro_situacao.addItem(
            "Inadimplentes",
            "inadimplente",
        )
        self.filtro_situacao.addItem(
            "Congelados",
            "congelado",
        )
        self.filtro_situacao.addItem(
            "Inativos",
            "inativo",
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.campo_pesquisa
        )
        topo.addWidget(
            self.filtro_situacao
        )

        self.tabela = QTableWidget(
            0,
            6,
        )

        self.tabela.setMinimumHeight(300)

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Nome",
                "CPF",
                "Telefone",
                "Situação",
                "Vencimento",
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

        for coluna in range(2, 6):
            cabecalho.setSectionResizeMode(
                coluna,
                QHeaderView
                .ResizeMode
                .ResizeToContents,
            )

        self.campo_pesquisa.textChanged.connect(
            self.atualizar_tabela
        )

        self.filtro_situacao.currentIndexChanged.connect(
            self.atualizar_tabela
        )

        self.tabela.itemSelectionChanged.connect(
            self.carregar_aluno_selecionado
        )

        layout.addLayout(topo)
        layout.addWidget(self.tabela)

        return frame
    
    def criar_area_observacoes(self):
        frame = QFrame()
        frame.setObjectName("cartao")
        frame.setMinimumHeight(300)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )
        layout.setSpacing(12)

        topo = QHBoxLayout()

        titulo = QLabel(
            "Observações do aluno"
        )
        titulo.setObjectName(
            "tituloSecao"
        )

        self.rotulo_aluno_observacao = QLabel(
            "Selecione um aluno na tabela"
        )
        self.rotulo_aluno_observacao.setObjectName(
            "destaque"
        )

        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(
            self.rotulo_aluno_observacao
        )

        layout.addLayout(topo)

        conteudo = QHBoxLayout()
        conteudo.setSpacing(14)

        formulario = QVBoxLayout()

        self.campo_observacao = QTextEdit()
        self.campo_observacao.setPlaceholderText(
            "Digite uma informação relevante "
            "sobre o aluno"
        )
        self.campo_observacao.setMaximumHeight(
            120
        )
        self.campo_observacao.setEnabled(False)

        self.contador_observacao = QLabel(
            "0/1000 caracteres"
        )
        self.contador_observacao.setObjectName(
            "contador"
        )

        self.botao_salvar_observacao = (
            QPushButton(
                "Registrar observação"
            )
        )
        self.botao_salvar_observacao.setObjectName(
            "botaoPrimario"
        )
        self.botao_salvar_observacao.setEnabled(
            False
        )

        self.botao_salvar_observacao.clicked.connect(
            self.registrar_observacao
        )

        self.campo_observacao.textChanged.connect(
            self.atualizar_contador_observacao
        )

        formulario.addWidget(
            QLabel("Nova observação")
        )
        formulario.addWidget(
            self.campo_observacao
        )
        formulario.addWidget(
            self.contador_observacao
        )
        formulario.addWidget(
            self.botao_salvar_observacao
        )
        formulario.addStretch()

        historico = QVBoxLayout()

        filtros = QHBoxLayout()

        self.campo_pesquisa_observacao = (
            QLineEdit()
        )
        self.campo_pesquisa_observacao.setPlaceholderText(
            "Pesquisar no histórico"
        )
        self.campo_pesquisa_observacao.setEnabled(
            False
        )

        self.botao_excluir_observacao = (
            QPushButton(
                "Excluir selecionada"
            )
        )
        self.botao_excluir_observacao.setObjectName(
            "botaoPerigo"
        )
        self.botao_excluir_observacao.setEnabled(
            False
        )

        self.botao_excluir_observacao.clicked.connect(
            self.excluir_observacao
        )

        self.campo_pesquisa_observacao.textChanged.connect(
            self.atualizar_observacoes
        )

        filtros.addWidget(
            self.campo_pesquisa_observacao
        )
        filtros.addWidget(
            self.botao_excluir_observacao
        )

        self.tabela_observacoes = QTableWidget(
            0,
            4,
        )
        
        self.tabela_observacoes.setMinimumHeight(
            150
        )

        self.tabela_observacoes.setHorizontalHeaderLabels(
            [
                "ID",
                "Data e hora",
                "Responsável",
                "Observação",
            ]
        )

        self.tabela_observacoes.setSelectionBehavior(
            QAbstractItemView
            .SelectionBehavior
            .SelectRows
        )

        self.tabela_observacoes.setSelectionMode(
            QAbstractItemView
            .SelectionMode
            .SingleSelection
        )

        self.tabela_observacoes.setEditTriggers(
            QAbstractItemView
            .EditTrigger
            .NoEditTriggers
        )

        self.tabela_observacoes.setAlternatingRowColors(
            True
        )

        self.tabela_observacoes.verticalHeader().setVisible(
            False
        )

        cabecalho = (
            self.tabela_observacoes
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
            QHeaderView
            .ResizeMode
            .ResizeToContents,
        )

        cabecalho.setSectionResizeMode(
            2,
            QHeaderView
            .ResizeMode
            .ResizeToContents,
        )

        cabecalho.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch,
        )

        self.tabela_observacoes.itemSelectionChanged.connect(
            self.selecionar_observacao
        )

        historico.addLayout(filtros)
        historico.addWidget(
            self.tabela_observacoes
        )

        conteudo.addLayout(
            formulario,
            2,
        )
        conteudo.addLayout(
            historico,
            4,
        )

        layout.addLayout(
            conteudo,
            1,
        )

        return frame

    def dados_formulario(self):
        data = self.data_nascimento.date()

        return (
            self.campo_nome.text(),
            self.campo_cpf.text(),
            data.toString("yyyy-MM-dd"),
            self.campo_telefone.text(),
            self.campo_email.text(),
            self.campo_endereco.text(),
            self.combo_situacao.currentData(),
        )

    def salvar_aluno(self):
        try:
            if self.aluno_selecionado_id is None:
                servicos_alunos.cadastrar_aluno(
                    self.conexao,
                    *self.dados_formulario(),
                )

                mensagem = (
                    "Aluno cadastrado com sucesso."
                )

            else:
                servicos_alunos.editar_aluno(
                    self.conexao,
                    self.aluno_selecionado_id,
                    *self.dados_formulario(),
                )

                mensagem = (
                    "Aluno atualizado com sucesso."
                )

        except RegraNegocioErro as erro:
            QMessageBox.warning(
                self,
                "StrongFit Academia",
                str(erro),
            )
            return

        self.limpar_formulario()
        self.atualizar_tabela()

        self.mensagem.setText(mensagem)

    def atualizar_tabela(self):
        alunos = repo.listar_alunos(
            self.conexao,
            self.campo_pesquisa.text(),
            self.filtro_situacao.currentData(),
        )

        self.tabela.setRowCount(
            len(alunos)
        )

        for linha, aluno in enumerate(alunos):
            valores = [
                aluno["id"],
                aluno["nome"],
                aluno["cpf"] or "",
                aluno["telefone"] or "",
                aluno["situacao"].title(),
                aluno["proximo_vencimento"]
                or "Sem plano",
            ]

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item,
                )

        self.tabela.clearSelection()

    def carregar_aluno_selecionado(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            return

        aluno_id = int(
            self.tabela.item(
                linha,
                0,
            ).text()
        )

        aluno = repo.obter_aluno(
            self.conexao,
            aluno_id,
        )

        if aluno is None:
            return

        self.aluno_selecionado_id = aluno_id

        self.campo_nome.setText(
            aluno["nome"]
        )
        self.campo_cpf.setText(
            aluno["cpf"] or ""
        )
        self.campo_telefone.setText(
            aluno["telefone"] or ""
        )
        self.campo_email.setText(
            aluno["email"] or ""
        )
        self.campo_endereco.setText(
            aluno["endereco"] or ""
        )

        if aluno["data_nascimento"]:
            data = QDate.fromString(
                aluno["data_nascimento"],
                "yyyy-MM-dd",
            )

            self.data_nascimento.setDate(
                data
            )

        indice = (
            self.combo_situacao.findData(
                aluno["situacao"]
            )
        )

        self.combo_situacao.setCurrentIndex(
            max(indice, 0)
        )

        self.rotulo_aluno_observacao.setText(
            aluno["nome"]
        )

        self.campo_observacao.setEnabled(
            True
        )

        self.campo_pesquisa_observacao.setEnabled(
            True
        )

        self.botao_salvar_observacao.setEnabled(
            True
        )

        self.campo_observacao.clear()
        self.campo_pesquisa_observacao.clear()

        self.atualizar_observacoes()

        self.botao_salvar.setText(
            "Atualizar"
        )

        self.mensagem.setText(
            "Aluno selecionado para edição."
        )
        

    def limpar_formulario(self):
        self.aluno_selecionado_id = None

        self.campo_nome.clear()
        self.campo_cpf.clear()
        self.data_nascimento.setDate(
            QDate(2000, 1, 1)
        )
        self.campo_telefone.clear()
        self.campo_email.clear()
        self.campo_endereco.clear()
        self.combo_situacao.setCurrentIndex(0)
        self.tabela.clearSelection()
        self.botao_salvar.setText(
            "Cadastrar"
        )
        self.campo_nome.setFocus()
        
        self.observacao_selecionada_id = None

        self.rotulo_aluno_observacao.setText(
            "Selecione um aluno na tabela"
        )

        self.campo_observacao.clear()
        self.campo_observacao.setEnabled(False)

        self.campo_pesquisa_observacao.clear()
        self.campo_pesquisa_observacao.setEnabled(
            False
        )

        self.botao_salvar_observacao.setEnabled(
            False
        )

        self.botao_excluir_observacao.setEnabled(
            False
        )

        self.tabela_observacoes.setRowCount(0)

        self.mensagem.setText(
            "Formulário limpo."
        )