import streamlit as st
import seaborn as sns
import pandas as pd
import altair as alt


st.set_page_config(
    page_title="Analysis on Threatened Species",
    page_icon="✅",
    layout="wide",
)

raw_data = pd.read_csv("UN_unprocessed_data_Threatened Species.csv",index_col=None, header=0, encoding='latin-1')

df_nature = raw_data.pivot(index= ["Code","Country","Year"], columns="Series", values="Value")
df_nature = df_nature.reset_index()
df_nature = df_nature.rename(columns={"Threatened Species: Invertebrates (number)": "Invertebrates",
    "Threatened Species: Plants (number)" : "Plants",
    "Threatened Species: Total (number)" : "Total",
    "Threatened Species: Vertebrates (number)" : "Vertebrates"})
df_nature = df_nature[['Code','Country', 'Year', "Invertebrates", "Vertebrates", "Plants", "Total"]]
labels_nature = df_nature.select_dtypes(include='float64').columns

tab1, tab2, tab3, tab4 = st.tabs(["Raw Data", "Univariate Analysis", "Bivariate Analysis","Findings"])

tab1.header("Understanding Data")
tab1.write("Data fetched from the United Nations website")
tab1.dataframe(raw_data)
tab1.write("Converting data for simpler access")
tab1.dataframe(df_nature)

 

uni_chart = ['Box Plot', 'Scatter Plot', 'Histogram','KDE']
hue_facet = ['None','Hue','Facet']


tab2.header("Diving into individual species")
tab2.dataframe(df_nature.drop(["Year", "Code"], axis= 1).describe())

x_axis_choice_uni = tab2.selectbox(
    "x axis",
    labels_nature)

chart_uni = tab2.selectbox(
    "Chart Type",
     uni_chart)

if chart_uni == "Box Plot":
        fig = alt.Chart(df_nature.drop(["Year", "Code"], axis= 1)).mark_boxplot().encode(
                x = x_axis_choice_uni
        ).interactive()
# elif chart_uni == "Scatter Plot":
#         fig = alt.Chart(df_nature.drop(["Year", "Code"], axis= 1)).mark_circle().encode(
#                 x= x_axis_choice_uni,
#                 y= x_axis_choice_uni,
#                 color = "Year"
#         ).interactive()
# elif chart_uni == 'Histogram':
#         fig = alt.Chart(df_nature.drop(["Year", "Code"], axis= 1)).mark_bar().encode(
#                 x = 'Year',
#                 y = x_axis_choice_uni
#         ).interactive()

else :
        fig = alt.Chart(df_nature).mark_area().encode(
                y = x_axis_choice_uni
        ).interactive()

tab2.altair_chart(fig) 
# uni_df = pd.DataFrame({
#     'x': x,
#     'y': y
#     })

bi_chart = ['scatter plot', 'histogram','KDE']
hue_facet = ['hue','facet']

cm = sns.light_palette("blue", as_cmap= True)

tab3.header("Is there any relation between them?")
tab3.dataframe(df_nature.drop(["Code","Year"], axis= 1).corr().style.background_gradient(cmap= cm))
x_axis_choice_bi = tab3.selectbox(
    "x axis bi",
    labels_nature)
y_axis_choice_bi = tab3.selectbox(
    "y axis bi",
    labels_nature)

tab4.header("Findings")


