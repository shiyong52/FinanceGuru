Meta_Category = [' Birthday Gift', 'Business Expense', 'Charity', 'Entertainment','Food','Materialistic Desires','Medical','Other','Rent','Self-Improvement','Transportation','Travel']
record = {}
LIST = []
total = 0 
for i in Meta_Category:
    record['Meta Category'] = i
    SUM = db.execute("SELECT SUM(expenses) FROM Expenses WHERE id = ? AND Date LIKE ? AND MetaC = ?", session["user_id"],search,i)
    SUM = SUM[0]['SUM(expenses)']
    if SUM == None:
        SUM = 0
    total += SUM
    record['Sum'] = SUM
    record['Percentage'] = 0
    LIST.append(record.copy())
