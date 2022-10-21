import streamlit as st
import seaborn as sns
import pandas as pd
import altair as alt
import numpy as np

def main():
    st.set_page_config(
    page_title="Analysis on Threatened Species",
    page_icon="✅",
    layout="wide",
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


def num_lab(df):
    num_lab = df.select_dtypes(include='float64').columns
    return num_lab

num_label = num_lab(processed_data)


def countries(df):
    country = df["Country"].unique()
    country = np.append(country,"All")
    return country

country_label = countries(processed_data)



def side_bar(tab_select):
    if tab_select == "Show Data":
        radio_data = st.sidebar.radio("Select options below",["Raw Data", "Transformed Data", "Basic Statistics","Correlation Plot"],index=0)
        if st.sidebar.button("Click Me", key="click"):
            show_data(radio_data)
    if tab_select == "Univariate Analysis":
        st.sidebar.subheader("Select the X parameter to analyse")
        x_axis_choice_uni = st.sidebar.selectbox("x axis",num_label,index= 0)
        hue_uni = st.sidebar.selectbox("Hue", ["None","Year"], index= 0)
        country_uni = st.sidebar.multiselect("Country",  country_label, default= "All")
        chart_uni = st.sidebar.selectbox("Select Chart to display", ["KDE","Log-Normal",'Histogram','Box','Violin'])
        if st.sidebar.button("Click Me", key= "click"):
            d_uni = data_uni(country_uni)
            log_df = log_transform(country_uni)
            chart_plot_uni = chart_func_uni(d_uni,log_df,chart_uni,x_axis_choice_uni,hue_uni)            
            st.write(chart_plot_uni)

    if tab_select == "Bivariate Analysis":
        st.sidebar.subheader("Select the X and Y parameter to analyse")
        x_axis_choice_bi = st.sidebar.selectbox("x axis",num_label,index= 0)
        y_axis_choice_bi = st.sidebar.selectbox("y axis",num_label,index= 1)
        hue_bi = st.sidebar.selectbox("Hue", ["None","Year"],index= 0)
        country_bi = st.sidebar.multiselect("Country", country_label, default= "All")
        chart_bi = st.sidebar.selectbox("Select Chart to display", ["KDE (Joint Probability)",'Scatter','Line','Regression Line'])
        if st.sidebar.button("Click Me", key= "click"):
            d_bi = data_bi(country_bi)
            chart_plot_bi = chart_func_bi(d_bi,chart_bi,x_axis_choice_bi,y_axis_choice_bi,hue_bi)            
            st.write(chart_plot_bi)
        
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


def log_transform(country_uni):
        if ("All" in country_uni) :
                df = processed_data
        else :
                df = processed_data.where(processed_data.Country.isin(country_uni)).dropna()
        np.seterr(divide = 'ignore')
        df.iloc[:,3:]= df.iloc[:,3:].astype(float)  
        df.replace(0,0.1,inplace=True)
        df.iloc[:,3:]= df.iloc[:, 3:].apply(np.log)
        df.replace(np.log(0.1),0.0,inplace=True)
        return df

def show_data(radio_data):
        if (radio_data == "Raw Data"):
                output = st.dataframe(raw_data,width=600)
                return output
        if (radio_data == "Transformed Data"):
                output = st.dataframe(processed_data,width=600)
                return output
        if (radio_data == "Basic Statistics"):
                output = st.dataframe(processed_data.drop(["Year", "Code"], axis= 1).describe(),width=600)
                return output
        if (radio_data == "Correlation Plot"):
                cm = sns.light_palette("lightblue", as_cmap= True)
                output = st.dataframe(processed_data.drop(["Code","Year"], axis= 1).corr().style.background_gradient(cmap= cm),width=600)
                return output
        else :
                return 0


def chart_func_uni(df,log_df,chart_uni,x_axis_choice_uni,hue_uni):
        if (chart_uni == "KDE"):
                if (hue_uni == "None"):
                        chart = alt.Chart(df ,title = f'{x_axis_choice_uni}' + " vs Density",width=600, height=500).transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_= [f'{x_axis_choice_uni}', "Density"],
                                ).mark_area(
                                        color = 'red', opacity = 0.3
                                ).encode(
                                        x= alt.X(f'{x_axis_choice_uni}'+":Q",
                                                stack='center',
                                                impute=None,
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        y= alt.Y('Density:Q',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ), 
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q", "Density:Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                else:
                        chart = alt.Chart(df,title = f'{x_axis_choice_uni}' + " vs Density",width=150, height=250).transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_= [f'{x_axis_choice_uni}', "Density"],
                                        groupby=['Year']
                                ).mark_area(
                                        opacity = 0.3
                                ).encode(
                                        x= alt.X(f'{x_axis_choice_uni}'+":Q",
                                                stack='center',
                                                impute=None,
                                                title= None,
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        y= alt.Y('Density:Q',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        color = alt.Color("Year:N", legend= None),
                                        column=alt.Column(
                                                'Year:N',
                                                header=alt.Header(
                                                titleOrient='bottom',
                                                labelOrient='bottom',
                                                labelPadding=0,
                                                ),
                                        ),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q", "Density:Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive() 
                return chart
        if (chart_uni == "Log-Normal"):  
                if (hue_uni == "None"):
                        chart = alt.Chart(log_df ,title = f'{x_axis_choice_uni}' + " vs Log-Normal Density",width=600, height=500).transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_= [f'{x_axis_choice_uni}', "Density"],
                                ).mark_area(
                                        color = 'red', opacity = 0.3
                                ).encode(
                                        x= alt.X(f'{x_axis_choice_uni}'+ ":Q",
                                                stack='center',
                                                impute=None,
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        y= alt.Y('Density:Q',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q", "Density:Q"], 
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                else :
                        chart = alt.Chart(log_df, title = f'{x_axis_choice_uni}' + " vs Log-Normal Density" ,width=150, height=250).transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_= [f'{x_axis_choice_uni}', "Density"],
                                        groupby=['Year']
                                ).mark_area(
                                        opacity = 0.3
                                ).encode(
                                        x= alt.X(f'{x_axis_choice_uni}'+ ":Q",
                                                stack='center',
                                                impute=None,
                                                title= None,
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        y= alt.Y('Density:Q',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        color = alt.Color("Year:N", legend= None),
                                        column=alt.Column(
                                                'Year:N',
                                                header=alt.Header(
                                                titleOrient='bottom',
                                                labelOrient='bottom',
                                                labelPadding=0,
                                                ),
                                        ),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q", "Density:Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                return chart
        if (chart_uni == "Histogram"):
                if (hue_uni == "None"):
                        chart = alt.Chart(df ,title = f'{x_axis_choice_uni}' + " across Years",width=600, height=500).mark_bar().encode(
                                        alt.X( f'{x_axis_choice_uni}'+":Q",
                                                stack='center',
                                                impute=None,
                                                axis=alt.Axis(labels=True,grid=False, ticks=True),
                                                bin= True,
                                        ),
                                        y= alt.Y('count()',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                else :
                        chart = alt.Chart(df ,title = f'{x_axis_choice_uni}' + " across Years" ,width=600, height=500).mark_bar().encode(
                                        alt.X( f'{x_axis_choice_uni}'+":Q",
                                        bin= True,
                                        stack='center',
                                        impute=None,
                                        axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        y= alt.Y('count()',
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        color = alt.Color("Year:N", legend= None),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q"],                                
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive() 
                return chart
        if (chart_uni == "Box"):
                if (hue_uni == "None"):
                        chart = alt.Chart(df,title = f'{x_axis_choice_uni}' + " across Years",width=600, height=500).mark_boxplot().encode(
                                        alt.Y( f'{x_axis_choice_uni}'+":Q",
                                        scale= alt.Scale(zero=False),
                                        axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        x = alt.X("Year:N",
                                                stack='center',
                                                impute=None,
                                                axis=alt.Axis(labels=True, grid=False, ticks=True)
                                                ),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                else :
                        chart = alt.Chart(df, title = f'{x_axis_choice_uni}' + " across Years", width=600, height=500).mark_boxplot().encode(
                                        alt.Y(f'{x_axis_choice_uni}'+":Q",
                                        scale= alt.Scale(zero=False),
                                        axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        x= alt.X('Year:N',
                                                stack='center',
                                                impute=None,
                                                axis=alt.Axis(labels=True, grid=False, ticks=True)
                                                ),
                                        color = alt.Color("Year:N", legend= None),
                                        tooltip = ['Year',f'{x_axis_choice_uni}' + ":Q"],
                                ).configure_axis(
                                        labelFontSize = 10,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                return chart
        if (chart_uni == "Violin"):
                if (hue_uni == 'None'):
                                chart = alt.Chart(df, title = f'{x_axis_choice_uni}' + " Density Plot").transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_=[f'{x_axis_choice_uni}', 'Density'],
                                        groupby=['Year']
                                ).mark_area(orient='horizontal').encode(
                                        y= alt.Y(f'{x_axis_choice_uni}' + ":Q",
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        x=alt.X(
                                                'Density:Q',
                                                stack='center',
                                                impute=None,
                                                title = None,
                                                axis=alt.Axis(labels=False, grid=False, ticks=True),
                                        ),
                                        column=alt.Column(
                                                'Year:N',
                                                header=alt.Header(
                                                titleOrient='bottom',
                                                labelOrient='bottom',
                                                labelPadding=0,
                                                )
                                        ),
                                        tooltip = [f'{x_axis_choice_uni}' + ":Q", 'Density:Q'], 
                                ).properties(
                                        width = 100,
                                        height = 500,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                else :
                        chart = alt.Chart(df, title = f'{x_axis_choice_uni}' + " Density Plot").transform_density(
                                        f'{x_axis_choice_uni}',
                                        as_=[f'{x_axis_choice_uni}', 'Density'],
                                        groupby=['Year']
                                ).mark_area(orient='horizontal').encode(
                                        y= alt.Y(f'{x_axis_choice_uni}' + ":Q",
                                                axis=alt.Axis(labels=True,grid=False, ticks=True)
                                                ),
                                        color= alt.Color('Year:N', legend= None),
                                        x=alt.X(
                                                'Density:Q',
                                                stack='center',
                                                impute=None,
                                                title= None,
                                                axis=alt.Axis(labels=False, grid=False, ticks=True),
                                        ),
                                        column=alt.Column(
                                                'Year:N',
                                                header=alt.Header(
                                                titleOrient='bottom',
                                                labelOrient='bottom',
                                                labelPadding=0,)
                                        ),
                                        tooltip = [f'{x_axis_choice_uni}' + ":Q", 'Density:Q'],
                                ).properties(
                                        width = 100,
                                        height = 500,
                                ).configure_facet(
                                        spacing=0
                                ).configure_view(
                                        stroke=None
                                ).configure_title(
                                        anchor = "middle"
                                ).interactive()
                return chart
        else :
                return 0


def chart_func_bi(df,chart_bi,x_axis_choice_bi,y_axis_choice_bi,hue_bi):
        if (chart_bi == "KDE (Joint Probability)"):
                chart = alt.Chart(df,width=600, height=500).transform_density(
                                f'{x_axis_choice_bi}',
                                as_= [f'{x_axis_choice_bi}', "Density"],
                        ).mark_area(
                                color = 'red', opacity = 0.3
                        ).encode(
                                x= f'{x_axis_choice_bi}'+":Q",
                                y= 'Density:Q',
                                # color = "Year:N" 
                        ).interactive()
                return chart
        if (chart_bi == 'Scatter'):
                chart = alt.Chart(df,width=600, height=500).mark_bar().encode(
                                alt.X( f'{x_axis_choice_bi}'+":Q",
                                # bin=alt.Bin(extent=[0, df[f'{x_axis_choice_uni}'].max()], step=df[f'{x_axis_choice_uni}'].max()/len(df)/2)),
                                ),
                                y='count()',
                                # color = "blue" if hue_bi == "None" else f'{hue_bi}'
                        ).interactive()
                return chart
        if (chart_bi == "Line"):
                chart = alt.Chart(df,width=600, height=500).mark_boxplot().encode(
                                alt.Y( f'{x_axis_choice_bi}'+":Q",
                                # bin=alt.Bin(extent=[0, df[f'{x_axis_choice_uni}'].max()], step=df[f'{x_axis_choice_uni}'].max()/len(df)/2)),
                                ),
                                x='Year:O',
                        ).interactive()
                return chart
        if (chart_bi == "Regression Line"):
                chart = alt.Chart(processed_data).transform_density(
                                f'{x_axis_choice_bi}',
                                as_=[f'{x_axis_choice_bi}', 'density'],
                                groupby=['Year']
                        ).mark_area(orient='horizontal').encode(
                                y=f'{x_axis_choice_bi}'+":Q",
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
        else :
                return 0





side_bar = side_bar(tab_select)
