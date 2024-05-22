import streamlit as st
import requests

def pv(fv, requiredRateOfReturn, years):
    return fv / ((1 + requiredRateOfReturn / 100) ** years)

def fv(pv, growth, years):
    return pv * (1 + growth) ** years

def format_market_cap(market_cap_str):
    market_cap = float(market_cap_str)
    if market_cap >= 1e9:
        return f"{market_cap / 1e9:.2f} Billion"
    elif market_cap >= 1e6:
        return f"{market_cap / 1e6:.2f} Million"
    else:
        return f"{market_cap:.2f}"

# Title of the app
st.title("Stock Valuation App")

# Initial UI for user input
ticker = st.text_input('Enter Ticker Symbol', 'AAPL').upper()
buttonClicked = st.button('Get Data')

# API Key for Alpha Vantage. Mine is such, you can register yours for free at Alpha Vantage.
api_key = 'O8Y3055L5UZRA0XE'

# Callbacks to fetch data when the button is clicked
if buttonClicked:
    # Construct the request URL
    base_url = f"https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": api_key
    }

    # Send the request to Alpha Vantage API
    response = requests.get(base_url, params=params)
    
    # Process the response
    if response.status_code == 200:
        try:
            data = response.json()
            if "Symbol" in data:  # Checking if the response contains the expected data
                st.session_state.data = data
            else:
                st.error("Invalid ticker symbol or data not available.")
        except ValueError:
            st.error("Failed to decode JSON response.")
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")

# Display the data if available
if 'data' in st.session_state:
    data = st.session_state.data

    # Company Profile
    st.header("Company Profile")
    st.write(f"**Sector:** {data['Sector']}")
    st.write(f"**Industry:** {data['Industry']}")
    market_cap_formatted = format_market_cap(data['MarketCapitalization'])
    st.write(f"**Market Cap:** {market_cap_formatted}")
    st.write(f"**Description:** {data['Description']}")

    # Valuation Section
    st.header("Valuation")
    currentPrice = float(data["50DayMovingAverage"])
    growth = float(data["EPS"] if data["EPS"] else 0)  # Assuming EPS growth as a proxy for actual growth rate
    peFWD = float(data["ForwardPE"])
    epsFWD = float(data["EPS"])
    requiredRateOfReturn = 10.0
    yearsToProject = 5

    # Displaying default metrics
    st.metric("Current Price", currentPrice)
    st.metric("Growth (%)", growth)
    st.metric("Forward P/E", peFWD)
    st.metric("Forward EPS", epsFWD)
    st.metric("Required Rate of Return (%)", requiredRateOfReturn)
    st.metric("Years to Project", yearsToProject)

    # User inputs for valuation
    growth = st.number_input("Growth (%)", value=growth, step=1.0)
    peFWD = st.number_input("Forward P/E", value=peFWD, step=1.0)
    requiredRateOfReturn = st.number_input("Required Rate of Return (%)", value=requiredRateOfReturn, step=1.0)

    # Valuation calculations
    futureEPS = fv(epsFWD, growth / 100, yearsToProject)
    futurePrice = futureEPS * peFWD
    stickerPrice = pv(futurePrice, requiredRateOfReturn, yearsToProject)
    upside = (stickerPrice - currentPrice) / stickerPrice * 100

    # Displaying valuation results
    st.metric("Future EPS", f"{futureEPS:.2f}")
    st.metric("Future Price", f"{futurePrice:.2f}")
    st.metric("Fair Price", f"{stickerPrice:.2f}")
    st.metric("Upside Potential (%)", f"{upside:.2f}")
