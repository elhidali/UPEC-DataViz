##

#streamlit==1.28.2
#pandas==2.1.3
#numpy==1.26.2
#matplotlib==3.8.2
#seaborn==0.13.0
#plotly==5.18.0
#bokeh==2.4.3
#Pillow==10.1.0
#ipython==8.18.1
#scipy==1.11.4
#statsmodels==0.14.0

##
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt  # Add this import

##
st.set_page_config(page_title="Superstore!!!",
                   page_icon=":bar_chart:",
                   layout="wide")
st.title(" :bar_chart: SuperStore Dashboard")

##
fl = "Data/Sample - Superstore.xls"

##
df = pd.read_excel(fl)
df.set_index("Row ID", inplace=True)
st.write(df.head())

##
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()
##
col1, col2 = st.columns(2)

with col1:
    date1 = st.date_input("start date", startDate)
    date1 = pd.to_datetime(date1)

with col2:
    date2 = st.date_input("end date", endDate)
    date2 = pd.to_datetime(date2)

##
df = df[(df["Order Date"] >= date1) &
        (df["Order Date"] <= date2)].copy()

##
st.sidebar.header("Choisissez votre filtre: ")
# Create filter for Region
region = st.sidebar.multiselect("Choisissez votre région", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create filter for State
state = st.sidebar.multiselect("Choisissez l'État", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create filter for City
city = st.sidebar.multiselect("Choisissez la ville", df3["City"].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(city)]

##
col1, col2 = st.columns(2)

category_df = df4.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Ventes par catégorie")
    fig = px.bar(category_df, x="Category", y="Sales",
                 text=[f'${x:,.0f}' for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Ventes par région")
    fig = px.pie(df4, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=df4["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
##
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Vue par catégorie"):
        # st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Cliquez ici pour télécharger les données au format CSV')

with cl2:
    with st.expander("Vue par région"):
        region = df4.groupby(by="Region", as_index=False)["Sales"].sum()
        # st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les données", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Cliquez ici pour télécharger les données au format CSV')

##
df4["month_year"] = df4["Order Date"].dt.to_period("M")
df4["month_year"] = df4["month_year"].dt.strftime("%Y : %b")
month_year = df4.groupby(by="month_year", as_index=False)["Sales"].sum()

st.subheader('Analyse de séries temporelles')

fig2 = px.line(month_year, x="month_year", y="Sales",
               labels={"Sales": "Amount"}, height=500, width=1000,
               template="gridon")
st.plotly_chart(fig2, use_container_width=True)
##
with st.expander("Vue sur la série temporelle:"):
    st.write(month_year.T)
    csv = month_year.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger les données", data=csv,
                       file_name="month_year.csv", mime="text/csv",
                       help='Cliquez ici pour télécharger les données au format CSV')

##
st.subheader("Vue hiérarchique des ventes à l'aide de la carte arborescente (Tree Map)")

fig3 = px.treemap(df4, path=["Region", "Category", "Sub-Category"],
                  values="Sales",
                  hover_data=["Region", "Category", "Sales"],
                  color="Sub-Category")

fig3.update_layout(width=650, height=500)
st.plotly_chart(fig3, use_container_width=True)

##
cl1, cl2 = st.columns(2)

with cl1:
    st.subheader("Ventes par segment")
    fig = px.pie(df4, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=df4["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with cl2:
    st.subheader("Ventes par catégorie")
    fig = px.pie(df4, values="Sales", names="Category", template="plotly_dark")
    fig.update_traces(text=df4["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

##
import plotly.figure_factory as ff

st.subheader(":point_right: Résumé des ventes par sous-catégorie mois par mois")
with st.expander("Tableau Récapitulatif"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    # st.write(df_sample)
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Tableau mensuel des sous-catégories")
    df4["month"] = df4["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=df4, values="Sales", index=["Sub-Category"], columns="month")
    # st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

##
# Create a scatter plot
data1 = px.scatter(df4, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relation entre les ventes et les profits à l'aide d'un graphique de dispersion.",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("Visualiser le dataframe"):
    # st.write(df4.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))
    st.write(df4.iloc[:500, 1:20:2])

# Download orginal DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Télécharger les données', data=csv, file_name="Data.csv", mime="text/csv",
                   help="Cliquez ici pour télécharger les données au format CSV")
