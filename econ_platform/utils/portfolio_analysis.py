import pandas as pd
import datetime
import requests

# auth
basepath = Path(__file__).parent.parent

with open(str(basepath) + '/keys/keys.json', 'r') as key_file:
    keys = json.load(key_file)

class portfolio_analysis:

    def __init__(self, ticker_list, period_type='annual', call_type='stock', country='united states'):
        assert period_type in ['quarterly', 'annual']
        
        self.period_type = period_type
        self.ticker_list = ticker_list
        self.country = country
        # year
        currentDateTime = datetime.datetime.now()
        self.date = currentDateTime.date()
        self.year = int(self.date.strftime("%Y"))
        self.call_type=call_type

    
    def create_estimates(self, data_type, from_date='01/01/2015', to_date=convert_date_format(str(datetime.datetime.now().date()), 'Investing.com')):
        estimate_dict = dict()
        for ticker in self.ticker_list:
            estimate_dict[ticker] = dict()
            estimate_dict[ticker]['data'] = self._seekingAlpha_estimates(ticker, data_type)
            estimate_dict[ticker]['average_growth'] = estimate_dict[ticker]['data']['v_pct_change'].mean()
            estimate_dict[ticker]['growth_type'] = self._determine_growth_type(estimate_dict[ticker]['average_growth'])
            estimate_dict[ticker]['price_history'] = self._investing_api(ticker, from_date, to_date)
        
        self.estimate_dict = estimate_dict
        print("Created `estimate_dict`")
        
    
    def calculate_price_range(self, multiplier=[1.5, 2]):
        """
        For stable grower, min max estimation based on diluted eps is fairly accurate.
        However, when it comes to fast grower, market sentiment become relatively more important.
        For slow grower, it refers to divident paying stocks. Thus min max price should be calculated differently.
        """
        
        for ticker in self.ticker_list:
            self._calculate_price_range(ticker, multiplier)
        print("Created price_range")
        
        
    def plot_price_range(self, ticker, name=None):
        data = self.estimate_dict[ticker]['price_history']

        trace = go.Scatter(x=data['Date'],
                           y=data['Close'],
                           name='apple')

        fig = go.Figure()
        fig.add_trace(trace)
        fig.add_hline(y=self.estimate_dict[ticker]['price_range'][0])
        fig.add_hline(y=self.estimate_dict[ticker]['price_range'][1])
        
        return fig
                
        
    def _investing_api(self, ticker, from_date, to_date):
        """
        call_type: etf, stock, fund, index
        ticker: str. ticker name
        from_date: dd/mm/yyyy
        """
        if self.call_type == 'etf':
            # search name from ticker and return
            etfs = investpy.etfs.get_etfs(country=self.country)
            etf_name = etfs.loc[(etfs.symbol == ticker), 'name'].tolist()[0]
            data = investpy.get_etf_historical_data(etf=etf_name, country=self.country,
                                                    from_date=from_date,
                                                    to_date=to_date).reset_index()
        if self.call_type == 'stock':
            data = investpy.stocks.get_stock_historical_data(stock=ticker, country=self.country,
                                                             from_date=from_date,
                                                             to_date=to_date).reset_index()
            
        return data
        
        
    def _calculate_price_range(self, ticker, multiplier):
        """
        Calculate price range for one ticker
        """
        next_year_dil_eps = self.estimate_dict[ticker]['data'].loc[\
                                    self.estimate_dict[ticker]['data'].year==self.year+1, 'consensus'].values[0]
        average_growth = self.estimate_dict[ticker]['average_growth']
        self.estimate_dict[ticker]['price_range'] = [next_year_dil_eps*average_growth*m for m in multiplier]
        
    
    def _determine_growth_type(self, growth):
        if (growth>10)&(growth<20):
            return "stable grower"
        elif growth>=20:
            return "fast grower"
        elif growth<=10:
            return "slow grower"
    
        
    def _seekingAlpha_estimates(self, ticker, data_type, key=keys['rapidAPI_seekingalpha']):
        assert data_type in ['eps', 'revenues']        
        url = "https://seeking-alpha.p.rapidapi.com/symbols/get-estimates"

        querystring = {"symbol": ticker.lower(),
                    "data_type": data_type,
                    "period_type": self.period_type}
        headers = {
            'x-rapidapi-key': key,
            'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        df = pd.DataFrame([response.json()['data'][i]['attributes'] for i in range(len(response.json()['data']))])
        
        df = df.loc[df.year.isin([self.year-2, self.year-1, self.year, self.year+1])]
        
        df['v'] = df['actual']
        df.loc[df.actual.isna(), 'v'] = df.loc[df.actual.isna(), 'consensus']
        df['v_pct_change'] = df.v.pct_change() * 100

        return df
    
        