__author__ = 'James'
from monopyly import *
from .property_with_probs import *


class PropertyProbCalcs():
    def __init__(self):
        self.properties_with_probs={}
        self._add_all_properties()
        

    def rolls_to_recoup(self, property_name, num_houses=None, set_owned=None,number_of_stations_owned=None):
        # Returns the number of opponent rolls expected to recoup
        # the cumulative cost of this property with set number of houses
        if num_houses is None and number_of_stations_owned is None:
            #Error - not called correctly
            print('Error calculating rolls_to_recoup, must pass either num houses or stations owned')
            return 9999
        if not number_of_stations_owned is None:
            return self.properties_with_probs[property_name].rolls_to_recoup(number_of_stations_owned)

        if num_houses > 0:
            return self.properties_with_probs[property_name].rolls_to_recoup(num_houses)
        
        if set_owned:
            return self.properties_with_probs[property_name].rolls_recoup_all_sets
      
        return self.properties_with_probs[property_name].rolls_recoup_single_prop

    def income_per_turn(self, property_name, num_houses=None, set_owned=None, number_of_stations_owned=None):
        # Returns the number of opponent rolls expected to recoup
        # the cumulative cost of this property with set number of houses
        if num_houses is None and number_of_stations_owned is None:
            #Error - not called correctly
            return 0
        if not number_of_stations_owned is None:
            return self.properties_with_probs[property_name].income(number_of_stations_owned)

        if num_houses > 0:
            return self.properties_with_probs[property_name].income(num_houses)

        if set_owned:
            return self.properties_with_probs[property_name].income_all_sets

        return self.properties_with_probs[property_name].income_single_prop

    def _add_all_properties(self):
       # self.properties_with_probs[Square.Name.MAYFAIR]=PropertyProb(Square.Name.MAYFAIR, 322.1658,	124.8429,
      #                                                               [80.5414,	20.1354,	10.0677,	26.8471,	26.8471],
      #      1.2416, 2.4832, [4.9664, 14.8992, 34.7647, 42.2143, 49.6639] )

     #   self.properties_with_probs[Square.Name.PARK_LANE] = PropertyProb(Square.Name.PARK_LANE, 485.5496,
     #                                                                    130.4382,
    #                                                                   [92.4856, 29.8800, 16.1850, 48.5550,48.5550],
     #       0.7208,	1.4417,	[3.6042, 10.2976,	22.6547, 26.7738, 30.8928])

        self.properties_with_probs[Square.Name.OLD_KENT_ROAD] = PropertyProb(Square.Name.OLD_KENT_ROAD,1494.5282,370.8991,[415.1467,124.544,41.5147,35.584,27.6764],0.0401,0.0803,[0.2007,0.6022,1.8066,3.2117,5.0183])
        self.properties_with_probs[Square.Name.WHITECHAPEL_ROAD] = PropertyProb(Square.Name.WHITECHAPEL_ROAD,736.4116,295.4227,[204.5588,61.3676,20.4559,17.5336,18.8823],0.0815,0.163,[0.4074,1.2221,3.6664,6.5181,9.1661])
        self.properties_with_probs[Square.Name.THE_ANGEL_ISLINGTON] = PropertyProb(Square.Name.THE_ANGEL_ISLINGTON,781.8495,178.4163,[130.3083,39.0925,13.0308,18.0427,15.637],0.1279,0.2558,[0.6395,1.9185,5.7556,8.5268,11.7243])
        self.properties_with_probs[Square.Name.EUSTON_ROAD] = PropertyProb(Square.Name.EUSTON_ROAD,761.9564,177.3596,[126.9927,38.0978,12.6993,17.5836,15.2391],0.1312,0.2625,[0.6562,1.9686,5.9058,8.7494,12.0304])
        self.properties_with_probs[Square.Name.PENTONVILLE_ROAD] = PropertyProb(Square.Name.PENTONVILLE_ROAD,691.8736,198.0109,[96.0936,38.4374,11.5312,15.375,15.375],0.1734,0.3469,[0.8672,2.168,6.5041,9.7561,13.0082])
        self.properties_with_probs[Square.Name.PALL_MALL] = PropertyProb(Square.Name.PALL_MALL,547.7404,137.3005,[130.4144,39.1243,13.0414,22.3568,31.2995],0.2556,0.5112,[1.278,3.8339,11.5018,15.9747,19.1697])
        self.properties_with_probs[Square.Name.WHITEHALL] = PropertyProb(Square.Name.WHITEHALL,643.9566,142.6429,[153.323,45.9969,15.3323,26.2839,36.7975],0.2174,0.4348,[1.087,3.2611,9.7833,13.5879,16.3054])
        self.properties_with_probs[Square.Name.NORTHUMBERLAND_AVENUE] = PropertyProb(Square.Name.NORTHUMBERLAND_AVENUE,549.7065,151.64,[114.5222,34.3567,12.8837,20.614,20.614],0.2911,0.5821,[1.4553,4.366,12.1277,16.9788,21.8298])
        self.properties_with_probs[Square.Name.BOW_STREET] = PropertyProb(Square.Name.BOW_STREET,479.7082,112.8324,[88.8348,28.7005,10.6602,18.6553,18.6553],0.3752,0.7505,[1.8761,5.3604,14.7411,20.1015,25.4619])
        self.properties_with_probs[Square.Name.MARLBOROUGH_STREET] = PropertyProb(Square.Name.MARLBOROUGH_STREET,455.7593,111.4549,[84.3999,27.2677,10.128,17.724,17.724],0.3949,0.7899,[1.9747,5.6421,15.5157,21.1578,26.7999])
        self.properties_with_probs[Square.Name.VINE_STREET] = PropertyProb(Square.Name.VINE_STREET,444.5587,119.7646,[74.0931,25.4034,9.3591,17.7823,17.7823],0.4499,0.8998,[2.2494,6.1859,16.8707,22.4942,28.1178])
        self.properties_with_probs[Square.Name.STRAND] = PropertyProb(Square.Name.STRAND,467.5215,109.9014,[106.2549,35.861,12.7506,32.7872,32.7872],0.4706,0.9411,[2.3528,6.5356,18.2998,22.8748,27.4497])
        self.properties_with_probs[Square.Name.FLEET_STREET] = PropertyProb(Square.Name.FLEET_STREET,476.1134,110.3696,[108.2076,36.5201,12.9849,33.3898,33.3898],0.4621,0.9241,[2.3104,6.4177,17.9696,22.462,26.9544])
        self.properties_with_probs[Square.Name.TRAFALGAR_SQUARE] = PropertyProb(Square.Name.TRAFALGAR_SQUARE,400.9446,112.6859,[83.5301,25.059,11.1373,28.6389,28.6389],0.5986,1.1972,[2.9929,8.9788,22.447,27.6846,32.9223])
        self.properties_with_probs[Square.Name.LEICESTER_SQUARE] = PropertyProb(Square.Name.LEICESTER_SQUARE,465.834,115.2667,[89.5835,26.875,12.5798,33.7858,33.7858],0.5581,1.1163,[2.7907,8.3721,20.296,24.7357,29.1754])
        self.properties_with_probs[Square.Name.COVENTRY_STREET] = PropertyProb(Square.Name.COVENTRY_STREET,469.1373,115.4679,[90.2187,27.0656,12.669,34.0253,34.0253],0.5542,1.1084,[2.771,8.3131,20.153,24.5615,28.97])
        self.properties_with_probs[Square.Name.PICCADILLY] = PropertyProb(Square.Name.PICCADILLY,478.5081,122.6644,[85.4479,25.6344,12.5556,35.1557,35.1557],0.5852,1.1703,[2.9258,8.7773,20.7241,24.9909,29.2576])
        self.properties_with_probs[Square.Name.REGENT_STREET] = PropertyProb(Square.Name.REGENT_STREET,457.2156,114.7708,[101.6035,30.481,15.5394,39.6253,45.2861],0.6561,1.3123,[3.2807,9.8422,22.7127,27.76,32.1764])
        self.properties_with_probs[Square.Name.OXFORD_STREET] = PropertyProb(Square.Name.OXFORD_STREET,466.7445,115.362,[103.721,31.1163,15.8632,40.4512,46.2299],0.6427,1.2855,[3.2137,9.6412,22.249,27.1933,31.5195])
        self.properties_with_probs[Square.Name.BOND_STREET] = PropertyProb(Square.Name.BOND_STREET,485.6852,122.2951,[90.4201,28.3316,15.4536,42.4975,42.4975],0.6589,1.3177,[3.5296,10.5889,23.5308,28.237,32.9431])
        self.properties_with_probs[Square.Name.PARK_LANE] = PropertyProb(Square.Name.PARK_LANE,485.5496,130.4382,[92.4856,29.88,16.185,48.555,48.555],0.7208,1.4417,[3.6042,10.2976,22.6547,26.7738,30.8928])
        self.properties_with_probs[Square.Name.MAYFAIR] = PropertyProb(Square.Name.MAYFAIR,322.1658,124.8429,[80.5414,20.1354,10.0677,26.8471,26.8471],1.2416,2.4832,[4.9664,14.8992,34.7647,42.2143,49.6639])
        self.properties_with_probs[Square.Name.KINGS_CROSS_STATION] = StationProb(Square.Name.KINGS_CROSS_STATION,[260.3346,89.2966,33.9793,13.7128],[0.7682,1.5365,3.073,6.1459])
        self.properties_with_probs[Square.Name.MARYLEBONE_STATION] = StationProb(Square.Name.MARYLEBONE_STATION,[275.1957,92.1411,34.6302,13.8707],[0.7268,1.4535,2.907, 5.814])

        self.properties_with_probs[Square.Name.FENCHURCH_STREET_STATION] = StationProb(Square.Name.FENCHURCH_STREET_STATION,[246.8124,86.5847,33.3434,13.5564],[0.8103,1.6207,3.2413,6.4827])

        self.properties_with_probs[Square.Name.LIVERPOOL_STREET_STATION] = StationProb(Square.Name.LIVERPOOL_STREET_STATION,[349.2577,104.508,37.2832,14.4902],[0.5726,1.1453,2.2906,4.5811])
        #self.properties_with_probs[Square.Name.WATER_WORKS]
        #self.properties_with_probs[Square.Name.ELECTRIC_COMPANY]


