from . import dataset
import country_converter as coco

def build_production_dataset(energyData, year, transactions, codes):
    '''
    Filters the dataset to extract data on electricty generation and transforms 
    it for plotting.
    
    Parameters
    ----------
    energyData: dataset.EnergyData object
        The full dataset on electricity
    year: int
        A year to filter the data set on. 
    transactions: str, list
        A transaction or list of transactions to filter the data set on.
    codes: bool
        If True, the transactions will be filtered and indexed by their codes instead of strings.
        Use codes=True if passing codes in the transactions parameter.
    
    Returns
    -------
    df_plot: pandas.DataFrame
        The cleaned and transformed dataset, containing columns on % of total production,
        named fuels and generation purpose tags for main activity vs autoproducer.
    '''
    df_production = energyData.extract_generation_data(years=year, 
                                                       transactions=transactions,
                                                       codes=codes)

    # clean and transform data set with features needed for plotting
    df_plot = df_production.reset_index()
    
    # add rows for 'Other' main activity and autoproducers (to sum to 100% in pie chart)
    total_EP_fuels = df_plot['Quantity (1e6 kW/h)'][df_plot['Transaction Code'].str.contains("^015.*?")].sum()
    total_SP_fuels = df_plot['Quantity (1e6 kW/h)'][df_plot['Transaction Code'].str.contains("^016.*?")].sum()
    df_plot = df_plot.append({'Year': year, 
                'Transaction Code': '015O', 
                'Quantity (1e6 kW/h)': (df_production['Quantity (1e6 kW/h)'].loc[:,'EP'].values - total_EP_fuels)[0]},
              ignore_index=True)
    df_plot = df_plot.append({'Year': year, 
                    'Transaction Code': '016O', 
                    'Quantity (1e6 kW/h)': (df_production['Quantity (1e6 kW/h)'].loc[:,'SP'].values - total_SP_fuels)[0]},
                ignore_index=True)

    # add columns for fuel and generation purposes
    fuel_map = dataset.EnergyData.map_code_to_fuel(df_plot['Transaction Code'])
    purpose_map = dataset.EnergyData.map_code_to_purpose(df_plot['Transaction Code'])

    df_plot['Fuel'] = df_plot['Transaction Code'].map(fuel_map)
    df_plot['Purpose'] = df_plot['Transaction Code'].map(purpose_map)
    
    return df_plot


def build_consumption_dataset(energyData, years):
    '''
    Filters the dataset to extract data on electricty consumption and transforms 
    it for plotting.
    
    Parameters
    ----------
    energyData: dataset.EnergyData object
        The full dataset on electricity
    years: int, list
        A year or list of years to filter the data set on. 
    transactions: str, list
        A transaction or list of transactions to filter the data set on.
    codes: bool
        If True, the transactions will be filtered and indexed by their codes instead of strings.
        Use codes=True if passing codes in the transactions parameter.
    
    Returns
    -------
    df_plot: pandas.DataFrame
        The cleaned and transformed dataset, with transaction codes mapped to consumer tags.
    '''
    
    # TODO: generalize to entire set (the implementation below only focuces on case study)
    consumer_map = {'1231': 'Households', 
                    '121': 'Industry', 
                    '122': 'Transport', 
                    '1232': 'Agriculture', 
                    '1235': 'Services'}
    transactions=['121', '1231', '1235', '1232', '122']
    
    df_consumption = energyData.extract_consumption_data(years=years, 
                                                       transactions=transactions,
                                                       codes=True)

    df_plot = df_consumption.reset_index()
    df_plot['Consumer'] = df_plot['Transaction Code'].map(consumer_map)
    return df_plot
    
    
def build_world_data(energyData, year, transaction):
    '''
    Filters the dataset to extract per-country data for a given year and transaction.
    
    energyData: dataset.EnergyData object
        The full dataset on electricity
    year: int
        A year to filter the data set on. 
    transactions: str, list
        A transaction or list of transactions to filter the data set on.
    
    Raises
    ------
    ValueError
        If passed value for transaction does not match any Transaction or Transaction Code in the dataset.
        
    Returns
    -------
    df_plot: pandas.DataFrame
        The cleaned and filtered dataset for plotting.
    '''

    df_plot = energyData.data[(energyData.data['Year'] == year) & (energyData.data['Transaction Code'] == transaction)]
    df_plot['ISO-3'] = coco.convert(df_plot['Country or Area'], to='ISO3')
    
    return df_plot
    
    
        