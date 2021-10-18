import numpy as np 
import pandas as pd 

class EnergyData:
    
    def __init__(self, filename):
        '''
        Initializes the "Total Electricity" data set downloaded from http://data.un.org/Data.aspx?d=EDATA&f=cmID%3aEL
        
        Parameters
        ----------
        filename: str
            Path to the file containing data.
            
        Attributes
        ----------
        data: pandas DataFrame
        
        Methods
        -------
        transform_generation_data
        transform_consumption_data
        '''
        df = pd.read_csv(filename, dtype={'Commodity Code': 'str', 
                                        'Country or Area Code': np.int32,
                                        'Country or Area': 'str', 
                                        'Transaction Code': 'str', 
                                        'Commodity - Transaction Code': 'str',
                                        'Commodity - Transaction': 'str',
                                        'Year': np.int32,
                                        'Unit': 'str',
                                        'Quantity': np.float64,
                                        'Quantity Footnotes': np.float64},
                         skipfooter=2)
        # clean up the data: drop columns with only one value (commodity)
        # substitute commodity - transaction with transaction only
        # quantity footnotes indicate estimates and we're not using them here, so will drop them as well
        df['Transaction'] = df['Commodity - Transaction'].apply(lambda x: x.split(' - ')[-1])
        df = df.rename(columns={'Quantity': 'Quantity (1e6 kW/h)'}).drop(columns='Unit')
        df.drop(columns = ['Commodity Code', 'Commodity - Transaction Code', 'Commodity - Transaction', 'Quantity Footnotes'], 
                inplace=True)
        self.data = df
        
        
    def extract_generation_data(self, years=None, transactions=None, codes=False):
        '''
        Extracts the data pertaining to production of electricity.
        Can be further filtered on specific years and transactions within the data set.
        
        Parameters
        ----------
        years: int, list
            A year or list of years to filter the data set on. 
        transactions: str, list
            A transaction or list of transactions to filter the data set on.
        codes: bool
            If True, the transactions will be filtered and indexed by their codes instead of strings.
            Use codes=True if passing codes in the transactions parameter.
            
        Returns
        -------
        pandas.DataFrame object
            Filtered data set on production data (for specified years and transactions, if provided)
        '''
        
        if codes:
            columns = ['Year', 'Transaction Code']
        else:
            columns = ['Year', 'Transaction']
        
        # The production data have transaction codes starting with 01.
        # The transaction code for total production - main activity is EP
        # The Transaction code for total production - autoproducer is SP
        df_production = self.data[self.data['Transaction Code'].str.contains("01.*?|EP|SP")].groupby(
                by=columns, as_index=True).sum().drop(
                columns=['Country or Area Code'])
        
        if years is not None:
            if transactions is not None:
                return df_production.loc[years, transactions, :]
            else:
                return df_production.loc[years,:, :]
        else:
            if transactions is not None:
                return df_production.loc[:, transactions, :]
            else:
                return df_production
                
        
    def extract_consumption_data(self, years=None, transactions=None, codes=False):
        '''
        Extracts the data pertaining to consumption of electricity.
        Can be further filtered on specific years and transactions within the data set.
        
        Parameters
        ----------
        years: int, list
            A year or list of years to filter the data set on. 
        transactions: str, list
            A transaction or list of transactions to filter the data set on.
        codes: bool
            If True, the transactions will be filtered and indexed by their codes instead of strings.
            Use codes=True if passing codes in the transactions parameter.
            
        Returns
        -------
        pandas.DataFrame object
            Filtered data set on consumption data (for specified years and transactions, if provided)
        '''
        
        if codes:
                columns = ['Year', 'Transaction Code']
        else:
            columns = ['Year', 'Transaction']
        
        # The consumption data have transaction codes starting with 12.

        df_consumption = self.data[self.data['Transaction Code'].str.contains("12.*?")].groupby(
                by=columns, as_index=True).sum().drop(
                columns=['Country or Area Code'])
        
        if years is not None:
            if transactions is not None:
                return df_consumption.loc[years, transactions, :]
            else:
                return df_consumption.loc[years,:, :]
        else:
            if transactions is not None:
                return df_consumption.loc[:, transactions, :]
            else:
                return df_consumption

    
    @staticmethod
    def map_code_to_fuel(codes):
        '''
        Transforms a list of electricity production codes to the fuel used for generation.
        
        Parameters
        ----------
        codes: list, pandas Series, array
            The electricity transaction codes to transform
            
        Returns
        -------
        fuel_map: dict
            A mapping between the codes and fuels.
        '''
        
        fuel_map = {}
        for code in codes:
            if code in ['EP', 'SP']:
                fuel_map[code] = 'Total'
            elif code == '01':
                fuel_map[code] = 'Gross'
            elif code == '019':
                fuel_map[code] = 'Net'
            elif code[-1] == 'C':
                fuel_map[code] = 'Combustible Fuels'
            elif code[-1] == 'S':
                fuel_map[code] = 'Solar'
            elif code[-1] == 'N':
                fuel_map[code] = 'Nuclear'
            elif code[-1] == 'H':
                fuel_map[code] = 'Chemical Heat'
            elif code[-1] == 'W':
                fuel_map[code] = 'Wind'
            elif code[-1] == 'Y':
                fuel_map[code] = 'Hydro'
            else:
                fuel_map[code] = 'Other'
                
        return fuel_map
            
    
    @staticmethod
    def map_code_to_purpose(codes):
        '''
        Transforms a list of electricity production codes to the production purpose: 
        main activity vs autoproducer.
        
        Parameters
        ----------
        codes: list, pandas Series, array
            The electricity transaction codes to transform
            
        Returns
        -------
        purpose_map: dict
            A mapping between the codes and purposes.
        '''
        purpose_map = {}
        for code in codes:
            if code[1:3] == '15' or code == 'EP':
                purpose_map[code] = 'Main activity'
            elif code[1:3] == '16' or code == 'SP':
                purpose_map[code] = 'Autoproducer'
            else:
                purpose_map[code] = 'Other'
                
        return purpose_map