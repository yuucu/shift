
import random
import itertools


class People:
  def __init__(self, shift, name):
    self.shift = shift
    self.name = name

  def __str__(self):
    return self.name


shift_d = ['d7', 'd8', 'd', 'd11', 'd12']
shift_u = ['u']
shift_f = ['f7', 'f8', 'f9', 'f10', 'f11', 'f12']
shift_m = ['m7', 'm8', 'm9', 'm10', 'm11', 'm13', 'm14']
shift_b = ['b7', 'b8']
shift_n = ['n1', 'n2']

all = shift_d + shift_u + shift_f + shift_m + shift_b + shift_n

peoples = []

for i in range(13):
  peoples.append(People(random.sample(all, 12), "people" + str(i)))


ds = set()
d8s = set()
d11s = set()

for p in peoples:
  if 'd8' in p.shift:
    d8s.add(p)
  if 'd' in p.shift:
    ds.add(p)
  if 'd11' in p.shift:
    d11s.add(p)


ds_comb = list(itertools.combinations(ds, 3))


for ds_three in ds_comb:
  for d8_one in d8s:
    if d8_one in ds_three:
      continue

    for d11_one in d11s:
      if d11_one in ds_three or d8_one == d11_one:
        continue
      for ds_one in ds_three:
        print(ds_one, end='')
        print("/", end='')

      print(d8_one, end='')
      print("/", end='')
      print(d11_one, end='')
      print()
