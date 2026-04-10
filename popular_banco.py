from operacoes import *

print("🌱 Iniciando o plantio de dados no banco...\n")

# 1. Cadastrando um Professor
print(cadastrar_professor(nome="Juliana (Jazz)", telefone="11999999999", chave_pix="juliana@pix.com"))

# 2. Cadastrando um Aluno
print(cadastrar_aluno(nome="Carlos Silva", cpf="111.222.333-44", contato_1="11988888888", email="carlos@email.com"))
# 3. Cadastrando um Plano
print(cadastrar_plano(nome_plano="Semestral", percentual_desconto=0.15, duracao_meses=6))

# 4. Cadastrando uma Turma (Ligando ao Professor ID 1)
print(cadastrar_turma(
    nome_turma="Jazz Adulto Iniciante",
    tipo_gestao="Parceiro",
    sala="Sala Grande",
    id_professor=1,
    hora_inicio="19:30",
    hora_fim="21:00",
    dias_semana="Terça, Quinta",
    valor_mensal_base=150.00
))

# 5. Cadastrando um Evento e uma Transação
print(cadastrar_evento(nome_evento="Festival de Inverno 2026", data_evento="20/07/2026"))
print(cadastrar_transacao_evento(id_evento=1, descricao="Venda de 10 Ingressos", tipo="Entrada", valor=350.00))

# 6. Cadastrando uma Aula Avulsa
print(cadastrar_aula_avulsa(
    aluno_nome="Mariana Visitante", 
    nome_professor="Juliana", 
    data_aula="30/03/2026", 
    valor_total_aula_avulsa=50.00, 
    percentual_repasse=50
))

# 7. Cadastrando um Pagamento Completo (Usando o laço do Plano Semestral)
print(cadastrar_pagamento(
    id_aluno=1, 
    id_turma=1, 
    id_plano=1, 
    data_vencimento_inicial="10/04/2026", 
    valor_final_mensal=127.50, 
    status="Pago", 
    data_pagamento="30/03/2026", 
    duracao_meses=6
))

print("\n✅ Banco de dados populado com sucesso! A despensa está cheia.")