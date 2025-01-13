from sys import exit
from prettytable import PrettyTable
from sqlite3 import connect
import networkx as nx
database="bigdata.db"
conn=connect(database,isolation_level=None)
crsr=conn.cursor()
conn2=connect(database)
crsr2=conn2.cursor()
crsr2.execute('SAVEPOINT sp1;')
crsr.execute('''create table if not exists Bus 
             (name text,
             regno text primary key)''')
crsr.execute('''create table if not exists Bustable 
             (name text,
             regno text,
             arrivalPlace text,
             arrivalTime int,
             departurePlace text,
             departureTime int,
             primary key(regno,arrivalTime))''')
crsr.execute('''create table if not exists Route
             (placeA text,
             placeB text,
             distance int,
             primary key(placeA,placeB,distance))''')
crsr.execute('''create table if not exists places(
             place text primary key)''')
main={1:"Find buses",2:"Settings",3:"Clear data"}
second={1:"Routes",2:"Buses",3:"Palces",4:"Bustable"}
route={1:"View routes",2:"Add routes",3:"Delete routes"}
buses={1:"View buses",2:"Add buses",3:"Delete buses"}
busTable={1:"View bustable",2:"Add bustable",3:"Delete bustable"}
places={1:"View place",2:"Add places",3:"Delete places"}
placeTable={}

def refreshPlaces():
    global placeTable
    placeTable={}
    crsr.execute("Select * from places")
    details=crsr.fetchall()
    x=1
    for i in details:
        placeTable.update({x:i[0]})
        x+=1

def message():
    if crsr.rowcount==0:
        return "Update failed"
    conn.commit()
    return "Update successful"

def addBusSql(name,regno):
    try:
        crsr.execute('''insert into Bus values(?,?)''',(name,regno))
    except: return "Update failed"
    return message()

def addBusTableSql(name,regno,arrivalPlace,arrivalTime,departurePlace,departureTime):
    try:
        crsr.execute('''insert into Bustable values(?,?,?,?,?,?)''',(name,regno,arrivalPlace,arrivalTime,departurePlace,departureTime))
    except: return "Update failed"
    return message()

def addRouteSql(placea,placeb,distance):
    try:
        crsr.execute('''insert into Route values(?,?,?)''',(placea,placeb,distance))
    except: return "Update failed"
    return message()

def deleteRouteSql(placea,placeb,distance):
    try:
        crsr.execute('delete from Route where placeA=? and PlaceB=? and distance=?',(placea,placeb,distance))
    except:pass
    return message()

def deleteBuses(name,regno):
    try:
        crsr.execute('delete from Bus where name=? and regno=?',(name,regno))
    except:pass
    return message()

def deleteBusTableSql(name,regno,arrivalPlace,arrivalTime,departurePlace,departureTime):
    try:
        crsr.execute('delete from Bustable where name=? and regno=? and arrivalPlace=? and arrivalTime=? and departurePlace=? and departureTime=? ',(name,regno,arrivalPlace,arrivalTime,departurePlace,departureTime))
    except :pass
    return message()

def timeFormat(s):
    if s.isdigit():
        x=s
        y="00"
    else:
        x,y=s.split(":")
    if x.isdigit() and y.isdigit():
        if int(x)<24 and int(y)<60:
            return True
    return False

def timeConvert(s):
    if s.isdigit():
        h=s
        m="00"
    else:
        h,m=s.split(":")
    return int(h)*60+int(m) 

def timeConvertBack(n):
    n=int(n)
    h=(n//60)%24
    m=n%60
    if h==0:h="00"
    if m==0:m="00"
    if (n//60)//24>0:return f"1d:{h}:{m}"
    return f"{h}:{m}"

def addNumToList(details):
    i=1
    newlist=[]
    for x in details:
        newE=list(x)
        newE.insert(0,str(i)+".")
        newlist.append(newE)
        i+=1
    return newlist

def getInp():
    try:
        i=abs(int(input("Your choice : ")))
        if i=="": return getInp()
    except : 
        return getInp()
    else: return i

def quit():
    conn.close()
    conn2.close()
    exit()

def viewPlace():
    cnt=0
    refreshPlaces()
    for x in placeTable.keys():
        cnt+=1
        p=str(x)+"."+str(placeTable[x])
        print(f"{p:<15}",end="  ")
        if cnt==4:
            cnt=0
            print()


def addPlace():
    print("Places in the list")
    viewPlace()
    s=input("Enter new place name: ")
    if s in placeTable.values() :
        print("Cannot create duplicates!!!")
    else:
        crsr.execute('''Insert into places values(?)''',(s,))
        refreshPlaces()
        print("Updated successfully")

def deletePlace():
    print("Select from the places")
    viewPlace()
    ch=getInp()
    if ch not in placeTable.keys():
        print("Invalid Entry")
    else:
        crsr.execute('''delete from places where place=?''',(placeTable[ch],))
        refreshPlaces()
        print("Updated successfully")

def placeMenu():
    while True:
        print()
        print("Choose from the options below")
        print()
        for x in places:
            print(x,places[x])
        print("4 Back")
        print("5 Main menu")
        print("6 Quit")
        ch=getInp()
        if ch==1:
            viewPlace()
        elif ch==2:
            addPlace()
        elif ch==3:
            deletePlace()
        elif ch==4:
            secondMenu()
        elif ch==5:
            mainMenu()
        elif ch==6:
            quit()
        else :continue

bs=[]
def viewBus():
    crsr.execute('''Select * from Bus''')
    details=crsr.fetchall()
    if details==[]:return
    global bs
    bs=addNumToList(details)
    table=PrettyTable()
    table.field_names=["Sl. No.","Name","Reg. no."]
    table.add_rows(bs)
    print(table)

def addBus():
    viewBus()
    name=input("Enter Bus name : ")
    regno=input("Reg. no. : ")
    msg=addBusSql(name,regno)
    print(msg)

def deleteBus():
    while True:
        viewBus()
        n=getInp()
        if n<=len(bs):
            b=bs[n-1]
            print("This will delete all entries of this bus from bus table")
            print("Do you wish to continue? (Y/n)")
            while True:
                l=input()
                if l.isalpha():
                    l=l[0].lower()
                    break
            if l=="y":
                msg=deleteBuses(name=b[1],regno=b[2])
                crsr.execute('''delete from bustable where regno=?''',(b[2],))
                conn.commit()
                print(msg)
        else:print("Invalid Entry try again")

def busMenu():
    while True:
        print("Choose from the options below")
        print()
        for x in buses:
            print(x,buses[x])
        print("4 Back")
        print("5 Main menu")
        print("6 Quit")
        ch=getInp()
        if ch==1:
            viewBus()
        elif ch==2:
            addBus()
        elif ch==3:
            deleteBus()
        elif ch==4:
            secondMenu()
        elif ch==5:
            mainMenu()
        elif ch==6:
            quit()
        else :continue

rt=[]
def viewRoute():
    global rt
    crsr.execute('''select * from Route''')
    details=crsr.fetchall()
    if details==[]:return
    rt=addNumToList(details)
    table=PrettyTable()
    table.field_names=["Sl. No.","Place A","Place B","Distance"]
    table.add_rows(rt)
    print(table)

def addRoute():
    viewRoute()
    viewPlace()
    while True:
        print("Starting point : ")
        ch=getInp()
        if ch in placeTable.keys():
            placeA=placeTable[ch]
            break
        else:
            print("Invalid Entry") 
    while True:
        print("Ending point : ")
        ch=getInp()
        if ch in placeTable.keys():
            placeB=placeTable[ch]
            if placeA==placeB:
                print("Invalid Entry")
                continue
            print("Distance : ")
            distance=getInp()
            msg=addRouteSql(placeA,placeB,distance)
            print(msg)
            break
        else:
            print("Invalid Entry") 

def deleteRoute():
    while True:
        viewRoute()
        print("Enter the route you want to delete : ")
        ch=getInp()
        if ch<=len(rt):
            r=rt[ch-1]
            print("Warning : This will delete all entries of the route in the bus table")
            print("Do you wish to continue? (Y/n)")
            while True:
                l=input()
                if l.isalpha():
                    l=l[0].lower()
                    break
            if l=="y":
                msg=deleteRouteSql(placea=r[1],placeb=r[2],distance=r[3])
                crsr.execute('''delete from bustable where arrivalPlace=? and departurePlace=?''',(r[1],r[2]))
                conn.commit()
                print(msg)
                break
        else : print("Invalid Entry")

def routeMenu():
    while True:
        print("Choose from the options below")
        print()
        for x in route:
            print(x,route[x])
        print("4 Back")
        print("5 Main menu")
        print("6 Quit")
        ch=getInp()
        if ch==1:
            viewRoute()
        elif ch==2:
            addRoute()
        elif ch==3:
            deleteRoute()
        elif ch==4:
            secondMenu()
        elif ch==5:
            mainMenu()
        elif ch==6:
            quit()
        else :continue

lst=[]
def viewBusTable():
    crsr.execute("Select * from bustable")
    details=crsr.fetchall()
    if details==[]:return
    global lst
    lst=[]
    x=1
    for i in details:
        l=list(i)
        l.insert(0,x)
        l[4]=timeConvertBack(l[4])
        l[6]=timeConvertBack(l[6])
        lst.append(l)
        x+=1
    table=PrettyTable()
    table.field_names=["Sl. No.","Name","Reg. no.","Arrival","A-Time","Departure","D-Time"]
    table.add_rows(lst)
    print(table)

def addBusTable():
    viewBusTable()
    print()
    print("Enter the following details")
    while True:
        print()
        print("Choose the Bus")
        viewBus()
        n=getInp()
        global bs
        if n<=len(bs):
            b=bs[n-1]
            name=b[1]
            regno=b[2]
            break
        else:
            print("Invalid Entry")
    viewPlace()
    while True:
        print()
        print("Arrival place : ")
        arrivalPlace=getInp()
        if arrivalPlace in placeTable.keys():
            arrivalPlace=placeTable[arrivalPlace]
            break
        else:print("Choose valid input")
    while True:
        arrivalTime=input("Time in 24hr (HH:MM): ")
        if timeFormat(arrivalTime):
            arrivalTime=timeConvert(arrivalTime)
            break
        else: print("Incorrect format")
    while True:
        viewPlace()
        print()
        print("Departure place : ")
        departurePlace=getInp()
        if departurePlace in placeTable.keys():
            departurePlace=placeTable[departurePlace]
            if arrivalPlace==departurePlace:
                print("Arrival and departure cannot be same")
                continue
            break
        else:print("Choose valid input")
    while True:
        departureTime=input("Time in 24hr (HH:MM): ")
        if timeFormat(departureTime):
            departureTime=timeConvert(departureTime)
            break
        else: print("Incorrect format")
    msg=addBusTableSql(name,regno,arrivalPlace,arrivalTime,departurePlace,departureTime)
    print(msg)

def deleteBusTable():
    while True:
        viewBusTable()
        print("Enter the serial number you want to delete")
        n=getInp()
        if n<=len(lst):
            l=lst[n-1]
            msg=deleteBusTableSql(name=l[1],regno=l[2],arrivalPlace=l[3],arrivalTime=timeConvert(l[4]),departurePlace=l[5],departureTime=timeConvert(l[6]))
            print(msg)
            return
        else:
            print("Invalid Entry try again")

def bustableMenu():
    while True:
        print("Choose from the options below")
        print()
        for x in busTable:
            print(x,busTable[x])
        print("4 Back")
        print("5 Main menu")
        print("6 Quit")
        ch=getInp()
        if ch==1:
            viewBusTable()
        elif ch==2:
            addBusTable()
        elif ch==3:
            deleteBusTable()
        elif ch==4:
            secondMenu()
        elif ch==5:
            mainMenu()
        elif ch==6:
            quit()
        else :continue

def secondMenu():
    while True:
        print("Choose from the options below")
        print()
        for x in second:
            print(x,second[x])
        print("5 Back")
        print("6 Quit")
        choice=getInp()
        if choice==1:
            routeMenu()
        elif choice==2:
            busMenu()
        elif choice==3:
            placeMenu()
        elif choice==4:
            bustableMenu()
        elif choice==5:
            mainMenu()
        elif choice==6:
            quit()
        else :
            continue

g=nx.Graph()
def createGraph():
    global g
    g=nx.Graph()
    node=list(placeTable.values())
    g.add_nodes_from(node)
    crsr.execute("select * from route")
    details=crsr.fetchall()
    for i in details:
        g.add_edge(i[0],i[1],weight=int(i[2]))
    

def pathLength(graph, path): 
    length = 0 
    for i in range(len(path) - 1):
        length += graph[path[i]][path[i + 1]]['weight'] 
    return length

def calcAllPath(start,end):
    createGraph()
    global g
    pathList=[]
    allPath=list(nx.all_simple_paths(g,source=placeTable[start],target=placeTable[end]))
    for path in allPath:    
        length=pathLength(g,path)
        temp=list(path)
        temp.append(length)
        pathList.append(temp)
    sorted_data = sorted(pathList, key=lambda x: x[-1])
    sorted_data=addNumToList(sorted_data)
    return sorted_data

def choosePath(start,end,arrivalTime):
    pathList=calcAllPath(start,end)
    print("Choose a Path")
    for path in pathList:
        length=path[-1]
        print(path[0],end="")
        for x in path[1:-2]:
            print(x,end="->")
        print(path[-2])
        print("Distance = ",length/1000,"Km")
        print()
    while True:
        ch=getInp()
        if ch<=len(pathList):
            ch=pathList[ch-1][1:-1]
            break
        else: print("Try again")
    showBuses(ch,arrivalTime)

class BusPath():
    def __init__(self,path):
        self.path=[list(x) for x in path]
        self.totalTime=0
    def set(self):
        self.totalTime=self.path[-1][5]-self.path[0][3]
        if len(self.path)!=1:
            cnt=0
            i=0
            while i<len(self.path)-1:
                if cnt==1:
                    i-=1
                    cnt=0
                if self.path[i][1]==self.path[i+1][1]:
                    self.path[i+1][2]=self.path[i][2]
                    self.path[i+1][3]=self.path[i][3]
                    self.path.pop(i)
                    cnt=1
                i+=1
        for i in self.path:
            i[3]=timeConvertBack(i[3])
            i[5]=timeConvertBack(i[5])

def printFinalTable(bpList):
    bpList_sorted=sorted(bpList, key=lambda obj: obj.totalTime)
    cnt=0
    for p in bpList_sorted:
        table=PrettyTable()
        table.field_names=["Bus name","Reg. no.","Arrival","A-Time","Departure ","D-Time"]
        table.max_width=20
        table.add_rows(p.path)
        print(table)
        print("Estimated Time : ",timeConvertBack(p.totalTime),"h")
        print()
        cnt+=1
        if cnt==2 and len(p)>2:
            cnt=0
            print("Load more ? (Y/n)")
            while True:
                l=input()
                if l.isalpha():
                    l=l[0].lower()
                    break
            if l=="y":continue
            else:break

def pathMaker(x,path):
    if len(path)==1: return []
    arrivalTime=x[5]
    arrivalPlace=x[4]
    newPaths=[]
    crsr2.execute("""update bustable set arrivalTime=arrivalTime+1440,departureTime=departureTime+1440 where arrivalTime<? and arrivalPlace=?""",(arrivalTime,arrivalPlace))
    crsr2.execute("""update bustable set departureTime=departureTime+1440 where departureTime<? and arrivalPlace=?""",(arrivalTime,arrivalPlace))
    crsr2.execute("Select * from bustable where arrivalPlace=? and arrivalTime>=?",(arrivalPlace,arrivalTime))
    details=crsr2.fetchall()
    crsr2.execute("rollback to sp1;")
    if details==[]:return []
    for i in details:
        if i[4] in path[1:]:
            newPath=[]
            index=path.index(i[4])
            rpath=path[index:]
            newPath.append(i)
            pm=pathMaker(i,rpath)
            if pm==[] :
                newPaths.append(list(newPath))
            else:
                for p in pm:
                    temp=newPath[:]
                    temp+=p
                    newPaths.append(temp)
    return newPaths

def get_keys_from_value(d, value): 
    keys = [key for key, val in d.items() if val == value] 
    return keys

def showBuses(path,arrivalTime):
    h=nx.Graph()
    h.add_nodes_from(path)
    pathListFull=[]
    endPath=path[1:]
    crsr.execute("Select * from bustable where arrivalPlace=? and arrivalTime>=?",(path[0],arrivalTime))
    details1=crsr.fetchall()
    if details1!=[]:
        crsr2.execute("""update bustable set arrivalTime=arrivalTime+1440,departureTime=departureTime+1440 where arrivalTime<? and arrivalPlace=?""",(arrivalTime,path[0]))
        crsr2.execute("""update bustable set departureTime=departureTime+1440 where departureTime<? and arrivalPlace=?""",(arrivalTime,path[0]))
        crsr2.execute("Select * from bustable where arrivalPlace=? and arrivalTime>=?",(path[0],arrivalTime))
        details=crsr2.fetchall()
        crsr2.execute("rollback to sp1;")
        for x in details:
            if x[4] in endPath:
                pathList=[]
                index=path.index(x[4])
                rpath=path[index:]
                pathList.append(x)
                pm=pathMaker(x,rpath)
                if pm ==[]:
                    pathListFull.append(pathList)
                else:
                    for p in pm:
                        temp=pathList[:]
                        temp+=p
                        pathListFull.append(temp)
    bpList=[]
    for i in pathListFull:
        bp=BusPath(i)
        bp.set()
        bpList.append(bp)
        for j in i:
            h.add_edge(j[2],j[4],weight=j[5]-j[3],name=f"{j[0]}:{j[1]}")
    if nx.is_connected(h)==False :
        print("No complete bus routes, choose a different path")
        print("Do you wish to continue? (Y/n)")
        while True:
            l=input()
            if l.isalpha():
                l=l[0].lower()
                break
        print()
        if l!="y":mainMenu()
        start=get_keys_from_value(placeTable,path[0])
        end=get_keys_from_value(placeTable,path[-1])
        choosePath(start[0],end[0],arrivalTime)
        return
    printFinalTable(bpList)

def findBus():
    while True:
        print("Places available ")
        viewPlace()
        print()
        print("Choose starting the place : ",end="")
        start=getInp()
        if start not in placeTable.keys():
            print("Invalid input")
            continue
        else:
            print("Enter drop point : ",end="")
            end=getInp()
            if end not in placeTable.keys() or end==start:
                print("Invalid input")
                continue
            else:
                while True:
                    arrivalTime=input("Time in 24hr (HH:MM): ")
                    if timeFormat(arrivalTime):
                        arrivalTime=timeConvert(arrivalTime)
                        break
                    else: 
                        print("Incorrect format")
            print()
            choosePath(start,end,arrivalTime)
            break

def mainMenu():
    print("Hello there!! Welcome")
    while True:
        print()
        for x in main:
            print(x,main[x])
        print("4 Quit")
        choice=getInp()
        print()
        if choice==1:
            findBus()
        elif choice==2:
            secondMenu()
        elif choice==3:
            print("Are you sure? (Y/n)")
            while True:
                l=input()
                if l.isalpha():
                    l=l[0].lower()
                    break
            if l=="y":
                crsr.execute("drop table bus")
                crsr.execute("drop table bustable")
                crsr.execute("drop table places")
                crsr.execute("drop table route")
                print("Data cleared")
        elif choice==4:
            quit()
        else:
            continue
try:
    mainMenu()
except:pass
