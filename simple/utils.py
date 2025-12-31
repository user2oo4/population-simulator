from Person import Person

import numpy as np
from scipy.optimize import brentq

# For utility functions related to population simulation
def generate_death_age_distribution(newborn_death_rate=None, life_expectancy=None, b=None):
    # Gompertz mortality model with infant mortality
    # random age at death (X)
    # X = 1/b * ln(1 - b/a * ln(U)) where U ~ Uniform(0,1)
    # b: aging rate (0.08 to 0.1 for humans)

    if newborn_death_rate is None:
        raise ValueError("newborn_death_rate must be provided")
    if life_expectancy is None:
        raise ValueError("life_expectancy must be provided")
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
    
    sum = 0.0
    for key in sorted(distribution.keys()):
        sum += distribution[key]
    
    if sum < 1.0:
        distribution[max(distribution.keys())] += 1.0 - sum  # Adjust last value to make sum 1.0
    
    return distribution

def generate_starting_population(death_age_distribution, n):
    people = {}
    couples = set() # set of tuples
    single_m = set()
    single_f = set()
    annual_death = {}

    for i in range(1, n + 1, 1):
        death_age = np.random.choice(list(death_age_distribution.keys()), 
                                        p=list(death_age_distribution.values()))
        person = Person(
            first_name=f"M_{i}",
            last_name=f"D_{i}",
            birth_year=0,
            death_year=death_age,
            gender="M" if i % 2 == 0 else "F",
            mom_id=None,
            dad_id=None
        )
        people[person.id] = person
        if person.gender == "M":
            if person.id + 1 <= n:
                couples.add((person.id, person.id + 1))
            else:
                single_m.add(person.id)

        if person.death_year not in annual_death:
            annual_death[person.death_year] = []
        annual_death[person.death_year].append(person)

    return people, couples, single_m, single_f, annual_death

def create_child(mom: Person, dad: Person, birth_year: int, death_age_distribution):
    death_age = np.random.choice(list(death_age_distribution.keys()), 
                                        p=list(death_age_distribution.values()))
    gender = "M" if np.random.rand() < 0.5 else "F"
    child = Person(
        first_name=mom.first_name,
        last_name=dad.last_name,
        birth_year=birth_year,
        death_year=birth_year + death_age,
        gender=gender,
        mom_id=mom.id,
        dad_id=dad.id
    )
    return child

def random_mate(self, people, avg_age_diff=2):
    # simple random mating algorithm
    # since age is sorted, we can keep 2 pointers to find mates within acceptable age range
    mated_couples = set()
    current_f_index = 0
    for male in self.single_m:
        # Randomly assign mating chance based on current age
        current_m_age = self.current_year - self.people[male].birth_year
        # Goes up by from 18-30, then down after 30
        mating_chance = -0.01 * (current_m_age - 30) ** 2 + 0.36
        if np.random.rand() > mating_chance:
            continue

        if current_f_index >= len(self.single_f):
            break
        age_diff = np.random.normal(loc=avg_age_diff, scale=2)
        while current_f_index < len(self.single_f) and (self.people[self.single_f[current_f_index]].birth_year > self.people[male].birth_year + age_diff):
            current_f_index += 1
        while current_f_index >= 0 and (self.people[self.single_f[current_f_index]].birth_year < self.people[male].birth_year - age_diff):
            current_f_index -= 1
        if current_f_index < len(self.single_f):
            female = self.single_f[current_f_index]
            if check_incest(people, male, female) == False:
                mated_couples.add((male.id, female.id))
        
    return mated_couples

def check_incest(people, male, female):
    # Check if two people are within 3 generations
    male_ancestors_id = set()
    queue = [male]
    for gen in range(3):
        next_queue = []
        for person in queue:
            if person.mom_id is not None:
                male_ancestors_id.add(person.mom_id)
                next_queue.append(people[person.mom_id])
            if person.dad_id is not None:
                male_ancestors_id.add(person.dad_id)
                next_queue.append(people[person.dad_id])
        queue = next_queue

    queue = []
    for gen in range(3):
        next_queue = []
        for person in queue:
            if person.id in male_ancestors_id:
                return True
            if person.mom_id is not None:
                next_queue.append(people[person.mom_id])
            if person.dad_id is not None:
                next_queue.append(people[person.dad_id])
        queue = next_queue
    return False