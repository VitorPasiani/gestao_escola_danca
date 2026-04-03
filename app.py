from flask import Flask, render_template, request, redirect, flash
from operacoes import listar_turmas, cadastrar_aluno, cadastrar_professor

app = Flask(__name__)
app.secret_key = 'chave_secreta_espaco_ato'

@app.route('/')
def pagina_inicial():
    escola = "Espaço de Dança ATO"
    turmas_ativas = listar_turmas()
    return render_template('index.html', nome_dinamico=escola, lista_de_turmas=turmas_ativas)

@app.route('/cadastrar_aluno', methods=['GET', 'POST'])
def pagina_cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        rg = request.form.get('rg')
        endereco = request.form.get('endereco')
        data_nascimento = request.form.get('data_nascimento')
        email = request.form.get('email')
        contato_1 = request.form.get('contato_1')
        contato_2 = request.form.get('contato_2')
        responsavel = request.form.get('responsavel')

        cadastrar_aluno(nome, cpf, rg, endereco, data_nascimento, email, contato_1, contato_2, responsavel)
        flash('Aluno cadastrado com sucesso!', 'success')

        return redirect('/cadastrar_aluno')

    return render_template('cadastrar_aluno.html')

@app.route('/cadastrar_professor', methods=['GET', 'POST'])
def pagina_cadastrar_professor():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        chave_pix = request.form.get('chave_pix')

        cadastrar_professor(nome, telefone, chave_pix)
        flash('Professor cadastrado com sucesso!', 'success')

        return redirect('/cadastrar_professor')

    return render_template('cadastrar_professor.html')       

if __name__ == '__main__':
    app.run(debug=True)