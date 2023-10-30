'''
Processes raw data and produces a new CSV or other type of output object
representing the raw input alongside a 'damage channel'

For example, a colum for 'input signal amplitude vs time' with a column
for 'probable damage vs time'

Statistical probability of damage incurred at time = x would be a good way to 
represent our output data
'''
class SignalProcessor():

    '''
    Processor class creates a processed_data object when called
    '''
    def __call__(self, raw_data):

        decomposed_data = self.__decompose(raw_data)
        return self.__process(decomposed_data)
    
    '''
    Deconstruct the raw audio into usable components such as Power, Frequencies, Etc.
    What ever useful components whe can devise to disposition the sample
    '''
    def __decompose(self, raw_data):

        power = []
        frequencies = []
        trigger_signal = []

        decomposed_data = [
            power,
            frequencies,
            trigger_signal # definitely required for processing
        ]

        return decomposed_data
    
    '''
    Return a table/csv object representing our raw data alongside our annotations and any
    additional channels devised to indicate damage recieved by the UAS

    May be done through a pure math, 'hardcoded' approach or through a teachable machine-learning 
    depending on which implementation proves most doable and most robust
    '''
    def __process(self, data_components):
        return