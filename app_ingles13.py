# -*- coding: utf-8 -*-
"""app_ingles13.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PK3dWBKXTFPiUzahpf4h0Y0l3t7raSzC
"""

import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd
from data_exercises import all_exercises_data, grammar_tips

st.set_page_config(page_title="App de Aprendizado de Inglês", layout="centered")

st.title("📚 App de Aprendizado de Inglês")

# --- Constantes ---
NUM_EXERCISES_PER_LEVEL = 15

# --- Funções de gerenciamento de estado ---
def _initialize_exercise_state(level, exercises):
    """Inicializa ou reinicializa o estado do exercício para um novo nível ou sessão."""
    # Garante que não pegamos mais exercícios do que o disponível
    num_to_sample = min(NUM_EXERCISES_PER_LEVEL, len(exercises))

    shuffled_exercises_for_level = random.sample(exercises, num_to_sample)
    # Pré-embaralha as opções de cada exercício UMA VEZ
    for exercise in shuffled_exercises_for_level:
        if "opcoes" in exercise and isinstance(exercise["opcoes"], list):
            exercise['shuffled_options'] = random.sample(exercise["opcoes"], len(exercise["opcoes"])) # Embaralha e guarda

    st.session_state.exercise_data = {
        'current_level': level,
        'index': 0,
        'shuffled': shuffled_exercises_for_level,
        'selected_option': None,
        'feedback': '',
        'show_answer': False,
        'show_tip': False,
        'correct_count': 0,
        'incorrect_count': 0,
        'current_answered': False # Renomeado para clareza
    }

def _next_exercise():
    """Avança para o próximo exercício."""
    current_index = st.session_state.exercise_data['index']
    total_exercises = len(st.session_state.exercise_data['shuffled'])

    if current_index + 1 >= total_exercises:
        st.session_state.exercise_data['index'] = total_exercises # Marca como "finalizado"
        st.session_state.exercise_data['selected_option'] = None
        st.session_state.exercise_data['feedback'] = ''
        st.session_state.exercise_data['show_answer'] = False
        st.session_state.exercise_data['show_tip'] = False
        st.session_state.exercise_data['current_answered'] = False
        st.session_state['quiz_finished'] = True # Sinaliza que o quiz terminou
        return

    st.session_state.exercise_data.update({
        'index': (current_index + 1),
        'selected_option': None, # Reseta a opção selecionada para o novo exercício
        'feedback': '',
        'show_answer': False,
        'show_tip': False,
        'current_answered': False
    })

def _check_answer(correct_answer):
    """Verifica a resposta do usuário e atualiza o feedback."""
    if st.session_state.exercise_data['current_answered']:
        return

    user_selected_option = st.session_state.exercise_data['selected_option']

    if user_selected_option is None:
        st.session_state.exercise_data['feedback'] = "Por favor, selecione uma opção antes de verificar."
        st.session_state.exercise_data['show_answer'] = True
        st.session_state.exercise_data['show_tip'] = False
        return

    if user_selected_option.strip().lower() == correct_answer.lower():
        st.session_state.exercise_data['feedback'] = "✅ Correto!"
        st.session_state.exercise_data['correct_count'] += 1
    else:
        st.session_state.exercise_data['feedback'] = f"❌ Incorreto. Resposta correta: **{correct_answer}**"
        st.session_state.exercise_data['incorrect_count'] += 1

    st.session_state.exercise_data['show_answer'] = True
    st.session_state.exercise_data['show_tip'] = False
    st.session_state.exercise_data['current_answered'] = True

def _show_grammar_tip(grammar_type):
    """Exibe a dica de gramática."""
    tip = grammar_tips.get(grammar_type, "Não há uma dica específica para este tipo de gramática.")
    st.session_state.exercise_data['feedback'] = f"**Dica sobre {grammar_type}:** {tip}"
    st.session_state.exercise_data['show_answer'] = True
    st.session_state.exercise_data['show_tip'] = True

# --- Mensagens Motivacionais ---
motivational_messages = {
    "high": [
        "Fantastic job! Your dedication is truly paying off. Keep up the excellent work! ✨",
        "Outstanding! You're making great progress and mastering these concepts. Celebrate your success! 🏆",
        "Brilliant! Your hard work shines through. The sky's the limit for your English skills! 🚀",
        "Exceptional performance! You're clearly committed to fluency. Keep pushing forward! 💪"
    ],
    "low": [
        "Every mistake is a lesson in disguise. Keep practicing, and you'll see amazing improvement! 🌟",
        "Don't give up! Learning a language is a journey, not a race. Your effort will lead to success. 🌱",
        "You're making progress, even if it feels slow. Consistency is key! Keep learning and growing. 📈",
        "Stay positive! Challenges are opportunities to grow. Keep reviewing and challenging yourself. You've got this! resilience 💪"
    ]
}

def get_motivational_message(score_percentage):
    """Retorna uma mensagem motivacional com base na porcentagem de acerto."""
    if score_percentage >= 70:
        return random.choice(motivational_messages["high"])
    else:
        return random.choice(motivational_messages["low"])

# --- Sidebar ---
st.sidebar.header("Configurações do Exercício")
level = st.sidebar.selectbox("Selecione o Nível:",
                             options=list(all_exercises_data.keys()),
                             index=0)

# Verificação de segurança dos níveis disponíveis
if level not in all_exercises_data:
    st.error("Nível selecionado não existe nos dados!")
    st.stop()

# Carrega os exercícios para o nível selecionado
try:
    all_level_exercises = all_exercises_data[level]["Completar Frases"]
except KeyError as e:
    st.error(f"Erro na estrutura de dados: {str(e)}")
    st.stop()

if not all_level_exercises:
    st.warning(f"Não há exercícios para o nível '{level}' ainda.")
    st.stop()

# Inicializa o estado se for a primeira vez ou se o nível mudou
if 'exercise_data' not in st.session_state or st.session_state.exercise_data['current_level'] != level:
    _initialize_exercise_state(level, all_level_exercises)
    st.session_state['quiz_finished'] = False

# --- Gráfico de Pizza de Acertos/Erros (na sidebar) ---
st.sidebar.subheader("Resultados Atuais")
total_answered = st.session_state.exercise_data['correct_count'] + st.session_state.exercise_data['incorrect_count']

if total_answered > 0:
    labels = ['Acertos', 'Erros']
    sizes = [st.session_state.exercise_data['correct_count'], st.session_state.exercise_data['incorrect_count']]
    colors = ['#4CAF50', '#F44336'] # Verde para acertos, Vermelho para erros
    explode = (0.1, 0) # explode 1st slice

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            colors=colors, shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.sidebar.pyplot(fig1)

    st.sidebar.write(f"**Acertos:** {st.session_state.exercise_data['correct_count']}")
    st.sidebar.write(f"**Erros:** {st.session_state.exercise_data['incorrect_count']}")
else:
    st.sidebar.info("Comece a responder para ver seus resultados!")

st.sidebar.write("---") # Linha divisória

# --- Lógica de exibição principal dos exercícios ---

current_exercise_index = st.session_state.exercise_data['index']
shuffled_exercises = st.session_state.exercise_data['shuffled']
total_exercises_in_batch = len(shuffled_exercises)

if st.session_state.get('quiz_finished') and current_exercise_index >= total_exercises_in_batch:
    # Quiz finalizado, exibe resultados e mensagem motivacional
    st.success("🎉 Parabéns! Você completou todos os exercícios deste nível!")
    final_correct = st.session_state.exercise_data['correct_count']
    final_total = total_exercises_in_batch

    if final_total > 0:
        score_percentage = (final_correct / final_total) * 100
        st.metric(label="Sua Pontuação Final", value=f"{score_percentage:.1f}%")
        st.write("---")
        st.subheader("Keep Going!")
        st.info(get_motivational_message(score_percentage))
    else:
        st.info("Nenhum exercício foi respondido neste nível.")

    if st.button("🔄 Recomeçar este Nível"):
        _initialize_exercise_state(level, all_level_exercises)
        st.session_state['quiz_finished'] = False
        st.rerun()

    st.write("---")
    st.info("Para continuar, selecione outro nível na barra lateral ou recomece este.")

else:
    # Continua exibindo os exercícios
    current_exercise = shuffled_exercises[current_exercise_index]

    # --- Verificação da existência de opções ---
    # Agora verifica por 'shuffled_options' que criamos na inicialização
    if "shuffled_options" not in current_exercise or not isinstance(current_exercise["shuffled_options"], list) or len(current_exercise["shuffled_options"]) < 4:
        st.error(f"Erro: O exercício para '{current_exercise['frase']}' não possui a lista de opções embaralhadas completa (4 opções esperadas). Verifique seu `data_exercises.py` ou a inicialização.")
        st.stop()

    st.subheader(f"Nível: {level} - Completar Frases")
    st.markdown(f"**Tipo de Gramática:** 🎯 *{current_exercise['tipo']}*")
    st.write("---")

    st.markdown(f"### Complete a frase:")
    st.markdown(f"## **`{current_exercise['frase']}`**")

    # --- Usando as opções pré-embaralhadas ---
    display_options = current_exercise["shuffled_options"]

    # Determina o index_padrão para manter a seleção.
    # Se uma opção já foi selecionada para o exercício atual, encontra seu índice.
    default_index = None
    if st.session_state.exercise_data['selected_option'] is not None:
        try:
            default_index = display_options.index(st.session_state.exercise_data['selected_option'])
        except ValueError:
            default_index = None # A opção selecionada não está nas opções atuais (não deveria acontecer)

    # st.radio para seleção de múltipla escolha
    selected_option_radio = st.radio(
        "Selecione a resposta correta:",
        options=display_options,
        index=default_index, # Usa o índice padrão
        key=f"opcoes_{st.session_state.exercise_data['index']}"
    )

    # Atualiza o session_state.exercise_data['selected_option']
    # Apenas se a seleção no radio mudou E o quiz não foi respondido ainda para o exercício atual
    if selected_option_radio != st.session_state.exercise_data['selected_option'] and not st.session_state.exercise_data['current_answered']:
        st.session_state.exercise_data['selected_option'] = selected_option_radio
        # Ao mudar a seleção, podemos querer resetar feedback e dica
        st.session_state.exercise_data['feedback'] = ''
        st.session_state.exercise_data['show_answer'] = False
        st.session_state.exercise_data['show_tip'] = False
        # Não é necessário st.rerun() aqui, o Streamlit já rerenderiza na interação do radio
        # e o on_change já não está sendo usado. A lógica de atualização é direta.

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button(
            "✅ Verificar",
            on_click=_check_answer,
            args=(current_exercise['resposta_correta'],),
            disabled=st.session_state.exercise_data['current_answered'] or st.session_state.exercise_data['selected_option'] is None
        )

    with col2:
        st.button(
            "⏭️ Próximo",
            on_click=_next_exercise,
            disabled=not st.session_state.exercise_data['current_answered']
        )

    with col3:
        st.button(
            "💡 Dica de Gramática",
            on_click=_show_grammar_tip, # <-- CORRIGIDO AQUI!
            args=(current_exercise['tipo'],),
            disabled=st.session_state.exercise_data['show_tip']
        )

    # --- Exibição de Feedback/Dica ---
    if st.session_state.exercise_data['show_answer']:
        if st.session_state.exercise_data['show_tip']:
            st.info(st.session_state.exercise_data['feedback'])
        else:
            st.markdown(f"**Feedback:** {st.session_state.exercise_data['feedback']}")

    # Contador de progresso
    st.write("---")
    st.caption(f"Progresso: {current_exercise_index + 1}/{total_exercises_in_batch} exercícios")