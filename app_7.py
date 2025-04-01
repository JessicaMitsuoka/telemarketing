import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

@st.cache_data(show_spinner= True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    processed_data = output.getvalue()
    return processed_data

st.set_page_config(page_title = 'Telemarketing analisys', \
    page_icon = '/Users/jessicamitsuoka/Downloads/Material_de_apoio_M19_Cientista de Dados-2/img/telmarketing_icon.png',
    layout="wide",
    initial_sidebar_state='expanded'
)

st.write('# Telemarketing analisys')
st.markdown("---")

st.sidebar.image("/Users/jessicamitsuoka/Downloads/Material_de_apoio_M19_Cientista de Dados-2/img/Bank-Branding.jpg")

st.sidebar.write("## Suba o arquivo")
data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

graph_type = None  # Garante que a variável existe antes do formulário

if data_file_1 is not None:
    bank_raw = load_data(data_file_1)
    bank = bank_raw.copy()

    st.write('## Antes dos filtros')
    st.write(bank_raw.head())

    with st.sidebar.form(key='my_form'):  # 🔹 Mantemos o radio dentro desse form
        graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))  # 🔹 ÚNICA OCORRÊNCIA
       
        max_age = int(bank.age.max())
        min_age = int(bank.age.min())
        idades = st.slider(label='Idade', 
                           min_value=min_age,
                           max_value=max_age, 
                           value=(min_age, max_age),
                           step=1)

        jobs_list = bank.job.unique().tolist()
        jobs_list.append('all')
        jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

        marital_list = bank.marital.unique().tolist()
        marital_list.append('all')
        marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

        default_list = bank.default.unique().tolist()
        default_list.append('all')
        default_selected = st.multiselect("Default", default_list, ['all'])

        housing_list = bank.housing.unique().tolist()
        housing_list.append('all')
        housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

        loan_list = bank.loan.unique().tolist()
        loan_list.append('all')
        loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

        contact_list = bank.contact.unique().tolist()
        contact_list.append('all')
        contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

        month_list = bank.month.unique().tolist()
        month_list.append('all')
        month_selected = st.multiselect("Mês do contato", month_list, ['all'])

        day_of_week_list = bank.day_of_week.unique().tolist()
        day_of_week_list.append('all')
        day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

        bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                    .pipe(multiselect_filter, 'job', jobs_selected)
                    .pipe(multiselect_filter, 'marital', marital_selected)
                    .pipe(multiselect_filter, 'default', default_selected)
                    .pipe(multiselect_filter, 'housing', housing_selected)
                    .pipe(multiselect_filter, 'loan', loan_selected)
                    .pipe(multiselect_filter, 'contact', contact_selected)
                    .pipe(multiselect_filter, 'month', month_selected)
                    .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
        )

        submit_button = st.form_submit_button(label='Aplicar')  # 🔹 Mantém o botão de submissão

    st.write('## Após os filtros')
    st.write(bank.head())

    st.markdown("---")

    st.write('## Proporção de aceite')

    if bank_raw['y'].empty or bank['y'].empty:
        st.error("Erro: Nenhum dado disponível para gerar o gráfico.")
    elif graph_type:  # 🔹 Só mostra os gráficos se um tipo foi selecionado
        fig, ax = plt.subplots(1, 2, figsize=(10, 8))

        if graph_type == 'Barras':
            sns.barplot(x=bank_raw['y'].value_counts(normalize=True).index, 
                        y=bank_raw['y'].value_counts(normalize=True).values, 
                        ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados Brutos', fontweight="bold")

            sns.barplot(x=bank['y'].value_counts(normalize=True).index, 
                        y=bank['y'].value_counts(normalize=True).values, 
                        ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados Filtrados', fontweight="bold")

        elif graph_type == 'Pizza':
            ax[0].pie(bank_raw['y'].value_counts(normalize=True), 
                      labels=bank_raw['y'].value_counts(normalize=True).index, 
                      autopct='%.2f%%')
            ax[0].set_title('Dados brutos', fontweight="bold")
            
            ax[1].pie(bank['y'].value_counts(normalize=True), 
                      labels=bank['y'].value_counts(normalize=True).index, 
                      autopct='%.2f%%')
            ax[1].set_title('Dados filtrados', fontweight="bold")

        st.pyplot(fig)  # 🔹 Mostra os gráficos














