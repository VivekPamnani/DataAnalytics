global item_freqs
from tqdm import tqdm
class FP_node:
    def __init__(self, value, parent_ptr, count):
        self.value = value
        self.count = count
        self.children = []
        self.parent_ptr = parent_ptr
        self.original_count = self.count


class FP_Tree:
    def __init__(self):
        self.header_table = {}
        self.item_freqs = {}
        self.root = FP_node(None, None,0)

    def insert(self,transaction, count=1):
        root = self.root
        for item in transaction:
            if item not in self.item_freqs:
                self.item_freqs[item] = 0
            self.item_freqs[item]+=count
            
            flag=True
            for i in root.children:
                if item == i.value:
                    root = i
                    root.count +=count
                    flag = False
                    break
            
            if flag:
                if item not in self.header_table:
                    self.header_table[item] = []
                newNode = FP_node(item, root, count)
                root.children.append(newNode)
                self.header_table[item].append(newNode)
                root =  newNode

    def mine(self, minsup, alpha):

        if len(self.root.children)==0:
            return []
        
        frequent_itemsets = []
        self.item_freqs = dict(sorted(self.item_freqs.items(), key=lambda x: list(item_freqs.keys()).index(x[0])))
        for key in self.item_freqs:
            if minsup>self.item_freqs[key]:
                continue
            # print(alpha, key)
            condition_base_fp = FP_Tree()
            frequent_itemsets.extend([alpha+[key],self.item_freqs[key]])
            for node in self.header_table[key]:
                cur_node = node
                prefix_path = []
                while cur_node.value !=None:
                    cur_node = cur_node.parent_ptr
                    prefix_path.append(cur_node.value)
                prefix_path = prefix_path[:-1]
                prefix_path.reverse()
                
                # print(prefix_path)
                condition_base_fp.insert(prefix_path,node.count)
            frequent_itemsets+=condition_base_fp.mine(minsup, alpha+[key])
        
        return frequent_itemsets


class FP_Tree_merge:
    def __init__(self):
        self.header_table = {}
        self.conditional_trees = {}
        self.root = FP_node(None, None,0)
        self.item_freqs = {}

    
    
    def delete(self, transaction, count=1):
        root= self.root
        for item in transaction:
            for i in root.children:
                if item == i.value:
                    root = i
                    break
        
        temp = transaction.copy()
        while root.value is not None:
            par = root.parent_ptr
            if count < root.count:
                root.count -=count
            else:
                if root.value not in self.conditional_trees:
                    self.conditional_trees[root.value] = FP_Tree_merge()
                    temp = temp[:-1]
                    self.conditional_trees[root.value].insert(temp, root.original_count)

                else:
                    temp = temp[:-1]
                    self.conditional_trees[root.value].insert(temp, root.original_count)
                root.parent_ptr.children.remove(root)
                self.header_table[root.value].remove(root)
                del root
            root = par

    def insert(self,transaction, count=1):
        root = self.root
        for item in transaction:
            if item not in self.item_freqs:
                self.item_freqs[item] = 0
            self.item_freqs[item]+=count
            
            flag=True
            for i in root.children:
                if item == i.value:
                    root = i
                    root.count +=count
                    root.original_count = root.count
                    flag = False
                    break
            
            if flag:
                if item not in self.header_table:
                    self.header_table[item] = []
                newNode = FP_node(item, root, count)
                self.header_table[item].append(newNode)
                root.children.append(newNode)
                root =  newNode

    def mine(self, minsup, alpha):
        frequent_itemsets = []

        if len(self.root.children)==0:
            return []
        
        self.item_freqs = dict(sorted(self.item_freqs.items(), key=lambda x: list(item_freqs.keys()).index(x[0])))
        for key in self.item_freqs:
            if minsup>self.item_freqs[key]:
                continue
            frequent_itemsets.extend([alpha+[key],self.item_freqs[key]])
            if key not in self.conditional_trees:
                self.conditional_trees[key] = FP_Tree_merge()

            for node in self.header_table[key].copy():
                cur_node = node
                prefix_path = []
                while cur_node.value !=None:
                    cur_node = cur_node.parent_ptr
                    prefix_path.append(cur_node.value)
                prefix_path = prefix_path[:-1]
                prefix_path.insert(0,key)
                prefix_path.reverse()

                self.delete(prefix_path,node.count)
            frequent_itemsets+=self.conditional_trees[key].mine(minsup, alpha+[key])
        
        return frequent_itemsets



dataset_file = open("data.txt","r")
data = dataset_file.readlines()
dataset = []
for i in data:
  dataset.append(i.split(' -1 ')[:-1])
temp_data =[]
for i in dataset:
    temp_data.append(list(set(i)))
dataset = temp_data
# dataset = dataset[:500]

item_freqs = {}
for i in dataset:
    for j in i:
        if j not in item_freqs:
            item_freqs[j]=1
        else:
            item_freqs[j]+=1

item_freqs = dict(sorted(item_freqs.items(), key=lambda x: x[1]))
# print(item_freqs)

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


tree = FP_Tree()

minsup = 0.5
for i in tqdm(range(len(dataset))):
    tree.insert(sorted(dataset[i], key=lambda x: [item_freqs[x], list(item_freqs.keys()).index(x)], reverse=True))

result = tree.mine(minsup*len(dataset),[])
temp = []
i=0
while i <len(result):
    temp.append([set(result[i]),result[i+1]])
    i+=2

result  = closed_frequent(temp)

print("\n***************\n")
print("BASIC FPG")
print("\n***************\n")
print("frequent itemset",temp)
print("\nLength: ", len(temp))
print()
print("closed frequent itemset",result)
print("\nLength: ", len(result))


print("using optimization")
tree1 = FP_Tree_merge()

for i in tqdm(range(len(dataset))):
    tree1.insert(sorted(dataset[i], key=lambda x: [item_freqs[x], list(item_freqs.keys()).index(x)], reverse=True))


result1 = tree1.mine(minsup*len(dataset),[])

temp = []
i=0
while i <len(result1):
    temp.append([set(result1[i]),result1[i+1]])
    i+=2

result  = closed_frequent(temp)

print("\n***************\n")
print("MERGING STRATEGY")
print("\n***************\n")
print("frequent itemset",temp)
print("\nLength: ", len(temp))
print()
print("closed frequent itemset",result)
print("\nLength: ", len(result))


