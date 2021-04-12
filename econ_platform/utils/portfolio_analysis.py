

class portfolio_analysis(ticker_list, period_type='annual', key=keys['rapidAPI_seekingalpha']):

    def __init__(self):
        self.key = key
        self.period_type = period_type
        self.ticker_list = ticker_list


    def seekingAlpha_estimates(ticker, data_type, period_type='annual', key=keys['rapidAPI_seekingalpha']):
        assert data_type in ['eps', 'revenues']
        assert period_type in ['quarterly', 'annual']
        url = "https://seeking-alpha.p.rapidapi.com/symbols/get-estimates"

        querystring = {"symbol": ticker.lower(),
                    "data_type": data_type,
                    "period_type": period_type}
        headers = {
            'x-rapidapi-key': key,
            'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        df = pd.DataFrame([response.json()['data'][i]['attributes'] for i in range(len(response.json()['data']))])

        df['v'] = df['actual']
        df.loc[df.actual.isna(), 'v'] = df.loc[df.actual.isna(), 'consensus']
        df['v_pct_change'] = df.v.pct_change() * 100

        return df