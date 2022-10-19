import streamlit as st
import seaborn as sns
import pandas as pd
import altair as alt
import numpy as np

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
    st.sidebar.subheader("Press click to visualize")
       

if __name__ == '__main__':
    main()


tab_select = st.sidebar.selectbox("Choose Tab",\
        ["Show Data","Univariate Analysis", "Bivariate Analysis","Findings"])

@st.cache(persist= True)
def load():
    raw_data = pd.read_csv("UN_unprocessed_data_Threatened Species.csv",
                            index_col=None, header=0, encoding='latin-1')
    return raw_data
raw_data = load()

@st.cache(persist= True)
def transform_data(df):
    processed_data = df.pivot(index= ["Code","Country","Year"],\
         columns="Series", values="Value")
    processed_data = processed_data.reset_index()
    processed_data = processed_data.rename(columns=
                                {"Threatened Species: Invertebrates (number)": "Invertebrates",
                                "Threatened Species: Plants (number)" : "Plants",
                                "Threatened Species: Total (number)" : "Total",
                                "Threatened Species: Vertebrates (number)" : "Vertebrates"})
    processed_data = processed_data[['Code','Country', 'Year',\
         "Invertebrates", "Vertebrates", "Plants", "Total"]].dropna()
    return processed_data
processed_data = transform_data(raw_data)

@st.cache(persist= True)
def num_lab(df):
    num_lab = df.select_dtypes(include='float64').columns
    return num_lab

num_label = num_lab(processed_data)

@st.cache(persist= True)
def countries(df):
    country = df["Country"].unique()
    country = np.append(country,"All")
    return country

country_label = countries(processed_data)



def side_bar(tab_select):
    if tab_select == "Show Data":
        if st.sidebar.button("Click Me", key="click"):
            st.write("Data fetched from UN website")
            st.dataframe(raw_data,width=600,height= 500)
            st.write("Data after transformation and cleaning.")
            st.dataframe(processed_data,width=600,height= 500)
    if tab_select == "Univariate Analysis":
        st.sidebar.subheader("Select the X parameter to analyse")
        x_axis_choice_uni = st.sidebar.selectbox("x axis",num_label,index= 0)
        hue_uni = st.sidebar.selectbox("Hue", ["None","Year"], index= 0)
        country_uni = st.sidebar.multiselect("Country",  country_label, default= "All")
        chart_uni = st.sidebar.selectbox("Select Chart to display", ["KDE",'Histogram','Box','Violin','Rug'])
        if st.sidebar.button("Click Me", key= "click"):
            st.subheader("Looking at the basic stats")
            st.dataframe(processed_data.drop(["Year", "Code"], axis= 1).describe())
            d_uni = data_uni(country_uni)
            chart_plot_uni = chart_func_uni(d_uni,chart_uni,x_axis_choice_uni)            
            st.write(chart_plot_uni)
        #     st.markdown()

    if tab_select == "Bivariate Analysis":
        st.sidebar.subheader("Select the X and Y parameter to analyse")
        x_axis_choice_bi = st.sidebar.selectbox("x axis",num_label,index= 0)
        y_axis_choice_bi = st.sidebar.selectbox("y axis",num_label,index= 1)
        hue_bi = st.sidebar.selectbox("Hue", ["None","Year"],index= 0)
        country_bi = st.sidebar.multiselect("Country", country_label, default= "All")
        chart_bi = st.sidebar.selectbox("Select Chart to display", ["KDE (Joint Probability)",'Scatter','Line','Regression Line'])
        if st.sidebar.button("Click Me", key= "click"):
            cm = sns.light_palette("blue", as_cmap= True)
            st.subheader("Lets look at the correlation first!")
            st.dataframe(processed_data.drop(["Code","Year"], axis= 1).corr().style.background_gradient(cmap= cm))
            d_bi = data_bi(country_bi)
        #     chart_bi = chart_bi(d_bi)            
        #     st.altair_chart(chart_bi)
        #     st.markdown()
        
    if tab_select == "Findings":
        st.sidebar.subheader("Read Through")


def data_uni(country_uni):
        if ("All" in country_uni) :
                data_uni = processed_data
        else :
                data_uni = processed_data.where(processed_data.Country.isin(country_uni)).dropna()
        return data_uni

def data_bi(country_bi):
        if ("All" in country_bi) :
                data_bi = processed_data
        else :
                data_bi = processed_data.where(processed_data.Country.isin(country_bi)).dropna()
        return data_bi


def chart_func_uni(df,chart_uni,x_axis_choice_uni):
        if (chart_uni == "KDE"):
                chart = alt.Chart(df,width=600, height=500).transform_density(
                                f'{x_axis_choice_uni}',
                                as_= [f'{x_axis_choice_uni}', "Density"],
                        ).mark_area(
                                color = 'blue', opacity = 0.3
                        ).encode(
                                x= f'{x_axis_choice_uni}'+":Q",
                                y= 'Density:Q',
                        ).interactive()
                return chart
        if (chart_uni == "Histogram"):
                chart = alt.Chart(df,width=600, height=500).mark_bar().encode(
                                alt.X( f'{x_axis_choice_uni}'+":Q",
                                # bin=alt.Bin(extent=[0, df[f'{x_axis_choice_uni}'].max()], step=df[f'{x_axis_choice_uni}'].max()/len(df)/2)),
                                ),
                                y='count()',
                        ).interactive()
                return chart
        if (chart_uni == "Box"):
                chart = alt.Chart(df,width=600, height=500).mark_boxplot().encode(
                                alt.Y( f'{x_axis_choice_uni}'+":Q",
                                # bin=alt.Bin(extent=[0, df[f'{x_axis_choice_uni}'].max()], step=df[f'{x_axis_choice_uni}'].max()/len(df)/2)),
                                ),
                                x='Year:O',
                        ).interactive()
                return chart
        if (chart_uni == "Violin"):
                chart = alt.Chart(processed_data).transform_density(
                                f'{x_axis_choice_uni}',
                                as_=[f'{x_axis_choice_uni}', 'density'],
                                groupby=['Year']
                        ).mark_area(orient='horizontal').encode(
                                y=f'{x_axis_choice_uni}'+":Q",
                                color='Year:N',
                                x=alt.X(
                                        'density:Q',
                                        stack='center',
                                        impute=None,
                                        title=None,
                                        axis=alt.Axis(labels=False, values=[0],grid=False, ticks=True),
                                ),
                                column=alt.Column(
                                        'Year:N',
                                        header=alt.Header(
                                        titleOrient='bottom',
                                        labelOrient='bottom',
                                        labelPadding=0,
                                        ),
                                )
                        ).properties(
                                width=100
                        ).configure_facet(
                                spacing=0
                        ).configure_view(
                                stroke=None
                        ).interactive()
                return chart
        if (chart_uni == "Rug"):
                chart = alt.Chart(df,width=600, height=500).mark_bar().encode(
                                alt.X( f'{x_axis_choice_uni}'+":Q",
                                # bin=alt.Bin(extent=[0, df[f'{x_axis_choice_uni}'].max()], step=df[f'{x_axis_choice_uni}'].max()/len(df)/2)),
                                ),
                                y='count()',
                        ).interactive()
                return chart




# def chart_func_bi(df):



side_bar = side_bar(tab_select)
