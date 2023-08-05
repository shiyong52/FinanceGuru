Meta_Category = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Other','Rent','Self-Improvement','Transportation','Travel']
record = {}
LIST = []
for i in Meta_Category:
    record['Meta Category'] = i
    record['Sum'] = 0
    record['Percentage'] = 0
    #print(record)
    LIST.append(record.copy())
print(LIST)
