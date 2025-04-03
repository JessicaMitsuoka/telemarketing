import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Substituições de cache:
@st.cache_data(show_spinner=True)  # Para dados que podem ser serializados
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_data  # Para operações com dados
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

@st.cache_data  # Para conversão de DataFrame
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data  # Para criação de arquivo Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


def main():
    st.set_page_config(
        page_title='Telemarketing analisys',
        page_icon='telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )

    st.write('# Telemarketing analisys')
    st.markdown("---")
    
    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
        
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(
                label='Idade',
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age),
                step=1
            )

            # Listas de seleção
            def get_filter_options(column):
                options = bank[column].unique().tolist()
                options.append('all')
                return options

            jobs_selected = st.multiselect("Profissão", get_filter_options('job'), ['all'])
            marital_selected = st.multiselect("Estado civil", get_filter_options('marital'), ['all'])
            default_selected = st.multiselect("Default", get_filter_options('default'), ['all'])
            housing_selected = st.multiselect("Tem financiamento imob?", get_filter_options('housing'), ['all'])
            loan_selected = st.multiselect("Tem empréstimo?", get_filter_options('loan'), ['all'])
            contact_selected = st.multiselect("Meio de contato", get_filter_options('contact'), ['all'])
            month_selected = st.multiselect("Mês do contato", get_filter_options('month'), ['all'])
            day_of_week_selected = st.multiselect("Dia da semana", get_filter_options('day_of_week'), ['all'])

            submit_button = st.form_submit_button(label='Aplicar')
        
        # Aplicando filtros
        bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                .pipe(multiselect_filter, 'job', jobs_selected)
                .pipe(multiselect_filter, 'marital', marital_selected)
                .pipe(multiselect_filter, 'default', default_selected)
                .pipe(multiselect_filter, 'housing', housing_selected)
                .pipe(multiselect_filter, 'loan', loan_selected)
                .pipe(multiselect_filter, 'contact', contact_selected)
                .pipe(multiselect_filter, 'month', month_selected)
                .pipe(multiselect_filter, 'day_of_week', day_of_week_selected))
        
        st.write('## Após os filtros')
        st.write(bank.head())
        
        df_xlsx = to_excel(bank)
        st.download_button(
            label='📥 Download tabela filtrada em EXCEL',
            data=df_xlsx,
            file_name='bank_filtered.xlsx'
        )
        st.markdown("---")

        # Análise de proporção
        fig, ax = plt.subplots(1, 2, figsize=(5, 3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame()*100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()
        
        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame()*100
            bank_target_perc = bank_target_perc.sort_index()
        except:
            st.error('Erro no filtro')
        
        col1, col2 = st.columns(2)

        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(
            label='📥 Download',
            data=to_excel(bank_raw_target_perc),
            file_name='bank_raw_y.xlsx'
        )
        
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(
            label='📥 Download',
            data=to_excel(bank_target_perc),
            file_name='bank_y.xlsx'
        )
        st.markdown("---")
    
        st.write('## Proporção de aceite')
     
        if graph_type == 'Barras':
            sns.barplot(x=bank_raw_target_perc.index, 
                        y='y',
                        data=bank_raw_target_perc, 
                        ax=ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos', fontweight="bold")
            
            sns.barplot(x=bank_target_perc.index, 
                        y='y', 
                        data=bank_target_perc, 
                        ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados', fontweight="bold")
        else:
            bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[0])
            ax[0].set_title('Dados brutos', fontweight="bold")
            
            bank_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax=ax[1])
            ax[1].set_title('Dados filtrados', fontweight="bold")

        st.pyplot(fig)

if __name__ == '__main__':
    main()

    














