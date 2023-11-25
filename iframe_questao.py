import streamlit as st
import mysql.connector

# Configurações de conexão
config = {
    'user': 'admin',
    'password': 'Eduardo13*',
    'host': 'institutoscheffelt.clazmf0mr7c4.sa-east-1.rds.amazonaws.com',
    'database': 'questoes',
    'raise_on_warnings': True
}

# Função para obter todas as questões com base no assunto
def obter_questoes_por_assunto(assunto):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Consulta para recuperar todas as questões com um assunto específico
        cursor.execute("""
            SELECT Q.QuestaoID, Q.Enunciado, Q.Questao, Q.Resposta_Oficial, Q.Gabarito_Comentado, Q.Comentario, A.Assunto
            FROM Questoes Q
            JOIN Assuntos A ON Q.AssuntoID = A.AssuntoID
            WHERE A.Assunto = %s;
        """, (assunto,))

        # Recuperar os resultados
        resultados = cursor.fetchall()
        return resultados

    except Exception as e:
        st.error(f"Erro ao obter questões: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

# Função principal do dashboard
def main():
    st.set_page_config(page_title="Revisão de Questões", page_icon=":pencil:")

    st.title("Revisão de Questões")

    # Filtro de assunto na URL
    params = st.experimental_get_query_params()
    assunto_selecionado = params.get("assunto", ["Mérito Administrativo"])[0]
    # Adicionando um espaço para a mensagem de JavaScript
    st.markdown(
        """
        <script>
            // Esconde o comentário ao mudar de questão
            document.addEventListener('sessionStateChanged', function(event) {
                // Desmarca o radio button ao mudar de questão
                document.querySelectorAll('input[name^="resposta_radio"]').forEach(radio => {
                    radio.checked = false;
                });
            });

            // Desmarca o radio button ao carregar a página
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('input[name^="resposta_radio"]').forEach(radio => {
                    radio.checked = false;
                });
            });
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Exibir todas as questões cadastradas com base no assunto selecionado
    questoes_cadastradas = obter_questoes_por_assunto(assunto_selecionado)

    # Controlar o índice da questão
    questao_index = st.session_state.get("questao_index", 0)
    total_questoes = len(questoes_cadastradas)

    # Botões para navegar entre as questões
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Questão Anterior") and questao_index > 0:
            questao_index -= 1
            st.session_state.questao_index = questao_index

    with col2:
        numero_questao_placeholder = st.empty()  # Placeholder para o número da questão
        numero_questao_placeholder.write(f"Questão Atual: {questao_index + 1}/{total_questoes}")

    with col3:
        if st.button("Próxima Questão") and questao_index < total_questoes - 1:
            questao_index += 1
            st.session_state.questao_index = questao_index

    # Selecionar a questão atual
    questao_id, enunciado, questao, resposta_oficial, gabarito_comentado, comentario, assunto = questoes_cadastradas[questao_index]

    # Exibir detalhes da questão
    st.subheader("Detalhes da Questão:")
    st.write(f"ID: {questao_id}")
    st.write(f"Enunciado: {enunciado}")
    st.write(f"Questão: {questao}")

    # Radio button para escolher a resposta
    resposta_usuario = st.radio("Sua Resposta:", ["Certo", "Errado"], key=f"resposta_radio_{questao_index}", index=None)

    # Botão para confirmar a resposta
    if st.button("Confirmar Resposta"):
        # Verificar se a resposta está correta
        if resposta_usuario:
            if resposta_usuario == resposta_oficial:
                st.success("Parabéns! Sua resposta está correta.")
            else:
                st.error("Ops! Sua resposta está incorreta. Tente novamente.")

    # Checkbox (Expander) para exibir o comentário
    with st.expander("Comentário"):
        st.write(f"Comentário: {comentario}")



if __name__ == "__main__":
    main()
