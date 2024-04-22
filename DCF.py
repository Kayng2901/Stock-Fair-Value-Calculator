import streamlit as st
import requests

def pv(fv, requiredRateOfReturn, years):
    return fv / ((1 + requiredRateOfReturn / 100) ** years)

def fv(pv, growth, years):
    return pv * (1 + growth) ** years

# Initial UI
ticker = st.text_input('Ticker', "AAPL").upper()
buttonClicked = st.button('Set')

# Callbacks
if buttonClicked:
    # Get the data
    link = f"""https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?"""
    modules = f"""modules=assetProfile%2Cprice%2CfinancialData%2CearningsTrend%2CdefaultKeyStatistics"""
    requestString = link + modules

    request = requests.get(requestString, headers={"USER-AGENT": "Mozilla/5.0"})
    
    if request.status_code == 200:
        try:
            data = request.json()["quoteSummary"]["result"][0]
            st.session_state.data = data
        except ValueError:
            st.error("Decoding JSON has failed")
    else:
        st.error(f"Request was unsuccessful. Status code: {request.status_code}")

if 'data' in st.session_state:
    data = st.session_state.data

    # Print company profile
    st.header("Company Profile")
    st.metric("Sector", data["assetProfile"]["sector"])
    st.metric("Industry", data["assetProfile"]["industry"])
    st.metric("Website", data["assetProfile"]["website"])
    st.metric("Market Cap", data["price"]["marketCap"]["fmt"])
    
    with st.expander("About Company"):
        st.write(data["assetProfile"]["longBusinessSummary"])

    # Add space between sections
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    # Get the metrics needed for valuation
    st.header("Valuation")
    currentPrice = data["financialData"]["currentPrice"]["raw"]
    growth = data["earningsTrend"]["trend"][4]["growth"]["raw"] * 100
    peFWD = data["defaultKeyStatistics"]["forwardPE"]["raw"]
    epsFWD = data["defaultKeyStatistics"]["forwardEps"]["raw"]
    requiredRateOfReturn = 10.0
    yearsToProject = 5

    # Print the metrics
    st.metric("currentPrice", currentPrice)
    st.metric("growth", growth)
    st.metric("peFWD", peFWD)
    st.metric("epsFWD", epsFWD)
    st.metric("requiredRateOfReturn", requiredRateOfReturn)
    st.metric("yearsToProject", yearsToProject)

    # Add controls
    growth = st.number_input("Growth", value=growth, step=1.0)
    peFWD = st.number_input("P/E", value=peFWD, step=1.0)
    requiredRateOfReturn = st.number_input("Required Rate Of Return", value=requiredRateOfReturn, step=1.0)

    # Fair value calculation
    futureEPS = fv(epsFWD, growth / 100, yearsToProject)
    futurePrice = futureEPS * peFWD
    stickerPrice = pv(futurePrice, requiredRateOfReturn, yearsToProject)
    upside = (stickerPrice - currentPrice) / stickerPrice * 100

    # Show result
    st.metric("EPS", "{:.2f}".format(futureEPS))
    st.metric("Future Price", "{:.2f}".format(futurePrice))
    st.metric("Sticker Price", "{:.2f}".format(stickerPrice))
    st.metric("Current Price", "{:.2f}".format(currentPrice))
    st.metric("Upside", "{:.2f}".format(upside))
