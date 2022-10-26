import streamlit as st
import seaborn as sns
import scipy.stats as stats
import pandas as pd
import altair as alt
from altair import datum
import numpy as np
import streamlit.components.v1 as components
from PIL import Image


def main():
        st.set_page_config(
                page_title="EDA on Threatened Species",
                page_icon="✅",
                layout="wide",
                initial_sidebar_state="auto"
        )
    
        
        st.title('EDA on Threatened Species.')
        st.sidebar.title('Interactive Visualizer')
        st.sidebar.markdown("Select drop downs for customization.")
    
if __name__ == '__main__':
    main()
        

@st.cache(persist= True)
def load():
    raw_data = pd.read_csv("UN_unprocessed_data_Threatened Species.csv",
                            index_col=None, header=0, encoding='latin-1')
    return raw_data
raw_data = load()


@st.cache(persist= True)
def clean():
    clean_data = pd.read_csv("New_Threatened.csv",
                            index_col=None, header=0, encoding='UTF-8')
    clean_data = clean_data.dropna()
    return clean_data
En_data = clean()

Enc_data = En_data.copy()    
    
@st.cache(persist= True)
def long_clean(long_data):
    long_data = Enc_data.melt(
        id_vars=['Code','Country','Sub Region','Continent','Year'],
        value_vars=['Invertebrates','Vertebrates','Plants', 'Total'],
        var_name='Type', value_name='Value')
    return long_data
long_data = long_clean(Enc_data)

def num_lab(df):
    num_lab = df.select_dtypes(include='float64').columns
    return num_lab

num_label = num_lab(En_data)

def continent(df):
    continent = df["Continent"].unique()
    return continent

continent_label = continent(En_data)

def sub_region(continent_scatter):
        sub_region = En_data.where(En_data["Continent"].isin(continent_scatter)).dropna()
        sub_region0 = sub_region['Sub Region'].unique()
        return sub_region0

cm = sns.light_palette("lightblue", as_cmap= True)

longc_data = long_data.copy()

def long_transform(df,trans):
        if (trans == 'Log-Normal'):
                np.seterr(divide = 'ignore')
                df.iloc[:,6:]= df.iloc[:,6:].astype(float)  
                df.replace(0,0.9,inplace=True)
                df.iloc[:,6:]= df.iloc[:, 6:].apply(np.log)
                df.replace(np.log(0.9),0.0,inplace=True)
                df.round(1)
        else :
                numeric_cols = df.drop(['Code','Year'],axis =1).select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].apply(stats.zscore)
                df.round(1)
        return df

Enc_data = En_data.copy()

def transform(df,trans):
        if (trans == 'Log-Normal'):
                np.seterr(divide = 'ignore')
                df.iloc[:,5:]= df.iloc[:,5:].astype(float)  
                df.replace(0,0.9,inplace=True)
                df.iloc[:,5:]= df.iloc[:,5:].apply(np.log)
                df.replace(np.log(0.9),0.0,inplace=True)
                df.round(1)
        else :
                numeric_cols = df.drop(['Code','Year'],axis =1).select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].apply(stats.zscore)
                df.round(1)
        return df

        

def side_bar():
        st.subheader("Goals of the Analysis:")
        '''
        1. To understand the trend of threatened species across globe over time 
        2. To explore different regions of the world and get insights, like most affected countries and see if any pattern emerging
        3. To explore correlation between these species and see if data is sufficient for causation     

        Technologies Used -
        1. Altair for plotting
        2. Pandas for dataframe handling
        3. Scipy for statistical transformations
        4. Streamlit for application buiding 
        5. Heroku and Github for deployment 
        '''
        st.subheader("Raw Dataset")
        
        col1_raw , col2_raw = st.columns([5,3])
        
        with col1_raw :
                st.dataframe(raw_data,height = 500)
        with col2_raw :
                '''
                The dataset is organised and maintained by the [United Nations](https://data.un.org/), 
                available for public research. The data is in long format and series column in the data constitute of all our numerical attributes 
                The dataset contains attributes like `country, country code, year, and in series column as
                Number of endangered vertebrates, Number of endangered invertebrates, Number of endangered plants, total endangered species`,
                etc. Hence, a long to wide transformation of data is necessary for further analysis. 
                '''
                image = Image.open('img_1.jpg')
                st.image(image, caption='We Need Help!!', use_column_width = True)

        st.subheader("Processed Dataset")
        col1_trans , col2_trans = st.columns([6,2])

        with col1_trans :
                st.dataframe(En_data)
        with col2_trans :
                '''
                We have transformed our data into wider format. Also, more conditional variables were added which are factual information like continent 
                and sub regions of countries using their country code. This will help us to analyse by adding more dimension to our visualizations.
                The dataset is very clean and contains only two missing data points. The missingness is **completely random** 
                and no relation could be determined. Hence, in such cases our first step is to understand the distribution by 
                summarizing the central tendency of our data, the dispersion, and the shape of the attribute distribution.
                '''

        st.subheader("Summary Statistics")
        
        col1_summary , col2_summary = st.columns([4,4])
        
        with col1_summary :
                st.dataframe(En_data.drop(["Year", "Code"], axis= 1).describe(),width=600)
        with col2_summary :
                '''
                The attribute in the dataset has high value of standard deviation, with small mean and median. This indicates high positive skewness in our variables. 
                Such high differences between mean and standard deviation only happens in a data if there is: 
                * Presence of Outliers in the data set
                * Or distribution is a log distribution with high concentration of data points below mean and few high value data points influencing mean.

                To visualize our findings, we will use distribution plots like histogram and box plot to see if it's a log distribution or do we require outlier treatment.
                '''

        st.subheader("Histograms")
        
        chart_hist_find = alt.Chart(long_data).mark_bar().encode(
                                        x = alt.X("Value:Q", type='quantitative', 
                                                axis=alt.Axis(title=''), 
                                                scale=alt.Scale(zero=False),
                                                bin=alt.Bin(extent=[0, 1000], step=50)),
                                        y = alt.Y('count():Q', 
                                                axis=alt.Axis(title='')),
                                        color = alt.Color('Type:N',legend= None),
                                        tooltip = ["Value:Q", 'count():Q'],
                                        column=alt.Column('Type:N', sort=['Invertebrates','Vertebrates','Plants', 'Total'])
                                        ).properties(
                                        width=200,
                                        height=200
                                        ).interactive(                                                
                                )
        
        st.write(chart_hist_find)
        '''
        As we speculated, the histogram of our variables is highly concentrated on lower end of the values. This shows that the distribution of the 
        variable is non-linear, and for any further analysis or visualization, transformation of data is must. The graph is highly positive skewed which indicates 
        log normal distribution. To make the distribution linear we will apply multiple transformation and choose which transformation best suits are data.        
        
        Select transformation type from the select box in the sidebar panel. A density plot is used to visualise the effects of transformation, and to see if transformed 
        values are following a normal distribution. A Z-Score transformation is simply subtracting mean value from individual values and dividing the result by standard deviation
        It is a simple yet powerful transformation. A log normal transformation is taking natural log of values, One thing to keep in mind is log normal transformation are always
        performed on positive integers, thus in our case all zero values had to substituted by 1 to perform log transformation.
        '''

        trans = st.sidebar.selectbox("Transformation Type",["Z-Score","Log-Normal"],index = 1)
        Entrans_data = transform(Enc_data,trans)
        longtrans_data = long_transform(longc_data,trans)               

        chart_trans_find = alt.Chart(longtrans_data).transform_density(
                                        "Value",
                                        as_= ["Value", "Density"],
                                        groupby=['Type']
                                        ).mark_area(
                                                opacity = 0.3
                                        ).encode(
                                                x = alt.X("Value", type='quantitative', 
                                                axis=alt.Axis(title='', grid = False), 
                                                # scale=alt.Scale(zero=False),
                                                # bin=alt.Bin(extent=[0, 10], step=10)
                                                ),
                                                y = alt.Y('Density:Q', 
                                                axis=alt.Axis(title='', grid = False)),
                                                color = alt.Color('Type:N',legend= None),
                                                tooltip = ["Value:Q", 'Density:Q'],
                                                column=alt.Column('Type:N', sort=['Invertebrates','Vertebrates','Plants', 'Total'])
                                        ).properties(
                                        width=200,
                                        height=200
                                        ).interactive(                                                
                                )

        st.write(chart_trans_find)
        st.markdown('The log transformation showed similarities to normal distribution; however attributes are\
                 not perfectly normal distributed and contains positive kurtosis.')
        
        st.subheader("BoxPlot")
        '''
        Now that we have a good idea about the distribution, let's check if we still have outliers after transformation. To detect outliers and have a good understanding 
        of quantiles of the distribution a box plot is used. Notice that even after transformation we are able to see some outliers in the dataset. This highly suggest either 
        error is present in data values or few points in the data are having tremendous effects on the distribution properties. 
        '''
        chart_box_find = alt.Chart(longtrans_data, width=200, height=200).mark_boxplot().encode(
                                        alt.Y("Value:Q",title = ' ',
                                        # scale= alt.Scale(),
                                        axis=alt.Axis(labels=True,grid=False, ticks=True)
                                        ),
                                        x= alt.X('Year:N',
                                                stack='center',
                                                impute=None,title = ' ',
                                                axis=alt.Axis(labels=True, grid=False, ticks=True)
                                                ),
                                        color = alt.Color('Type:N', legend= None),
                                        column=alt.Column('Type:N', sort=['Invertebrates','Vertebrates','Plants', 'Total']),
                                        tooltip = ['Year',"Value:Q","Type:N"],
                                ).interactive()

        st.write(chart_box_find)
        st.subheader("Multivariate Analysis")
        '''
        From box plot, it was evident that we have lot of outliers in our data. 
        As it seems these outliers are important for the data and hence, we would not be eliminating them as they might be the
        countries we are looking for. So, let's jump into multivariate analysis, and the best way to start is by calculating correlation matrix. A correlation matrix
        is a symmetric table across the diagonal. The values in the table are correlation values between two variables. It ranges from -1 to 1. 
        '''


        col1_corr , col2_corr = st.columns([4,4])
        
        with col1_corr :
                st.dataframe(En_data.drop(["Code","Year"], axis= 1).corr().style.background_gradient(cmap= cm),width=600)
        with col2_corr :
                '''
                The attributes in the dataset have strong positive correlation values among vertebrates with plants and invertebrates. As the entire correlation matrix
                is positive thus this means with rise in value of one attribute we will also see increase in the others. However, it does not says that there is a causation of increase
                among these species.
                '''
        
        st.markdown("Let's try to visualize the trend of number of threatened species over the years. A line chart would be perfect for the task.")

        colors = ['#7fc97f','#beaed4','#fdc086','#0099ff']

        chart_line_find= alt.Chart(En_data, width = 500, height = 400 ).mark_line().encode(
                                x=alt.X("Year",axis=alt.Axis(title='',grid = False, )),
                                y=alt.Y(
                                        alt.repeat("layer"), aggregate="sum", #title="Mean of US and Worldwide Gross"
                                        axis=alt.Axis(title='', grid = False)
                                ),
                                color=alt.datum(alt.repeat("layer")),
                                ).repeat(
                                layer=["Invertebrates", "Vertebrates", "Plants","Total"],
                                ).configure_range(
                                category=alt.RangeScheme(colors)
                                )
        line_col1 , line_col2 = st.columns([5,3])

        with line_col1 :
                st.write(chart_line_find)
        with line_col2 :
                '''
                We can clearly see a constant increase in all species type over the year. Another thing to note is sharp increase in slopes around and after 2018.
                However, even in pandemic times when carbon footprint and human intervention were at local minimum, we still see a sharp increase in numbers around that time. 
                '''
                
        
        st.subheader("Scatter Plot")
        interval_sf = alt.selection_interval()
        Entrans_data_scatter = Entrans_data.where(Entrans_data['Year'].isin([2021,2004])).dropna()
        chart_scatter_find = alt.Chart(Entrans_data_scatter,width=400, height=250).mark_point().encode(
                        alt.X(alt.repeat("column"), type='quantitative',axis=alt.Axis(labels=True, grid=False, ticks=True)),
                        alt.Y(alt.repeat("row"), type='quantitative',axis=alt.Axis(labels=True, grid=False, ticks=True)),
                        color = 'Continent:N'
        ).repeat(
                row=['Invertebrates','Vertebrates'],
                column=['Total' , 'Plants']
        ).add_selection(
                interval_sf
        ).interactive(

        )
        st.write(chart_scatter_find)
        '''
        The scatter plot of transformed values coloured by continent does seem to show some trends, however it's so cluttered and unfiltered that deriving a meaningful insight
        is next to impossible. So, to add more dimensions to our graph we add size and shape along with colour based on attribute values. This adds more functionality to our chart.
        The default values in the select box represents one of the insights uncovered during exploration, feel free to play with the filters and give yourself a try.     
        '''

        x_scatter1 = st.sidebar.selectbox("X Axis - Chart 1", num_label,index= 0)
        x_scatter2 = st.sidebar.selectbox("X Axis - Chart 2", num_label,index= 2)
        y_scatter = st.sidebar.selectbox("Y Axis", num_label, index= 1)
        continent_scatter = st.sidebar.multiselect("Select Continents",continent_label,default = "Asia")
        sub_region_label = sub_region(continent_scatter)
        sub_scatter = st.sidebar.multiselect("Select Sub Regions",sub_region_label,default = ["South-eastern Asia", "Central Asia"])
        year_scatter = st.sidebar.multiselect("Select Years", [2004,2010,2015,2018,2019,2020,2021], default = [2021,2004])

        df_scatter = Entrans_data[Entrans_data['Sub Region'].isin(sub_scatter) & Entrans_data['Year'].isin(year_scatter)]


        # selection = alt.selection_interval(bind='scales')
        brush = alt.selection_interval(encodings=['x'])
        chart_scatter = alt.Chart(df_scatter).mark_point().encode(
                y = alt.Y(f'{y_scatter}' + ":Q", axis=alt.Axis(labels=True, grid=False, ticks=True)),
                # x= alt.X(f'{x_scatter1}' + ":Q"),
                # color = 'Sub Region:N',
                color = alt.condition(brush,"Sub Region:N", alt.ColorValue('gray'),legend= None),
                size = alt.Size("Year:O",legend = None),
                shape = "Continent:N",
                tooltip = ['Country','Sub Region', 'Year'],
        ).add_selection(
                brush
        ).properties(
                width = 450,
                height = 450
        ).interactive()

        chart_scatter.encode(x= alt.X(f'{x_scatter1}' + ":Q",\
                axis=alt.Axis(labels=True, grid=False, ticks=True))) \
                | chart_scatter.encode(x= alt.X(f'{x_scatter2}' + ":Q",\
                axis=alt.Axis(labels=True, grid=False, ticks=True)))  
        
        '''
        From the scatter plot, we can say that there are regions around the world who are experiencing sudden increase in number of threatened species.
        This indicates that there are more factors involved to increase in number and hence more data point is required to have a strong causation.

        '''

        st.markdown("Let's try to visualize highly affected countries and see how much they account for with respect to rest of the world.")

        col1 , col2 = st.columns([1,5])
        
        with col1 :
                select_axis_hist = st.selectbox("Species Type",num_label,index = 0)
        with col2 :
                slider_hist = st.slider("Top N Countries", min_value = 1, max_value = 250, step = 1, value = 10)
        
        t50_df0 = En_data.where(En_data['Year'] == 2021).dropna()
        t50 = t50_df0[f'{select_axis_hist}'].nlargest(slider_hist)
        t50_df = t50_df0[t50_df0[f'{select_axis_hist}'].isin(t50)]
        t50_df['Percent Of Total'] =  round(t50_df[f'{select_axis_hist}']/sum(t50_df0[f'{select_axis_hist}']),2)
        # x = (((sum(t50_df0[f'{select_axis_hist}'])-sum(t50_df[f'{select_axis_hist}']))/t50_df.shape[1]))/sum(t50_df0[f'{select_axis_hist}'])
        # t50_df['Rest Of World'] = x
        


        url = 'https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/world-110m.json'
        
        source = alt.topo_feature(url, "countries")

        background = alt.Chart(source).mark_geoshape(fill="white")

        foreground = (
                alt.Chart(source)
                .mark_geoshape(stroke="black", strokeWidth=0.15)
                .encode(
                        color=alt.condition(
                                'datum.Country !== null',
                                "Country:O",  
                                alt.value('lightgray'),
                                legend = None
                        ),
                        
                        # size = "Total:O",
                        tooltip = ["Country:N"],
                ).transform_lookup(
                        lookup="id",
                        from_=alt.LookupData(t50_df, "Code", ["Country",'Sub Region',"Total"])
                )
                )

        final_map = (
                (background + foreground)
                .configure_view(strokeWidth=0)
                .properties(width=800, height=400)
                .project("naturalEarth1")
        ).interactive()

        # st.write(final_map)

        bar_max = alt.Chart(t50_df).mark_bar().encode(
                y= alt.Y("Percent Of Total",axis=alt.Axis(labels=True, format='%', grid=False, ticks=True)),
                # tooltip = ['Percent Of Total'],
                color = alt.Color("Country:O", legend = None),
                # x= 
        ).properties(
                width = 150,
                height = 400
        ).interactive()

        
        with col1 :
                st.write(bar_max)

        with col2 :
                st.write(final_map)
        
        '''
        We can conclude that -
        1. There is an increasing trend in number of threatened species across globe over time, with big spikes around 2018 and 2021
        2. Top 10 countries with highest number of threatened species constitute of 25-35 percent of the total number
        3. Around 20 % of the countries are responsible for about 80 % of the total number of threatened species in the world, The dataset is following the Pareto principal
        4. If we look at sub regions of highly affected countries among different species, we will see clusters emerging with respect to their location. This suggest more factors are affecting in increase in numbers, thus more data is required for further analysis. 
        5. We can say that we do not have enough data points to prove a causation, the data is correlated but with the advent of a new attributes we might see a change in correlation and witness a Simpson's paradox. 
          
        The top 10 affected countries - Invertebrates 

        * United States of America, Australia, Indonesia, Philippines, Seychelles, Malaysia, Greece, Spain, Madagascar, Portugal

        The top 10 affected countries - Vertebrates
         
        * Indonesia, Mexico, Colombia, India, Madagascar, China, Brazil, United States of America, Ecuador, Australia

        The top 10 affected countries - Plants

        * Madagascar, Ecuador, Malaysia, Mexico, Brazil, United Rep. of Tanzania, Indonesia, Australia, United States of America, Colombia

        Countries present in at leat two of the above groups

        * USA, Australia, Indonesia, Malaysia, Madagascar, Mexico, Colombia, Brazil, Ecuador 

        Sub Region clusters - 
        1. Northern America (USA, Mexico)
        2. South America (Colombia, Ecuador) 
        3. South-eastern Asia (Indonesia, Philippines, Malaysia)
        4. Eastern Africa (Madagascar, United Rep. of Tanzania) and 
        5. Southern Europe (Greece, Spain, Portugal)

        '''

        icon =  '''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"> <i class="fa-solid fa-dragon"></i>'''

        embeded_components = {"linkedin": '''<script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script> 
                <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="medium" data-theme="light" data-type="VERTICAL" data-vanity="adiark" data-version="v1">
                        '''}

        st.sidebar.markdown(' Wish to connect?')
        st.sidebar.write('📧: jainadi5@msu.edu')

        with st.sidebar :
                components.html(embeded_components['linkedin'], height = 300)
        
side_bar = side_bar()
