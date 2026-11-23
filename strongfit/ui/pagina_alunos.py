from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
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
    QVBoxLayout,
    QWidget,
)

from strongfit import repositorio_alunos as repo
from strongfit import servicos_alunos
from strongfit.erros import RegraNegocioErro


class PaginaAlunos(QWidget):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao
        self.aluno_selecionado_id = None

        self.montar_interface()
        self.atualizar_tabela()

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

        conteudo = QHBoxLayout()
        conteudo.setSpacing(16)

        conteudo.addWidget(
            self.criar_formulario(),
            2,
        )
        conteudo.addWidget(
            self.criar_lista(),
            3,
        )

        layout_principal.addLayout(
            conteudo,
            1,
        )

        self.mensagem = QLabel(
            "Preencha os dados para cadastrar."
        )
        self.mensagem.setObjectName(
            "mensagem"
        )

        layout_principal.addWidget(
            self.mensagem
        )

    def criar_formulario(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)

        titulo = QLabel(
            "Dados do aluno"
        )
        titulo.setObjectName(
            "tituloSecao"
        )
        layout.addWidget(titulo)

        formulario = QFormLayout()
        formulario.setSpacing(10)

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

        return frame

    def criar_lista(self):
        frame = QFrame()
        frame.setObjectName("cartao")

        layout = QVBoxLayout(frame)

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

        self.mensagem.setText(
            "Formulário limpo."
        )