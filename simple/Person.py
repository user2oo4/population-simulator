class Person:
    def __init__(self,
                 first_name, last_name, 
                 birth_year, death_year,
                 gender, parents):
        self.id = id(self)
        self.first_name = first_name
        self.last_name = last_name
        self.birth_year = birth_year
        self.death_year = death_year
        self.gender = gender
        self.parents = parents # List of 2 Person objects
        self.partners = [] # List of Person objects
        self.children = [] # List of Person objects

    def __eq__(self, value):
        if not isinstance(value, Person):
            return False
        return self.id == value.id
    
    def __str__(self):
        return f"Person({self.full_name()}, {self.birth_year})"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

    
    def is_ancestor_of(self, other) -> int:
        # Return the number of generations between self and other if True
        # Return -1 otherwise
        if other is None:
            return -1
        
        if other.birth_year < self.birth_year:
            return -1
        
        for parent in other.parents:
            if parent == self:
                return 1
            generation = self.is_ancestor_of(parent)
            if generation == -1:
                continue
            else:
                return generation + 1
        
        return -1
    
    def get_most_recent_common_ancestor(self, other):
        # Return the most recent common ancestor of self and other
        # Return None if there is no common ancestor
        # BFS
        if other is None:
            return None
        
        self_ancestors = {}
        generation = 0
        queue = [(self, generation)]
        
        while queue:
            current, gen = queue.pop(0)
            if current not in self_ancestors:
                self_ancestors[current] = gen
                for parent in current.parents:
                    queue.append((parent, gen + 1))
        
        queue = [(other, generation)]
        most_recent_ancestor = None
        most_recent_generation = float('inf')
        
        while queue:
            current, gen = queue.pop(0)
            if current in self_ancestors:
                total_gen = gen + self_ancestors[current]
                if total_gen < most_recent_generation:
                    most_recent_generation = total_gen
                    most_recent_ancestor = current
            for parent in current.parents:
                queue.append((parent, gen + 1))
        
        return most_recent_ancestor
    
    def possible_to_mate(self, other, current_year) -> bool:
        # Return True if self and other can mate
        if other is None:
            return False
        
        self_age = current_year - self.birth_year
        other_age = current_year - other.birth_year

        max_age = max(self_age, other_age)
        min_age = min(self_age, other_age)

        if min_age < 18 or max_age > 55:
            return False
        
        if min_age * 2 < max_age:
            return False
        
        common_ancestor = self.get_most_recent_common_ancestor(other)
        if common_ancestor is None:
            return True
        generations_self = common_ancestor.is_ancestor_of(self)
        generations_other = common_ancestor.is_ancestor_of(other)

        if min(generations_self, generations_other) < 3:
            return False
        
        return True
    


        

    
    
    
    
