import streamlit as st
import mysql.connector
import streamlit.components.v1 as components

# Configurações de conexão
config = {
    'user': 'admin',
    'password': 'Eduardo13*',
    'host': 'institutoscheffelt.clazmf0mr7c4.sa-east-1.rds.amazonaws.com',
    'database': 'questoes',
    'raise_on_warnings': True
}

#Função para obter todas as questões
def obter_todas_questoes(materia,assunto):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Consulta para recuperar todas as questões com assuntos
        cursor.execute("""
            SELECT
                Q.QuestaoID,
                Q.Enunciado,
                Q.Questao,
                Q.Resposta_Oficial,
                Q.Comentario,
                M.Materia,
                A.Assunto,
                O.Orgao,
                C.Cargo,
                P.Prova, 
                Ano.Ano,   
                B.Banca                 
            FROM Questoes Q
            JOIN Materias M ON Q.MateriaID = M.MateriaID 
            JOIN Assuntos A ON Q.AssuntoID = A.AssuntoID
            JOIN Orgaos O ON Q.OrgaoID = O.OrgaoID
            JOIN Cargos C ON Q.CargoID = C.CargoID
            JOIN Provas P ON Q.ProvaID = P.ProvaID
            JOIN Anos Ano ON Q.AnoID = Ano.AnoID
            JOIN Bancas B ON Q.BancaID = B.BancaID         
            WHERE M.Materia = %s AND A.Assunto = %s;
            """, (materia,assunto,))

        # Recuperar os resultados
        questoes = cursor.fetchall()
        return questoes

    except Exception as e:
        st.error(f"Erro ao obter questões: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

# Função principal do dashboard
def main():
    st.set_page_config(page_title="Revisão de Questões", page_icon=":pencil:")

    st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
    )
    # Inicializar variáveis de estado
    if "acertos" not in st.session_state:
        st.session_state.acertos = 0

    if "erros" not in st.session_state:
        st.session_state.erros = 0
    # Ajustar o layout e estilo da resposta 
    st.markdown(
        """
        <style>
            body {
                font-size: 16px;
            }
            .btn-primary {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
            }
            .alternativas {
                margin-bottom: 20px;
            }
            .resposta-mensagem {
                font-size: 18px;
                margin-top: 8px;
                padding: 5px;
                border-radius: 8px;
            }
            .resposta-correta {
                background-color: #5cb85c;
                color: white;
            }
            .resposta-incorreta {
                background-color: #d9534f;
                color: white;
            }
            .acertos-mensagem {
                font-size: 18px;
                margin-top: 22px;
                padding: 6px;
                border-radius: 3px;
                text-align: center;
                margin: 4px 6px;
                cursor: pointer;
                border-radius: 8px;
                display: inline-block;
            }
            .acertos-correta {
                background-color: #5cb85c;
                color: white;
            }
            .acertos-incorreta {
                background-color: #d9534f;
                color: white;
            }
        </style>
        """
        , unsafe_allow_html=True)

    # Filtro de assunto na URL
    params = st.experimental_get_query_params()
    materia = params.get("materia", ["Direito Administrativo"])[0]
    assunto = params.get("assunto", ["Mérito Administrativo"])[0]
    if materia == 'da':
        materia = "Direito Administrativo"
    if assunto == 'ci':
        materia = "Conceito de Atos Administrativos"
    #assunto_selecionado = st.experimental_get_query_params().get("assunto", ["Conceitos Iniciais"])[0]

    # Exibir todas as questões cadastradas
    questoes = obter_todas_questoes(materia,assunto)
    st.header(f"Questões sobre {assunto}", divider='orange')
    # Seção para mostrar os acertos e erros
        
    # Controlar o índice da questão
    questao_index = st.session_state.get("questao_index", 0)
    resposta_usuario = st.session_state.get("resposta_usuario", None)
    total_questoes = len(questoes)
# Adicione esta parte no final da sua função main(), antes do if __name__ == "__main__":
    if questao_index == total_questoes - 1:
        st.markdown(
            f"""
                <h4>Boletim de Desempenho</h4>""", 
            unsafe_allow_html=True,
            )


        # Lógica para calcular a porcentagem de acertos
        total_perguntas = total_questoes
        percentual_acertos = (st.session_state.acertos / total_perguntas) * 100

        st.write(f"**Total de Acertos:** {st.session_state.acertos}")
        st.write(f"**Total de Erros:** {st.session_state.erros}")

        if percentual_acertos >= 70:
            st.success(f"Você teve um desempenho de {percentual_acertos:.2f}% - Parabéns!")
        else:
            st.error(f"Você teve um desempenho de {percentual_acertos:.2f}% - Estude mais para melhorar!")

        # Adicione um botão para reiniciar as questões
        if st.button("Reiniciar Questões"):
            # Reseta o estado da sessão
            st.session_state.questao_index = 0
            st.session_state.acertos = 0
            st.session_state.erros = 0
            # Limpa a tela atual
            st.empty()
    else:
        # Botões para navegar entre as questões
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Questão Anterior") and questao_index > 0:
                questao_index -= 1
                st.session_state.questao_index = questao_index

        with col2:
            st.markdown(f"""
                <div class="acertos-mensagem acertos-correta"><strong></strong>Acertos: {st.session_state.acertos}</div>    
                <div class="acertos-mensagem acertos-incorreta"><strong>Erros:</strong> {st.session_state.erros}</div> 
            """, 
            unsafe_allow_html=True,
            )


        with col3:
            if st.button("Próxima Questão") and questao_index < total_questoes - 1:
                questao_index += 1
                st.session_state.questao_index = questao_index

        # Selecionar a questão atual
        questao_id, enunciado, questao, resposta_oficial, Comentario, materia, assunto, orgao, cargo, prova, ano, banca = questoes[questao_index]

        st.markdown("""
            <style>
            /*
            Oculta os elementos com a classe .mostrar
            Oculta os elementos com a classe .hide-action
            */

            #box-1 .mostrar,
            #box-1 .hide-action,
            #box-2 .mostrar,
            #box-2 .hide-action {
                display: none;
            }

            /*
            conforme a HASH atual:
            Mostra os elementos com a classe .mostrar
            Mostra os elementos com a classe .hide-action
            */

            #box-1:target .mostrar,
            #box-1:target .hide-action,
            #box-2:target .mostrar,
            #box-2:target .hide-action {
                display: block;
            }

            /*
            conforme a HASH atual:
            Oculta os elementos com a classe .action-action
            */
            #box-1:target .show-action,
            #box-2:target .show-action
            {
                display: none;
            }
            </style>
                            """
        , unsafe_allow_html=True)


        with st.form("form_questao"):
            orgao_1 = orgao.split('-')[0].strip()
            st.markdown(
            f"""
            <div id="box-1">
            <div class="foo" style="display: flex; justify-content: space-between; align-items: baseline;">
                <div class="bar">
                    <div style="display: flex; align-items: baseline;">
                        <h5>Questão {questao_index + 1}/{total_questoes} - CEBRASPE (CESPE) - {orgao_1}/{ano}</h5>
                        <a href="#box-1" style="text-decoration: none; color: #007BFF; display: flex; align-items: center;margin-left: 80px;">
                            <span style="flex: 1; text-align: right; margin-right: 5px;">Mostrar Detalhes</span>
                            <i class="fas fa-info-circle" style="color: #007BFF;"></i>
                        </a>
                    </div>
                    <div class="mostrar" style="margin-top: 10px; border: 1px solid #ccc; padding: 10px; margin: 10px; border-radius: 5px;"">
                        <p><strong>Matéria:</strong> {materia}</p>
                        <p><strong>Assunto:</strong> {assunto}</p>
                        <p><strong>Órgão:</strong> {orgao}</p>
                        <p><strong>Cargo:</strong> {cargo}</p>
                        <p><strong>Prova:</strong> {prova}</p>
                        <p><strong>Ano:</strong> {ano}</p>
                        <p><strong>Banca:</strong> {banca}</p> 
                    </div>              
                </div>
            </div>
            <div class="baz">
                <a class="hide-action" href="#" style="margin-top: 10px; background-color: #DC3545; color: #fff; padding: 6px; border-radius: 5px;margin-left: 540px; margin-right: 45px;">
                    <i class="fas fa-times" style="margin-right: 5px; margin-left: 5px;"></i>Fechar
                </a>
            </div>
            </div>
            <div style="padding: 15px; margin: 5px 0; border-radius: 5px;" >
                <p>{enunciado}</p>
                <p>{questao}</p>
            </div>
            """, 
            unsafe_allow_html=True,
            )

            # Radio button para escolher a resposta
            resposta_usuario = st.radio(
                "",
                options=["Certo", "Errado"],
                key=f"resposta_radio_{questao_index}",
                help="",
                format_func=lambda x: f"**{x}**",
                index=None
            )
            #resposta_usuario = st.radio("", ["Certo", "Errado"], key=f"resposta_radio_{questao_index}", index=None)
            if st.form_submit_button("Confirmar Resposta"):
                if resposta_usuario:
                    mensagem = ""
                    if resposta_usuario == resposta_oficial:
                        mensagem = '<p><div class="resposta-mensagem resposta-correta">Parabéns! Sua resposta está correta.</div></p>'
                        st.session_state.acertos += 1
                    else:
                        mensagem = f'<p><div class="resposta-mensagem resposta-incorreta">Você errou! Gabarito: <strong>{resposta_oficial}</strong></div></p>'
                        st.session_state.erros += 1
                    
                else:
                    mensagem = 'Favor selecionar uma resposta'
                st.markdown(mensagem, unsafe_allow_html=True)
        
        # Adicionando um espaço para a mensagem de JavaScript
        st.markdown(
            """
            <script>
                // Esconde o comentário ao mudar de questão
                document.addEventListener('sessionStateChanged', function(event) {
                    // Desmarca o radio button ao mudar de questão
                    document.querySelectorAll('input[name^="resposta_usuario"]').forEach(function(radio) {
                        radio.checked = false;
                    });

                // Desmarca o radio button ao carregar a página
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('input[name^="resposta_usuario"]').forEach(function(radio) {
                        radio.checked = false;
                    });
                });
            </script>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <script>
                // Fecha o expander ao mudar de questão
                document.addEventListener('sessionStateChanged', function(event) {
                    var expander = document.querySelector('st.expander > .stDecoratedContent');
                    if (expander) {
                        expander.style.display = 'none';
                    }
                });
            </script>
            """,
            unsafe_allow_html=True
        )
        # Checkbox (Expander) para exibir o comentário
        # Checkbox (Expander) para exibir o comentário
        expander_id = f"expander_{questao_id}"
        expander_state = st.expander(f"Comentário - Questão {questao_index + 1}")
        with expander_state:
            if expander_state:
                if expander_id != st.session_state.get("expander_id", None):
                    st.session_state.expander_id = expander_id
                    st.markdown(
                        f"""
                        <script>
                            // Fecha o expander ao mudar de questão
                            document.addEventListener('sessionStateChanged', function(event) {{
                                var expanderId = event.detail.expander_id;
                                var currentExpanderId = '{expander_id}';
                                if (expanderId !== currentExpanderId) {{
                                    var expander = document.querySelector('.stExpander > .stDecoratedContent');
                                    if (expander) {{
                                        expander.style.display = 'none';
                                    }}
                                }}
                            }});
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                    expander_state.markdown("")
                st.markdown(
                    f"""
                    <div style="padding: 15px; margin: 10px 0; border-radius: 10px;">
                        <p>{Comentario}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True,
                    )
                

if __name__ == "__main__":
    main()
