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