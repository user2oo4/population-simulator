import Person
import numpy as np
from scipy.optimize import brentq

class Population:
    def __init__(self, 
                 period_length, 
                 starting_population=2,
                 ending_population=1000,
                 life_expectancy=70,
                 newborn_death_rate=0.005):
        self.period_length = period_length
        self.current_year = 20 # put starting population into year 20 so they can have children right away
        self.life_expectancy = life_expectancy
        self.newborn_death_rate = newborn_death_rate

        self.growth_rate = np.log(ending_population / starting_population) / (period_length)
        self.death_age_distribution = self.generate_death_age_distribution()
        self.people = self.generate_starting_population(starting_population)

        self.annual_population = {self.current_year: starting_population}
        self.annual_birth = {}
        for year in range(self.current_year + 1, self.current_year + period_length + 1):
            prev_population = self.annual_population[year - 1]
            new_population = int(prev_population * np.exp(self.growth_rate))
            self.annual_population[year] = new_population
            self.annual_birth[year] = new_population - prev_population
        self.annual_death = {}  
        
        
    
    def generate_death_age_distribution(self, newborn_death_rate=None, life_expectancy=None, b=None):
        # Gompertz mortality model with infant mortality
        # random age at death (X)
        # X = 1/b * ln(1 - b/a * ln(U)) where U ~ Uniform(0,1)
        # b: aging rate (0.08 to 0.1 for humans)

        if newborn_death_rate is None:
            newborn_death_rate = self.newborn_death_rate
        if life_expectancy is None:
            life_expectancy = self.life_expectancy
        if b is None:
            b = 0.085  # Typical human aging rate

        life_expectancy_adjusted = life_expectancy / (1 - newborn_death_rate)
        distribution = {}

        # 1. Define the Mean function for the Gompertz distribution
        # Solve for 'a' to match the desired life expectancy
        def gompertz_mean_diff(a_log):
            a_val = np.exp(a_log)
            # Integration of survival function to get mean
            # S(x) = exp((a/b) * (1 - e^(bx)))
            integrand = lambda x: np.exp((a_val / b) * (1 - np.exp(b * x)))
            x = np.linspace(0, 150, 1000)
            dx = x[1] - x[0]
            mean_val = np.sum(integrand(x)) * dx
            return mean_val - life_expectancy_adjusted

        a_log = brentq(gompertz_mean_diff, -10, 10)
        a = np.exp(a_log)

        # 2. Generate data points for age at death
        U = np.random.uniform(0, 1, int(10000 - newborn_death_rate * 10000))
        U = np.clip(U, newborn_death_rate, 1)  # Avoid log(0)

        age_at_death = (1 / b) * np.log(1 - (b / a) * np.log(U))
        # print(age_at_death)
        for age in age_at_death:
            age_rounded_down = int(np.floor(age))
            if age_rounded_down in distribution:
                distribution[age_rounded_down] += 1
            else:
                distribution[age_rounded_down] = 1

        distribution[0] = newborn_death_rate * 10000
        
        for key, value in distribution.items():
            distribution[key] = value / 10000.0  # Normalize to probabilities
        
        return distribution


    def generate_starting_population(self, n):
        people = []
        for i in range(1, n + 1, 1):
            death_age = np.random.choice(list(self.death_age_distribution.keys()), 
                                         p=list(self.death_age_distribution.values()))
            person = Person.Person(
                first_name=f"M_{i}",
                last_name=f"D_{i}",
                birth_year=0,
                death_year=death_age,
                gender="M" if i % 2 == 0 else "F",
                parents=[]
            )
            people.append(person)

            self.annual_death[person.death_year] = self.annual_death.get(person.death_year, 0) + 1

        return people

    def simulate_population_growth(self):
        for year in range(self.current_year + 1, self.current_year + self.period_length + 1):
            self.simulate_year(year)
    
    def simulate_year(self, year):
        # Simulate births
        births = self.annual_birth.get(year, 0)
        for i in range(births):
            self.simulate_birth(year)
    
    def simulate_birth(self, year):
        # Randomly select parents from current population
        # Check if they already have a partner
        pass  # Implementation of birth simulation goes here



if __name__ == "__main__":
    print("Generating population...")
    pop = Population(period_length=10, starting_population=10, life_expectancy=70, newborn_death_rate=0.005)
    age_distribution = pop.generate_death_age_distribution()
    for age, prob in sorted(age_distribution.items()):
        print(f"Age: {age}, Probability (percentage): {prob * 100:.2f}%")
    sum = np.sum(list(age_distribution.values()))
    print(sum)

            