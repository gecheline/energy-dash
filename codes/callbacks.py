from . import dataset

def build_production_dataset(energyData, years, transactions, codes):
    '''
    Filters the dataset to extract data on electricty generation and transforms 
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
        The cleaned and transformed dataset, containing columns on % of total production,
        named fuels and generation purpose tags for main activity vs autoproducer.
    '''
    df_production = energyData.extract_generation_data(years=years, 
                                                       transactions=transactions,
                                                       codes=codes)

    # Compute the total production as a sum of total production from main activity and autoproducers
    # Note: even though there are values for gross and net production in the table, they don't add up to EP + SP
    # and since we're displaying the main activity and autoproducers in the bar chart, this total is most suitable
    total_production = df_production['Quantity (1e6 kW/h)'].loc[:,'EP']+df_production['Quantity (1e6 kW/h)'].loc[:,'SP']
    # add columns for % of total energy production
    df_production['% of total'] = df_production['Quantity (1e6 kW/h)'].apply(lambda x: 100*x/total_production)
    # 
    # clean and transform data set with features needed for plotting
    df_plot = df_production.reset_index()

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
    