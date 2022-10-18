import streamlit as st
import seaborn as sns
import pandas as pd
import altair as alt

def main():
    st.set_page_config(
    page_title="Analysis on Threatened Species",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="auto"
    )
    st.title('Nature is dying')
    st.sidebar.title('Explore the filters to play with and analyse the data')
    st.sidebar.markdown("Let's start by selecting what we wanna see?")
    st.sidebar.subheader("Choose Tab")
    
if __name__ == '__main__':
    main()

tab_select = st.sidebar.selectbox("tab_select",("Show Data","Univariate Analysis", "Bivariate Analysis","Findings"))   

@st.cache(persist= True)
def load():
    raw_data = pd.read_csv("UN_unprocessed_data_Threatened Species.csv",
                            index_col=None, header=0, encoding='latin-1')
    return raw_data
raw_data = load()

@st.cache(persist= True)
def transform_data(df):
    processed_data = df.pivot(index= ["Code","Country","Year"], columns="Series", values="Value")
    processed_data = processed_data.reset_index()
    processed_data = processed_data.rename(columns=
                                {"Threatened Species: Invertebrates (number)": "Invertebrates",
                                "Threatened Species: Plants (number)" : "Plants",
                                "Threatened Species: Total (number)" : "Total",
                                "Threatened Species: Vertebrates (number)" : "Vertebrates"})
    processed_data = processed_data[['Code','Country', 'Year', "Invertebrates", "Vertebrates", "Plants", "Total"]]
    return processed_data
processed_data = transform_data(raw_data)


def num_lab(df):
    num_lab = df.select_dtypes(include='float64').columns
    return num_lab

num_label = num_lab(processed_data)

def countries(df):
    country = df["Country"].unique()
    return country

country = countries(processed_data)

def side_bar(tab_select,num_label,country,processed_data):
    if tab_select == "Show Data":
        if st.sidebar.button("Click Me", key="click"):
            st.write("Data fetched from UN website")
            st.dataframe(raw_data)
            st.write("Transformed data")
            st.dataframe(processed_data)
    if tab_select == "Univariate Analysis":
        st.sidebar.subheader("Select the X parameter to analyse")
        x_axis_choice_uni = st.sidebar.selectbox("x axis",num_label,index= 0)
        hue_uni = st.sidebar.selectbox("Hue", ("None","Year"), index= 0)
        country_uni = st.sidebar.multiselect("Country", ("All",country),default="All")
        chart_uni = st.sidebar.selectbox("Select Chart to display", ("Box Plot",'Histogram','KDE'))
        if st.sidebar.button("Click Me", key= "click"):
            st.subheader("Looking at the basic stats")
            st.dataframe(processed_data.drop(["Year", "Code"], axis= 1).describe())
    if tab_select == "Bivariate Analysis":
        st.sidebar.subheader("Select the X and Y parameter to analyse")
        x_axis_choice_bi = st.sidebar.selectbox("x axis",num_label,index= 0)
        y_axis_choice_bi = st.sidebar.selectbox("y axis",num_label,index= 1)
        hue_bi = st.sidebar.selectbox("Hue", ("None","Year"),index= 0)
        country_bi = st.sidebar.multiselect("Country", country)
        chart_bi = st.sidebar.selectbox("Select Chart to display", ("Scatter Plot",'Histogram','KDE'))
        if st.sidebar.button("Click Me", key= "click"):
            cm = sns.light_palette("blue", as_cmap= True)
            st.subheader("Lets look at the correlation first!")
            st.dataframe(processed_data.drop(["Code","Year"], axis= 1).corr().style.background_gradient(cmap= cm))
    if tab_select == "Findings":
        st.sidebar.subheader("Read Through")

side_bar = side_bar(tab_select,num_label,country,processed_data)
