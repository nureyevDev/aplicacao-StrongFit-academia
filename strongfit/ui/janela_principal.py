from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from strongfit.ui.pagina_alunos import PaginaAlunos
from strongfit.ui.pagina_inicio import PaginaInicio
from strongfit.ui.pagina_planos import PaginaPlanos
from strongfit.ui.pagina_matriculas import PaginaMatriculas
from strongfit.ui.pagina_pagamentos import PaginaPagamentos
from strongfit.ui.pagina_congelamentos import PaginaCongelamentos
from strongfit.ui.pagina_relatorios import PaginaRelatorios

class JanelaPrincipal(QMainWindow):
    def __init__(self, conexao):
        super().__init__()

        self.conexao = conexao

        self.setWindowTitle(
            "StrongFit Academia"
        )
        self.resize(1280, 760)
        self.setMinimumSize(1050, 650)

        self.montar_interface()
        self.aplicar_estilo()

        self.abrir_pagina(0)

    def montar_interface(self):
        central = QWidget()

        layout_principal = QHBoxLayout(central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        layout_principal.addWidget(
            self.criar_barra_lateral()
        )

        self.paginas = QStackedWidget()

        self.pagina_inicio = PaginaInicio(
            self.conexao
        )

        self.pagina_alunos = PaginaAlunos(
            self.conexao
        )

        self.pagina_planos = PaginaPlanos(
            self.conexao
        )

        
        self.pagina_matriculas = PaginaMatriculas(
            self.conexao
        )
        
        self.pagina_pagamentos = PaginaPagamentos(
            self.conexao
        )
        
        self.pagina_congelamentos = (
            PaginaCongelamentos(
                self.conexao
            )
        )
        
        self.pagina_relatorios = PaginaRelatorios(
            self.conexao
        )

        self.paginas.addWidget(
            self.pagina_inicio
        )

        self.paginas.addWidget(
            self.pagina_alunos
        )

        self.paginas.addWidget(
            self.pagina_planos
        )

        self.paginas.addWidget(
            self.pagina_matriculas
        )

        self.paginas.addWidget(
            self.pagina_pagamentos
        )
        
        self.paginas.addWidget(
            self.pagina_congelamentos
        )

        self.paginas.addWidget(
            self.pagina_relatorios
        )
        
        layout_principal.addWidget(
            self.paginas,
            1,
        )

        self.setCentralWidget(central)

    def criar_barra_lateral(self):
        barra = QFrame()
        barra.setObjectName("barraLateral")
        barra.setFixedWidth(230)

        layout = QVBoxLayout(barra)
        layout.setContentsMargins(
            16,
            22,
            16,
            22,
        )
        layout.setSpacing(8)

        nome = QLabel("StrongFit")
        nome.setObjectName("nomeSistema")

        descricao = QLabel(
            "Gestão da academia"
        )
        descricao.setObjectName(
            "descricaoSistema"
        )

        layout.addWidget(nome)
        layout.addWidget(descricao)
        layout.addSpacing(24)

        self.grupo_menu = QButtonGroup(self)
        self.grupo_menu.setExclusive(True)
        self.botoes_menu = []

        itens = [
            ("Visão geral", 0),
            ("Alunos", 1),
            ("Planos", 2),
            ("Matrículas", 3),
            ("Pagamentos", 4),
            ("Congelamentos", 5),
            ("Relatórios", 6),
        ]

        for texto, indice in itens:
            botao = QPushButton(texto)
            botao.setCheckable(True)
            botao.setProperty("menu", True)

            botao.clicked.connect(
                lambda marcado=False, pagina=indice:
                self.abrir_pagina(pagina)
            )

            self.grupo_menu.addButton(
                botao,
                indice,
            )
            self.botoes_menu.append(botao)
            layout.addWidget(botao)

        self.botoes_menu[0].setChecked(True)

        layout.addStretch()

        versao = QLabel("MVP 0.2")
        versao.setObjectName("versao")
        versao.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(versao)

        return barra

    def abrir_pagina(self, indice):
        print(
            "Índice solicitado:",
            indice,
            "| páginas disponíveis:",
            self.paginas.count(),
        )

        if indice < 0 or indice >= self.paginas.count():
            self.statusBar().showMessage(
                "Este módulo será implementado "
                "nas próximas etapas.",
                5000,
            )

            indice_atual = (
                self.paginas.currentIndex()
            )

            if (
                0
                <= indice_atual
                < len(self.botoes_menu)
            ):
                self.botoes_menu[
                    indice_atual
                ].setChecked(True)

            elif indice == 3:
                self.pagina_matriculas.atualizar_tudo()
                
            elif indice == 4:
                self.pagina_pagamentos.atualizar_tudo()
                
            elif indice == 5:
                self.pagina_congelamentos.atualizar_tudo()
            
            elif indice == 6:
                self.pagina_relatorios.atualizar_aba_atual()
                
                
        self.paginas.setCurrentIndex(indice)

        if indice == 0:
            self.pagina_inicio.atualizar()

        elif indice == 1:
            self.pagina_alunos.atualizar_tabela()

        elif indice == 2:
            self.pagina_planos.atualizar_tabela()

    def aplicar_estilo(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f4f6f8;
            }

            QWidget {
                color: #243128;
                font-family: "Segoe UI";
                font-size: 10pt;
            }

            QFrame#barraLateral {
                background-color: #1d3426;
                border: none;
            }

            QLabel#nomeSistema {
                color: #ffffff;
                font-family: "Segoe UI Semibold";
                font-size: 22pt;
            }

            QLabel#descricaoSistema,
            QLabel#versao {
                color: #a9b9ad;
            }

            QPushButton[menu="true"] {
                background-color: transparent;
                color: #dce7de;
                border: none;
                border-radius: 7px;
                padding: 11px 14px;
                text-align: left;
            }

            QPushButton[menu="true"]:hover {
                background-color: #294a35;
            }

            QPushButton[menu="true"]:checked {
                background-color: #3b684a;
                color: #ffffff;
                font-family: "Segoe UI Semibold";
            }
            
            QPushButton#botaoPerigo {
                background-color: #a6403a;
                color: #ffffff;
                border-color: #85332e;
                font-family: "Segoe UI Semibold";
            }

            QPushButton#botaoPerigo:hover {
                background-color: #bd514a;
            }

            QLabel#destaque {
                background-color: #e4eee6;
                color: #294a35;
                border: 1px solid #b7cbbb;
                border-radius: 6px;
                padding: 8px;
                font-family: "Segoe UI Semibold";
            }

            QPushButton#botaoPerigo:pressed {
                background-color: #7b2d29;
            }

            QLabel#tituloPagina {
                color: #1d3426;
                font-family: "Segoe UI Semibold";
                font-size: 22pt;
            }

            QLabel#subtituloPagina {
                color: #647269;
            }

            QFrame#cartao,
            QFrame#cartaoIndicador {
                background-color: #ffffff;
                border: 1px solid #ccd6ce;
                border-radius: 10px;
                padding: 12px;
            }

            QLabel#tituloSecao {
                color: #294a35;
                font-family: "Segoe UI Semibold";
                font-size: 12pt;
            }

            QLabel#valorIndicador {
                color: #294a35;
                font-family: "Segoe UI Semibold";
                font-size: 28pt;
            }

            QLabel#rotuloIndicador {
                color: #647269;
            }

            QLabel#mensagem {
                background-color: #e4eee6;
                color: #294a35;
                border: 1px solid #b7cbbb;
                border-radius: 7px;
                padding: 10px;
            }

            QLineEdit,
            QComboBox,
            QDateEdit,
            QDateTimeEdit,
            QSpinBox,
            QDoubleSpinBox,
            QTextEdit {
            
                background-color: #ffffff;
                color: #243128;
                border: 1px solid #aebcb1;
                border-radius: 7px;
                padding: 7px 9px;
                min-height: 28px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDateEdit:focus,
            QDateTimeEdit:focus,
            QSpinBox:focus,
            QDoubleSpinBox:focus
            QTextEdit:focus {
                border: 2px solid #3b684a;
            }

            QPushButton {
                background-color: #e1e9e3;
                color: #294a35;
                border: 1px solid #aebcb1;
                border-radius: 7px;
                padding: 8px 14px;
                min-height: 27px;
            }

            QPushButton:hover {
                background-color: #cfddd2;
            }

            QSplitter::handle {
                background-color: #d3ded5;
                height: 5px;
            }

            QSplitter::handle:hover {
                background-color: #799682;
            }

            QPushButton#botaoPrimario {
                background-color: #3b684a;
                color: #ffffff;
                border-color: #294a35;
                font-family: "Segoe UI Semibold";
            }

            QPushButton#botaoPrimario:hover {
                background-color: #467c58;
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f0f5f1;
                color: #243128;
                gridline-color: #d5ded7;
                border: 1px solid #b9c7bc;
                border-radius: 7px;
            }

            QTableWidget::item {
                padding: 7px;
            }

            QTableWidget::item:selected {
                background-color: #527d60;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }

            QTabBar::tab {
                background-color: #dce7de;
                color: #294a35;
                border: 1px solid #b7cbbb;
                padding: 9px 16px;
                min-width: 150px;
            }

            QTabBar::tab:selected {
                background-color: #3b684a;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background-color: #294a35;
                color: #ffffff;
                border: none;
                border-right: 1px solid #527d60;
                padding: 9px;
                font-family: "Segoe UI Semibold";
            }
            
            QCheckBox {
                color: #34483a;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #97aa9b;
                border-radius: 4px;
                background-color: #ffffff;
            }

            QCheckBox::indicator:checked {
                background-color: #3b684a;
                border-color: #294a35;
            }
            
             QScrollArea#areaPaginaAlunos {
                background-color: transparent;
                border: none;
            }

            QScrollArea#areaPaginaAlunos > QWidget > QWidget {
                background-color: #f4f6f8;
            }

            QWidget#conteudoPaginaAlunos,
            QWidget#areaSuperiorAlunos {
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #e5ece7;
                width: 12px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background-color: #9eb4a3;
                border-radius: 6px;
                min-height: 35px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #65836d;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            
            QScrollArea#areaDashboard {
                background-color: transparent;
                border: none;
            }

            QScrollArea#areaDashboard > QWidget > QWidget {
                background-color: #f4f6f8;
            }

            QWidget#conteudoDashboard {
                background-color: transparent;
            }

            QFrame#cartaoIndicador {
                background-color: #ffffff;
                border: 1px solid #ccd6ce;
                border-radius: 10px;
                padding: 4px;
            }

            QFrame#cartaoIndicador:hover {
                border-color: #77937f;
            }

            QFrame#cartaoIndicador[destaque="sucesso"] {
                border-left: 5px solid #3b684a;
            }

            QFrame#cartaoIndicador[destaque="perigo"] {
                border-left: 5px solid #a6403a;
            }

            QFrame#cartaoIndicador[destaque="aviso"] {
                border-left: 5px solid #b7832f;
            }

            QFrame#cartaoIndicador[destaque="destaque"] {
                border-left: 5px solid #456f97;
            }

            QFrame#cartaoIndicador[destaque="neutro"] {
                border-left: 5px solid #7d8580;
            }

            QLabel#valorIndicador {
                color: #1d3426;
                font-family: "Segoe UI Semibold";
                font-size: 24pt;
            }

            QLabel#rotuloIndicador {
                color: #647269;
                font-size: 10pt;
            }
            """
            )
                    

                    