import numpy as np
import itertools
from tqdm import tqdm

dataset_file = open("levithan_data.txt","r")
data = dataset_file.readlines()

dataset = []
for i in data:
  dataset.append(i.split(' -1 ')[:-1])

dataset = dataset[:1000]

temp_data =[]
for i in dataset:
    temp_data.append(list(set(i)))
dataset = temp_data

unique_items = []
for i in dataset:
  unique_items.extend(list(set(i)))
  unique_items = list(set(unique_items))

temp=[]
for i in unique_items:
  temp.append({i})
unique_items =temp


# Implementing default Apriori algorithm

def AprioriGen(F):
  # print(F)
  new_candidates=[]
  
  for k in range(len(F)-1):
    for l in range(k+1,len(F)):
      i=F[k]
      j=F[l]
      if len(set(i).difference(set(j))) == 1 and len(set(j).difference(set(i))) == 1:
        flag=True
        prospet = set(i).union(set(j))
        prospet_subsets = list(itertools.combinations(prospet,len(prospet)-1))
        temp = []
        for i in prospet_subsets:
          temp.append(set(i))
        prospet_subsets = temp
        # print(prospet_subsets)
        for i in prospet_subsets:
          if i not in F:
            flag=False
        
        if flag:
          new_candidates.append(prospet)
  return new_candidates

def Apriori(candidates,dataset, min_support):
  dataset_size = len(dataset)
  result={}
  while (candidates!=None and len(candidates)>0):
    candidate_counts = {}
    for i in candidates:
      temp = list(i)
      temp.sort()
      candidate_counts["-".join(temp)]=0
    for i in tqdm(dataset):
      for j in candidates:
        if j.issubset(set(i)):
          temp = list(j)
          temp.sort()
          candidate_counts["-".join(temp)]+=1
    frequent_candidates = []
    for f in candidate_counts:
      if candidate_counts[f]>= min_support * dataset_size:
        frequent_candidates.append([set(f.split("-")),candidate_counts[f]])

    if frequent_candidates!=[]:
      candidates = AprioriGen(list(np.array(frequent_candidates)[:,0]))
    else:
      break
    for i in frequent_candidates:
      if len(i[0])==1:
        continue
      subsets = list(itertools.combinations(i[0],len(i[0])-1))
      for j in subsets:
        try:
          if result["-".join(list(j))] == i[1]:
            result.pop("-".join(list(j)))
        except:
          pass
    
    for i in frequent_candidates:
      result["-".join(list(i[0]))] = i[1]
  return result

min_support = 0.5
candidates = unique_items

# Default Apriori
x = Apriori(candidates,dataset,min_support)
print("\n***************\n")
print("APRIORI ALGORITHM")
print("\n***************\n")
print(x)
print("\nLength: ", len(x))

# Implementing Hashing optimization for Apriori

def HashTechnique(single_itemset, dataset, min_support):
  hash_table ={}
  hash_count ={}
  for i in tqdm(dataset):
    for j in list(itertools.combinations(set(i),2)):
      hash = (int(j[0])+int(j[1]))%10
      if hash not in hash_table.keys():
        hash_table[hash]=set(tuple(set(j)))
        hash_count[hash]=1
      else:
        hash_table[hash].add(tuple(set(j)))
        hash_count[hash]+=1
  
  # print(len(hash_table[6]))
  # print({'8', '18'} in hash_table[6])
  # print(hash_table[6])
  possible_candidates = []
  for i in hash_table.keys():
    if hash_count[i]>= min_support *len(dataset):
      possible_candidates.extend([set(x) for x in hash_table[i]])
#   print(possible_candidates)
  # print({'8', '18'} in possible_candidates)
  # res = []
  # for i in tqdm(possible_candidates):
  #     if i not in res:
  #         res.append(i)
  return possible_candidates

# Implementing partitioning optimization for Apriori

def partition(min_support, dataset, num_part, hash=True):
  dataset_size = len(dataset)
  part_size = len(dataset)//num_part
  total_result = {}
  result_counts = {}
  for i in range(num_part):
    datapart = dataset[i*part_size:(i+1)*part_size]

    unique_items = []
    for j in datapart:
      unique_items.extend(list(set(j)))
      unique_items = list(set(unique_items))

    single_frequent_itemset = []
    temp=[]
    for j in unique_items:
      temp.append({j})
    unique_items =temp
    # candidates = unique_items
    candidates=[]
    if not hash:
      candidates = unique_items
    else:
      candidates = HashTechnique(unique_items,datapart,min_support)
      candidate_counts = {}
      for i in unique_items:
        candidate_counts["-".join(list(i))]=0;

      for i in tqdm(dataset):
        for j in unique_items:
          if j.issubset(set(i)):
            candidate_counts["-".join(list(j))]+=1

      for f in candidate_counts:
        if candidate_counts[f]>= min_support * dataset_size:
          single_frequent_itemset.append([set(f.split("-")),candidate_counts[f]])
    # if {'8','18'} in candidates:
    #   print('found')
    # print(candidates[:10])
    part_result = Apriori(candidates, datapart, min_support)
    total_result.update(part_result)

#   print(total_result)
  for i in total_result:
    result_counts[i]=0;
#   print("res counts: ", result_counts)
  for i in tqdm(dataset):
    k = []
    for j in total_result:
      k = set(j.split("-"))
      if k.issubset(set(i)):
        result_counts[j]+=1

  frequent_candidates = single_frequent_itemset
  for f in result_counts:
    if result_counts[f]>= min_support * dataset_size:
      frequent_candidates.append([set(f.split("-")),result_counts[f]])

  return frequent_candidates

def closed_frequent(freq):
  closed=[]
  temp ={}
  for i in freq:
    if i[1] not in temp:
      temp[i[1]] = []
    temp[i[1]].append(i[0])

  flag = True
  for i in temp:
    for j in temp[i]:
      flag=True
      for k in temp[i]:
        if j==k:
          continue
        if j.issubset(k):
          flag =False
      if flag:
        closed.append([j,i])
  return closed


print("CLOSED FREQUENT FOR BASE ALGORITHM")
y = []
for k in x.keys():
    y.append([set(k.split('-')),x[k]])
y = closed_frequent(y)
print(y)
print("\nLength: ", len(y))

# Parition Apriori
x = partition(0.5, dataset, 4, False)
print("\n***************\n")
print("PARTITION OPTIMIZATION")
print("\n***************\n")
print(x)
print("\nLength: ", len(x))

# Hash Apriori
partition(0.5, dataset, 1, True)
print("\n***************\n")
print("HASH OPTIMIZATION")
print("\n***************\n")
print(x)
print("\nLength: ", len(x))

# Hash Apriori with Partitioning
partition(0.5, dataset, 4, True)
print("\n***************\n")
print("HASH OPTIMIZATION")
print("\n***************\n")
print(x)
print("\nLength: ", len(x))