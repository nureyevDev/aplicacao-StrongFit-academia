# Levantamento de Requisitos - StrongFit Academia

## 1. Escopo do Projeto

### Objetivo

Desenvolver uma solução própria para a academia StrongFit que substitua o controle manual realizado em planilhas, reduzindo erros operacionais, agilizando o atendimento da recepção e permitindo o acompanhamento financeiro dos alunos.

### Problema de Negócio

O controle manual de mensalidades gera:

- Filas na recepção;
- Erros na consulta de pagamentos;
- Dificuldade no acompanhamento da inadimplência;
- Falta de padronização das informações;
- Dependência de planilhas.

### Escopo Incluído no MVP

#### Gestão de Alunos
- Cadastro de alunos;
- Edição de cadastro;
- Consulta por nome;
- Controle de status do aluno.

#### Gestão de Planos
- Cadastro de planos;
- Associação de plano ao aluno;
- Controle de vencimento.

#### Gestão Financeira
- Registro de pagamentos;
- Controle de inadimplência;
- Histórico financeiro.

#### Gestão de Observações
- Registro de observações;
- Consulta do histórico de observações.

#### Relatórios
- Relatório de alunos ativos;
- Relatório de alunos inadimplentes;
- Relatório de planos mais vendidos;
- Relatório financeiro simplificado.

### Fora do Escopo (Não contemplado no MVP)

- Integração com catraca;
- Aplicativo mobile;
- Portal do aluno;
- Integração bancária;
- Cobrança automática;
- Gestão de dependentes;
- Regras avançadas de desconto;
- Emissão automática de recibos.

---

# 2. Requisitos Funcionais (RF)

## RF01 - Cadastro de Alunos
O sistema deve permitir cadastrar alunos.

## RF02 - Alteração de Alunos
O sistema deve permitir editar os dados cadastrais dos alunos.

## RF03 - Consulta de Alunos
O sistema deve permitir pesquisar alunos pelo nome.

## RF04 - Situação do Aluno
O sistema deve exibir a situação atual do aluno:
- Ativo;
- Inadimplente;
- Congelado.

## RF05 - Observações
O sistema deve permitir registrar observações para cada aluno.

## RF06 - Histórico de Observações
O sistema deve armazenar e consultar o histórico de observações dos alunos.

## RF07 - Cadastro de Planos
O sistema deve permitir cadastrar planos.

## RF08 - Tipos de Plano
O sistema deve suportar os seguintes planos:
- Mensal;
- Trimestral;
- Semestral.

## RF09 - Associação de Plano
O sistema deve permitir vincular um plano a um aluno.

## RF10 - Data de Início
O sistema deve registrar a data de início do plano.

## RF11 - Data de Vencimento
O sistema deve registrar a data de vencimento do plano.

## RF12 - Registro de Pagamentos
O sistema deve permitir registrar pagamentos.

## RF13 - Forma de Pagamento
O sistema deve registrar a forma de pagamento utilizada.

### Formas identificadas inicialmente:
- Pix;
- Dinheiro.

## RF14 - Consulta de Pagamentos
O sistema deve permitir consultar pagamentos realizados.

## RF15 - Controle de Pendências
O sistema deve identificar mensalidades em atraso.

## RF16 - Lista de Inadimplentes
O sistema deve gerar a lista de alunos inadimplentes.

## RF17 - Consulta de Vencimento
O sistema deve exibir a próxima data de vencimento do aluno.

## RF18 - Atualização Financeira
O sistema deve atualizar automaticamente a situação financeira após o registro do pagamento.

## RF19 - Congelamento de Plano
O sistema deve permitir registrar o congelamento de planos.

## RF20 - Motivo do Congelamento
O sistema deve permitir informar o motivo do congelamento.

### Exemplos:
- Viagem;
- Atestado médico;
- Outros.

## RF21 - Consulta de Congelamentos
O sistema deve permitir consultar planos congelados.

## RF22 - Relatório de Alunos Ativos
O sistema deve gerar relatório de alunos ativos.

## RF23 - Relatório de Alunos Inadimplentes
O sistema deve gerar relatório de alunos inadimplentes.

## RF24 - Relatório de Planos Ativos
O sistema deve gerar relatório de planos ativos.

## RF25 - Relatório de Planos Mais Vendidos
O sistema deve gerar relatório dos planos mais vendidos.

## RF26 - Relatório Financeiro
O sistema deve gerar relatório financeiro simplificado.

---

# 3. Requisitos Não Funcionais (RNF)

## RNF01 - Facilidade de Uso
A interface deve ser simples e intuitiva para usuários da recepção.

## RNF02 - Navegação
As principais informações do aluno devem ser acessadas em até 3 cliques.

## RNF03 - Tempo de Resposta
A consulta de um aluno deve retornar em até 2 segundos.

## RNF04 - Atendimento em Horários de Pico
O sistema deve priorizar rapidez no atendimento durante horários de maior movimentação.

## RNF05 - Capacidade
O sistema deve suportar pelo menos 420 alunos cadastrados.

## RNF06 - Desempenho
Consultas de alunos e pagamentos devem ser executadas em até 2 segundos.

## RNF07 - Autenticação
O sistema deve exigir login e senha para acesso.

## RNF08 - Controle de Permissões
Somente usuários autorizados podem alterar informações financeiras.

## RNF09 - Segurança dos Dados
Os dados devem ser armazenados de forma segura em banco de dados.

## RNF10 - Disponibilidade
O sistema deve permanecer disponível durante o horário de funcionamento da academia.

## RNF11 - Backup
O sistema deve possuir mecanismo de backup periódico.

## RNF12 - Evolução de Planos
O sistema deve permitir inclusão futura de novos tipos de planos.

## RNF13 - Evolução de Pagamentos
O sistema deve permitir inclusão futura de novas formas de pagamento.

## RNF14 - Escalabilidade
O sistema deve estar preparado para futuras integrações com recibos e catracas.

---

# 4. Regras de Negócio (RN)

## RN01
Cada aluno poderá possuir apenas um plano ativo por vez.

## RN02
Todo plano deve possuir data de início e vencimento.

## RN03
Todo pagamento deve estar vinculado a um aluno.

## RN04
Todo pagamento deve possuir uma forma de pagamento registrada.

## RN05
Um aluno será considerado inadimplente quando houver vencimento sem pagamento registrado.

## RN06
Um aluno congelado não poderá ser considerado inadimplente durante o período de congelamento.

## RN07
Todo congelamento deve possuir motivo informado.

## RN08
A situação de inadimplência deve ser visualizada apenas por usuários autorizados.

## RN09
As observações cadastradas devem permanecer disponíveis para consultas futuras.

---

# 5. Restrições do Projeto

| ID | Restrição |
|------|------------|
| RES01 | Prazo máximo de desenvolvimento de 75 dias |
| RES02 | Equipe composta por 1 analista, 2 desenvolvedores e 1 QA parcial |
| RES03 | Redução aproximada de 40% do orçamento inicial |
| RES04 | O cliente não deseja pagar mensalidade de software |
| RES05 | As regras de desconto ainda não estão definidas |
| RES06 | Não incluir integração com catraca no MVP |
| RES07 | O MVP deve focar em mensalidades, inadimplência e relatórios simples |

---

# 6. Prioridades do MVP

## Must Have (Obrigatório)

- Cadastro de alunos;
- Cadastro de planos;
- Registro de pagamentos;
- Controle de vencimentos;
- Controle de inadimplência;
- Consulta rápida do status do aluno;
- Relatórios básicos.

## Should Have (Importante)

- Controle de congelamento;
- Histórico de observações.

## Could Have (Desejável)

- Emissão manual de recibo;
- Dashboard resumido.

## Won't Have (Não fará parte do MVP)

- Catraca;
- Aplicativo mobile;
- Portal do aluno;
- Integrações bancárias;
- Dependentes.

---

# 7. Riscos do Projeto

| ID | Risco | Impacto |
|------|--------|---------|
| R01 | Mudanças nas regras financeiras durante o projeto | Alto |
| R02 | Regras de desconto ainda indefinidas | Médio |
| R03 | Recepção não cadastrar ou atualizar informações corretamente | Alto |
| R04 | Solicitação de funcionalidades fora do MVP (catraca ou aplicativo) | Alto |
| R05 | Resistência dos usuários à substituição das planilhas atuais | Médio |
| R06 | Falta de padronização dos processos de congelamento | Médio |
| R07 | Restrições orçamentárias impactarem novas funcionalidades | Alto |

---

# MVP Recomendado

A primeira versão deve contemplar exclusivamente:

1. Cadastro de Alunos;
2. Cadastro de Planos;
3. Controle de Vencimentos;
4. Registro de Pagamentos;
5. Consulta de Situação do Aluno;
6. Controle de Inadimplência;
7. Registro de Observações;
8. Relatórios de Alunos Ativos;
9. Relatórios de Alunos Inadimplentes;
10. Relatório de Planos Mais Vendidos.

Essa abordagem atende às prioridades informadas pelo cliente, respeita a redução de orçamento e aumenta a chance de entrega dentro do prazo de 75 dias.