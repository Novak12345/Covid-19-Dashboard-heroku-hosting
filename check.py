import streamlit as st
st.set_page_config(
        page_title="Covid-19 Dashboard",
        page_icon=":Microbe:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
def homepage():
    import streamlit as st
    from PIL import Image as imging
    def main():
        img = imging.open("x.jpeg")
        st.image(img,width=1000)
        # set_png_as_page_bg('covid2.png')
        st.title("Covid-19 DASHBOARD")
        txt = """
        This web application will serve to analyze, visualize, the spread of Covid-19.
        Coronavirus disease 2019 (COVID-19) is a contagious disease caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2).
        The first known case was identified in Wuhan, China, in December 2019.
        The disease has since spread worldwide, leading to an ongoing pandemic.
        """
        st.write(txt)
        st.markdown('Symptoms')
        st.markdown(("* Respiratory symptoms\n""* Fever\n""* Cough\n""* Shortness of breath\n"))
        st.markdown("Vaccines")
        st.markdown(
            "Track [here](https://www.raps.org/news-and-articles/news-articles/2020/3/covid-19-vaccine-tracker)")
    main()
def dashboard():
    import os
    import streamlit as st
    import numpy as np
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import plotly.io as pio
    from datetime import datetime, timedelta
    from dashes3.utils.fetch_url import fetch_url
    from dashes3.utils.load_data import load_data
    from dashes3.utils.load_css import local_css
    from dashes3.utils.load_time_series import load_time_series
    from x import figcasesprov
    from plotly.offline import plot
    @st.cache
    def plot_snapshot_numbers(df, colors, date, country=None):
        """
        Function plots snapshots for worldwide and countries.
        :param df: DataFrame
        :param colors: list
        :param date: datetime object
        :param country: str
        :return: plotly.figure
        """
        with st.spinner("Rendering chart..."):
            colors = px.colors.qualitative.D3
            if country:
                df = df[df["Country_Region"] == country]
            fig = go.Figure()
            fig.add_trace(go.Bar(y=df[["Confirmed", "Deaths", "Recovered", "Active"]].columns.tolist(),
                                 x=df[["Confirmed", "Deaths", "Recovered", "Active"]].sum().values,
                                 text=df[["Confirmed", "Deaths", "Recovered", "Active"]].sum().values,
                                 orientation='h',
                                 marker=dict(color=[colors[1], colors[3], colors[2], colors[0]]),
                                 ),
                          )
            fig.update_traces(opacity=0.7,
                              textposition=["inside", "outside", "inside", "inside"],
                              texttemplate='%{text:.3s}',
                              hovertemplate='Status: %{y} <br>Count: %{x:,.2f}',
                              marker_line_color='rgb(255, 255, 255)',
                              marker_line_width=2.5
                              )
            fig.update_layout(
                title="Total count",
                width=800,
                legend_title_text="Status",
                xaxis=dict(title="Count"),
                yaxis=dict(showgrid=False, showticklabels=True),
            )

        return fig

    @st.cache
    def plot_top_countries(df, colors, date):
        """
        Function plots top countries by confirmed, deaths, recovered, active cases.
        :param df: DataFrame
        :param colors: list
        :param date: datetime object
        :return: plotly.figure
        """
        with st.spinner("Rendering chart..."):
            temp = df.groupby("Country_Region").agg({"Confirmed": "sum",
                                                     "Deaths": "sum",
                                                     "Recovered": "sum",
                                                     "Active": "sum"})
            colors = px.colors.qualitative.Prism
            fig = make_subplots(2, 2, subplot_titles=["Top 10 Countries by cases",
                                                      "Top 10 Countries by deaths",
                                                      "Top 10 Countries by recoveries",
                                                      "Top 10 Countries by active cases"])
            fig.append_trace(go.Bar(x=temp["Confirmed"].nlargest(n=10),
                                    y=temp["Confirmed"].nlargest(n=10).index,
                                    orientation='h',
                                    marker=dict(color=colors),
                                    hovertemplate='<br>Count: %{x:,.2f}',
                                    ),
                             row=1, col=1)

            fig.append_trace(go.Bar(x=temp["Deaths"].nlargest(n=10),
                                    y=temp["Deaths"].nlargest(n=10).index,
                                    orientation='h',
                                    marker=dict(color=colors),
                                    hovertemplate='<br>Count: %{x:,.2f}',
                                    ),
                             row=2, col=1)

            fig.append_trace(go.Bar(x=temp["Recovered"].nlargest(n=10),
                                    y=temp["Recovered"].nlargest(n=10).index,
                                    orientation='h',
                                    marker=dict(color=colors),
                                    hovertemplate='<br>Count: %{x:,.2f}',
                                    ),
                             row=1, col=2)

            fig.append_trace(go.Bar(x=temp["Active"].nlargest(n=10),
                                    y=temp["Active"].nlargest(n=10).index,
                                    orientation='h',
                                    marker=dict(color=colors),
                                    hovertemplate='<br>Count: %{x:,.2f}'),
                             row=2, col=2)
            fig.update_yaxes(autorange="reversed")
            fig.update_traces(
                opacity=0.7,
                marker_line_color='rgb(255, 255, 255)',
                marker_line_width=2.5
            )
            fig.update_layout(height=800,
                              width=1100,
                              showlegend=False)

        return fig

    @st.cache(allow_output_mutation=True)
    def plot_timeline(df, feature, country=None):
        """
        Function plots  time series charts for worldwide as well as countries
        :param df: DataFrame
        :param feature: str
        :param country: str
        :return: plotly.figure, DataFrame
        """
        color = px.colors.qualitative.Prism
        if country:
            df = df[df["Country/Region"] == country]
        temp = df.groupby(["Date"]).agg({feature: "sum"}).reset_index()
        temp["Delta_{}".format(feature)] = temp[feature].diff()
        temp["Delta_{}".format(feature)].clip(0, inplace=True)

        fig = make_subplots(2, 1, subplot_titles=["Cumulative {}".format(feature),
                                                  "Daily Delta {}".format(feature)])
        fig.add_trace(go.Scatter(
            x=temp["Date"],
            y=temp[feature],
            marker=dict(color=color[2]),
            line=dict(dash="dashdot", width=4),
            hovertemplate='Date: %{x} <br>Count: %{y:,.2f}',
        ),
            row=1, col=1)
        fig.add_trace(go.Bar(
            x=temp["Date"],
            y=temp["Delta_{}".format(feature)],
            marker=dict(color=color[6]),
            opacity=0.7,
            hovertemplate='Date: %{x} <br>Count: %{y:,.2f}'),
            row=2, col=1)
        fig.update_yaxes(showgrid=False, title="Number of cases")
        fig.update_xaxes(showgrid=False)
        fig.update_xaxes(showspikes=True, row=1, col=1)
        fig.update_yaxes(showspikes=True, row=1, col=1)
        fig.update_layout(height=800,
                          showlegend=False)

        return fig, temp

    @st.cache
    def plot_province_drilled(df, country):
        """
        Function computes top provinces by confirmed, deaths, recovered and active cases.
        :param df: DataFrame
        :param country: str
        :return: plotly.figure
        """
        fig = make_subplots(2, 2, subplot_titles=["Top 10 States by cases",
                                                  "Top 10 States by deaths",
                                                  "Top 10 States by recoveries",
                                                  "Top 10 States by active cases"])
        df = df[df["Country_Region"] == country]
        df = df.groupby(["Province_State"]).agg({"Confirmed": "sum",
                                                 "Deaths": "sum",
                                                 "Recovered": "sum",
                                                 "Active": "sum"})
        colors = px.colors.qualitative.Prism
        fig.append_trace(go.Bar(y=df["Confirmed"].nlargest(10).index,
                                x=df["Confirmed"].nlargest(10),
                                orientation='h',
                                marker=dict(color=colors),
                                hovertemplate='<br>Count: %{x:,.2f}',
                                ),
                         row=1, col=1)

        fig.append_trace(go.Bar(y=df["Deaths"].nlargest(10).index,
                                x=df["Deaths"].nlargest(10),
                                orientation='h',
                                marker=dict(color=colors),
                                hovertemplate='<br>Count: %{x:,.2f}',
                                ),
                         row=2, col=1)

        fig.append_trace(go.Bar(y=df["Recovered"].nlargest(10).index,
                                x=df["Recovered"].nlargest(10),
                                orientation='h',
                                marker=dict(color=colors),
                                hovertemplate='<br>Count: %{x:,.2f}',
                                ),
                         row=1, col=2)

        fig.append_trace(go.Bar(y=df["Active"].nlargest(10).index,
                                x=df["Active"].nlargest(10),
                                orientation='h',
                                marker=dict(color=colors),
                                hovertemplate='<br>Count: %{x:,.2f}',
                                ),
                         row=2, col=2)
        fig.update_yaxes(ticks="inside", autorange="reversed")
        fig.update_xaxes(showgrid=False)
        fig.update_traces(opacity=0.7,
                          marker_line_color='rgb(255, 255, 255)',
                          marker_line_width=2.5
                          )
        fig.update_layout(height=800, width=1200,
                          showlegend=False)

        return fig

    def load_day_change(time_series_dict, keys, granularity, country=None):
        """
        Function computes the delta change in confirmed, deaths, recovered and active cases over a single day
        :param time_series_dict: dict
        :param keys: list
        :param granularity: str
        :param country: str
        :return: plotly.figure
        """
        response_dict = {}
        PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
        local_css("style.css")
        curr = 0
        prev = 0
        for key in keys:
            if granularity == "Country":
                _, temp = plot_timeline(time_series_dict[key], key, country=country)
            else:
                _, temp = plot_timeline(time_series_dict[key], key)
            prev = temp.iloc[-2, -2]
            curr = temp.iloc[-1, -2]
            if (curr - prev) >= 0:
                arrow = "&uarr;"
            else:
                arrow = "&darr;"
            response_dict[key] = [arrow, abs(curr - prev)]

        val = response_dict["Confirmed"][1] - response_dict["Deaths"][1] - response_dict["Recovered"][1]
        if val >= 0:
            response_dict["Active"] = ["&uarr;", abs(val)]
        else:
            response_dict["Active"] = ["&darr;", abs(val)]

        st.write("\n")
        st.write("\n")
        t = (
            f"<div><span class='highlight blue'>Active:  <span class='bold'>{response_dict['Active'][0]} {response_dict['Active'][1]}</span> </span>"
            f"<span class='highlight orange'>Confirmed:  <span class='bold'>{response_dict['Confirmed'][0]} {response_dict['Confirmed'][1]}</span> </span>"
            f"<span class='highlight red'>Deaths:  <span class='bold'>{response_dict['Deaths'][0]} {response_dict['Deaths'][1]}</span> </span> "
            f"<span class='highlight green'>Recovered:  <span class='bold'>{response_dict['Deaths'][0]} {response_dict['Recovered'][1]}</span> </span></div>")

        st.markdown(t, unsafe_allow_html=True)

    @st.cache(suppress_st_warning=True)
    def plot_province(df, country):
        """
        Function plots the map of a country with the state/county level information as a hover.
        :param df: DataFrame
        :param country: str
        :return: plotly.figure
        """
        fig = None
        df = df[df["Country_Region"] == country]
        if df["Province_State"].isnull().all():
            st.info("Sorry we do not have province/state level information for {}".format(country))
        else:
            df.rename(columns={"Lat": "lat",
                               "Long_": "lon",
                               "Admin2": "City"}, inplace=True)
            df.loc[:, 'Scaled Confirmed'] = df.loc[:, 'Confirmed'].apply(lambda s: np.log(s))
            df.loc[:, 'Scaled Confirmed'] = df.loc[:, 'Scaled Confirmed'].apply(
                lambda s: 0 if s == -np.inf else s)
            df["Province_State"].fillna("Not Available", inplace=True)
            temp = df[["lat", "lon"]]
            temp.dropna(inplace=True)
            token = st.secrets[".mapbox_token"]
            fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=3, height=600, width=800,
                                    size="Scaled Confirmed",
                                    color="Incident_Rate",
                                    color_continuous_scale=px.colors.sequential.Hot,
                                    hover_name="Combined_Key", hover_data=["Confirmed",
                                                                           "Deaths", "Recovered"])
            fig.update_traces(opacity=0.7)
            fig.update_layout(mapbox_style="light", height=1000, width=1000, mapbox_accesstoken=token)
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        return fig

    def main():
        backgroundset('about.png')
        figcases = figcasesprov()
        st.write(figcases)
        pio.templates.default = "plotly_dark"
        date = datetime.today()
        df = None
        while True:
            try:
                df = load_data(fetch_url(date))
            except Exception as e:
                date = date - timedelta(days=1)
                continue
            break
        st.info("Data updated as on {}".format(date.date().strftime("%d %B, %Y")))
        time_series_dict = load_time_series()
        granularity = st.sidebar.selectbox("Granularity", ["Worldwide", "Country"])
        if granularity == "Country":
            country = st.sidebar.selectbox("Country", df["Country_Region"].unique())
            st.title(country)
            graph_type = st.selectbox("Choose visualization", ["Total Count",
                                                               "Timeline",
                                                               "Province/State"])
            if graph_type == "Total Count":
                st.subheader("One day change")
                load_day_change(time_series_dict, time_series_dict.keys(), granularity, country=country)
                fig = plot_snapshot_numbers(df, px.colors.qualitative.D3, date.date(), country)
                st.plotly_chart(fig)
            elif graph_type == "Timeline":
                feature = st.selectbox("Select one", ["Confirmed", "Deaths", "Recovered"])
                fig, _ = plot_timeline(time_series_dict[feature], feature, country=country)
                st.plotly_chart(fig)
            elif graph_type == "Province/State":
                fig = plot_province(df, country)
                if fig is not None:
                    fig_drilled = None
                    flag = st.checkbox("Summary (click and scroll)")
                    st.subheader("Hover Map")
                    st.plotly_chart(fig)
                    if flag:
                        if country == "US":
                            fig_drilled = plot_province_drilled(load_data(fetch_url(date, country="US")), country)
                        else:
                            fig_drilled = plot_province_drilled(df, country)
                    if fig_drilled is not None:
                        st.subheader("Summary")
                        st.plotly_chart(fig_drilled)
        else:
            st.title("Worldwide")
            st.write("\n")
            # st.info("Data updated as on {}".format(date.date().strftime("%d %B, %Y")))
            graph_type = st.sidebar.selectbox("Choose visualization", ["Total Count",
                                                                       "Top affected/recovered",
                                                                       "Timeline"])
            if graph_type == "Total Count":
                st.subheader("One day change")
                load_day_change(time_series_dict, time_series_dict.keys(), granularity)
                fig = plot_snapshot_numbers(df, px.colors.qualitative.D3, date.date())
                st.plotly_chart(fig)
            elif graph_type == "Top affected/recovered":
                fig = plot_top_countries(df, px.colors.qualitative.D3, date.date())
                st.plotly_chart(fig)
            elif graph_type == "Timeline":
                feature = st.selectbox("Select one", ["Confirmed", "Deaths", "Recovered"])
                fig, _ = plot_timeline(time_series_dict[feature], feature)
                st.plotly_chart(fig)
    main()
def datapage():
    import streamlit as st
    from datetime import datetime, timedelta
    from dashes3.utils.load_data import load_data
    from dashes3.utils.fetch_url import fetch_url
    from PIL import Image
    from x import figcasesprov

    def main():
        figcases = figcasesprov()
        st.write(figcases)
        backgroundset("covid.png")
        st.title("Data")
        date = datetime.today()
        df = None
        load_state = st.text('Loading data......')
        while True:
            try:
                df = load_data(fetch_url(date))
            except Exception as e:
                date = date - timedelta(days=1)
                continue
            break
        load_state.text("Loading data......done!")

        if st.checkbox("Show raw data"):
            st.subheader('Raw data')
            st.write(df)
        st.subheader("The numbers so far")
        st.markdown("* There are **{}** countries that have been affected by the COVID-19 virus.".format(
            len(df["Country_Region"].unique())))
        st.markdown("* The virus has affected **{:.2f}M** people and caused the death of **{:.2f}K**.".format(
            df["Confirmed"].sum() / 1000000,
            df["Deaths"].sum() / 1000))
        h_confirmed = df.groupby("Country_Region").agg({"Confirmed": "sum"}).nlargest(1, "Confirmed")
        st.markdown("* **{}** has the largest number of confirmed cases with **{:.2f}M** confirmed cases.".format(
            h_confirmed.index.values[0],
            h_confirmed["Confirmed"].values[0] / 1000000))
        h_deaths = df.groupby("Country_Region").agg({"Deaths": "sum"}).nlargest(1, "Deaths")
        st.markdown(
            "* **{}** has the largest number of deaths with **{:.2f}K** deaths.".format(h_deaths.index.values[0],
                                                                                        h_deaths["Deaths"].values[
                                                                                            0] / 1000))
        h_recovered = df.groupby("Country_Region").agg({"Recovered": "sum"}).nlargest(1, "Recovered")
        st.markdown("* **{}** has the largest number of recoveries with **{:.2f}M** recovered.".format(
            h_recovered.index.values[0],
            h_recovered["Recovered"].values[0] / 1000000))
    main()
def aboutpage():
    import streamlit as st
    def main():
        backgroundset('x.png')
        st.title("About")
        st.balloons()
        st.info(
            """
            This app is maintained by Arohan. You can learn more about me at
            https://sites.google.com/view/arohan/.
            """
        )
    main()
def backgroundset(file):
    import base64
    import streamlit as st
    import streamlit.components.v1 as components
    @st.cache(allow_output_mutation=True)
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def set_png_as_page_bg(png_file):
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = '''
        <style>
        .stApp {
         background-image: url("data:image/png;base64,%s");
         background-size: cover;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)
        return
    set_png_as_page_bg(file)
def main():
    backgroundset('ribbons.png')
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
        unsafe_allow_html=True,
    )
    query_params = st.experimental_get_query_params()
    tabs = [
        "Home",
        "Data",
        "Dashboard",
        "About"
    ]
    if "tab" in query_params:
        active_tab = query_params["tab"][0]
    else:
        active_tab = "Home"

    if active_tab not in tabs:
        st.experimental_set_query_params(tab="Home")
        active_tab = "Home"

    li_items = "".join(
        f"""
        <li class="nav-item">
            <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
        </li>
        """
        for t in tabs
    )
    tabs_html = f"""
        <ul class="nav nav-tabs">
        {li_items}
        </ul>
    """

    st.markdown(tabs_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if active_tab == "Home":
        homepage()
    elif active_tab == "About":
       aboutpage()
    elif active_tab == "Data":
        datapage()
    elif active_tab == "Dashboard":
        dashboard()
    else:
        st.error("Something has gone terribly wrong.")

if __name__ == '__main__':
    main()
