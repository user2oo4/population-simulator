import Person
import Simulator
import numpy as np

class Population:
    def __init__(self, 
                 period_length, 
                 starting_population=2,
                 ending_population=1000,
                 life_expectancy=70,
                 newborn_death_rate=0.005):
        self.period_length = period_length
        self.current_year = 20 # put starting population into year 20 so they can have children right away
        self.starting_population = starting_population
        self.ending_population = ending_population
        self.life_expectancy = life_expectancy
        self.newborn_death_rate = newborn_death_rate
        self.simulator = Simulator(period_length, starting_population, ending_population, life_expectancy, newborn_death_rate)

    


            