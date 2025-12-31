# This is the class to simulate population changes over time
# Should simulate births, deaths, marriages (year by year)
import numpy as np
import utils
import Person

class Simulator:
    def __init__(self, period_length: int, starting_population: int, 
                 ending_population: int, life_expectancy: int, newborn_death_rate: float):
        
        # Parameters from Population
        self.period_length = period_length
        self.current_year = 20 # put starting population into year 20 so they can have children right away
        self.starting_population = starting_population
        self.ending_population = ending_population
        self.life_expectancy = life_expectancy
        self.newborn_death_rate = newborn_death_rate

        # Initialize data structures
        self.people = {}
        self.couples = set() # set of tuples (male_id, female_id)
        self.single_m = set()
        self.single_f = set()

    def intialize_simulation(self):
        # Calculated simulation parameters
        self.growth_rate = np.log(self.ending_population / self.starting_population) / (self.period_length)
        print("growth rate = ", self.growth_rate)
        self.death_age_distribution = utils.generate_death_age_distribution(newborn_death_rate=self.newborn_death_rate,
                                                                            life_expectancy=self.life_expectancy)
        
        print("Sum: ", sum(self.death_age_distribution.values()))

        # Annual statistics and events
        self.annual_population = {self.current_year: self.starting_population}
        self.annual_birth = {}
        for year in range(self.current_year + 1, self.current_year + self.period_length + 1):
            prev_population = self.annual_population[year - 1]
            new_population = prev_population * np.exp(self.growth_rate)
            self.annual_population[year] = new_population
            # print(f"annual population {year} = ", self.annual_population[year])
        self.annual_death = {}
        self.annual_adulting = {} # people turning 18 each year
        self.current_population = self.starting_population

        # Generate starting population
        self.people, self.couples, self.single_m, self.single_f, self.annual_death = utils.generate_starting_population(
            self.death_age_distribution, self.starting_population)
    
    def simulate_year(self, year: int):
        # 1. Simulate deaths
        if year in self.annual_death:
            for person in self.annual_death[year]:
                if person.id in self.single_m:
                    self.single_m.remove(person.id)
                if person.id in self.single_f:
                    self.single_f.remove(person.id)
                if person.partner_id is not None:
                    partner = self.people[person.partner_id]
                    partner.partner_id = None
                    if partner.gender == "M":
                        self.single_m.add(partner.id)
                    else:
                        self.single_f.add(partner.id)
        
        # 2. Move kids turning 18 to single pool
        if year in self.annual_adulting:
            for person in self.annual_adulting[year]:
                if person.gender == "M":
                    self.single_m.add(person.id)
                else:
                    self.single_f.add(person.id)
        
        # 3. Mating (forming couples)
        # Call a mating function here
        new_couples = utils.random_mate(self, self.people)
        for couple in new_couples:
            self.couples.add(couple)
            if couple[0] in self.single_m:
                self.single_m.remove(couple[0])
            if couple[1] in self.single_f:
                self.single_f.remove(couple[1])

        # 4. Simulate births
        # Select couples to have children based on birth rate
        if year in self.annual_population:
            if self.couples.__len__() == 0:
                return
            birth_rate = (self.annual_population[year] - self.current_population) / self.couples.__len__()
            for couple in self.couples:
                if np.random.rand() < birth_rate:
                    father = self.people[couple[0]]
                    mother = self.people[couple[1]]
                    if father.gender != "M":
                        father, mother = mother, father
                    child = utils.create_child(mother, father, year, self.death_age_distribution)
                    self.current_population += 1
                    self.people[child.id] = child
                    father.children_ids.append(child.id)
                    mother.children_ids.append(child.id)
                    if (year + 18) not in self.annual_adulting:
                        self.annual_adulting[year + 18] = []
                    self.annual_adulting[year + 18].append(child)
    
    def simulate(self):
        self.intialize_simulation()
        for year in range(self.current_year + 1, self.current_year + self.period_length + 1):
            self.simulate_year(year)
    
    def print_data(self, folder_path: str):
        # Print out data to files
        with open(f"{folder_path}/people.txt", "w") as f:
            for person_id, person in self.people.items():
                f.write(f"{person_id}, {person.first_name}, {person.last_name}, {person.birth_year}, {person.death_year}, {person.gender}, {person.mom_id}, {person.dad_id}, {person.partner_id}, {person.children_ids}\n")
        
        # Print out annual statistics
        with open(f"{folder_path}/annual_statistics.txt", "w") as f:
            f.write("Year, Population, Births, Deaths, Adulting\n")
            for year in range(self.current_year, self.current_year + self.period_length + 1):
                population = self.annual_population.get(year, 0)
                births = self.annual_birth.get(year, 0)
                deaths = len(self.annual_death.get(year, []))
                adulting = len(self.annual_adulting.get(year, []))
                f.write(f"{year}, {population}, {births}, {deaths}, {adulting}\n")
        
        # Print out couples
        with open(f"{folder_path}/couples.txt", "w") as f:
            for couple in self.couples:
                f.write(f"{couple[0]}, {couple[1]}\n")
        
        # Draw graphs
        import matplotlib.pyplot as plt

        # Population over time
        years = list(self.annual_population.keys())
        populations = list(self.annual_population.values())
        plt.plot(years, populations)
        plt.xlabel("Year")
        plt.ylabel("Population")
        plt.savefig(f"{folder_path}/population_over_time.png")

        # Last name distribution
        last_name_count = {}
        for person in self.people.values():
            last_name_count[person.last_name] = last_name_count.get(person.last_name, 0) + 1

        # Plot last name distribution
        plt.figure()
        plt.bar(last_name_count.keys(), last_name_count.values())
        plt.xlabel("Last Name")
        plt.ylabel("Count")
        plt.savefig(f"{folder_path}/last_name_distribution.png")

    def print_family_tree(self, person_id: str, max_generations: int, folder_path: str):
        # Print family tree of a person up to max_generations
        person = self.people.get(person_id, None)
        if person is None:
            return
        
        with open(f"{folder_path}/family_tree_{person_id}.txt", "w") as f:
            def dfs(current_person: Person.Person, generation: int):
                if generation > max_generations:
                    return
                f.write("  " * generation + f"{current_person.full_name()} ({current_person.birth_year}-{current_person.death_year})\n")
                for child_id in current_person.children_ids:
                    child = self.people.get(child_id, None)
                    if child is not None:
                        dfs(child, generation + 1)
            dfs(person, 0)

if __name__ == "__main__":
    sim = Simulator(
        period_length=100,
        starting_population=10,
        ending_population=1000,
        life_expectancy=70,
        newborn_death_rate=0.05
    )
    sim.simulate()
    sim.print_data(folder_path="output")
