import random
lst = []
print(lst)
lst.append((0,0))
lst.append((0,1))
lst.append((0,2))
print(lst)
lst.append((0,0))
lst.append((0,1))
lst.append((0,2))
print(lst)
lst.remove((0,0))
print(lst)

pick = random.choice(lst)
lst.remove(pick)
print("Picked: ", pick)
print(lst)

