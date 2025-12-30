# Population simulation

## Problem

- Simulate population growth
- Birth of the people have to be simulated. Each person should have information about their ancestors stored (well, their parents are probably enough)

### Input
- Starting population
- Period of time
- Ending population
- Life expectancy

### Output
- All people ever lived, their parents, etc.
- Maybe visualize with a graph (can do generations but there will be cross generation mating later, also the graph's gonna be too big maybe)
- So maybe write some functions to track back and find LCA maybe
- Idk if we should encode the name in some way (actually this maybe interesting, if we assign a number of last names at first we can see the ending distribution of the last names. I suppose it should be relatively the same but it can fluctuate quite a bit actually depends on the first few generations)

### Method
- Need: 
  - Age of death distribution (maybe rate of newborn death as well idk)
  - Range of age which is possible for mating and giving birth (restricting factors for two people with LCA too close to each other) (this is probably bell curve)
  - Rate of birth (probably binary search this)
- Steps:
  - Define all the classes
  - Define all the parameters needed (distribution and all that)
  - Simulate
- How to simulate
  - Define all parameters at first (look in Population.py)
  - Simulate each year
- How to simulate each year
    - Simulate deaths and births each year based on the number of births and deaths calculated
    - Q: How to simulate births tho
    - Have to have some way to have some data structures to pick parents for a child. So maybe maintain a couples dictionary (store the id for look up), a heap to store all people who are underaged, people who are of age but still singles (Probably store pair of age and id?). Well maybe everything stored should be id instead of a pointer to a Person object that's just not good. Also store a dictionary of all people with the key being id. Also probably should just make a separate file call Simulator.py. Population should only store basic information to initialize an information and it will call an instance of Simulator to simulate the population?