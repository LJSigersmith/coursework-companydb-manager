from prettytable import PrettyTable
import mysql.connector
import os
import sys

## ====================== README =======================
## = Configure MySQL Database Login under MySQL Config =
##                                                     =
## = Dependencies:                                     =
##                                                     =
## = - PrettyTable                                     =
## =    - https://pypi.org/project/prettytable/        =
## =    - python -m pip install -U prettytable         =
##                                                     =
## = - MySQL Connector                                 =
## =====================================================

## ================ MySQL Config ===========
db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="project1"
)
## ================ Globals ================ 
employee = {
    1 : "First Name",
    2 : "Middle Initial",
    3 : "Last Name",
    4 : "SSN",
    5 : "Birthdate",
    6 : "Address",
    7 : "Sex",
    8 : "Salary",
    9 : "Supervisor SSN",
    10 :" Department Number"
}

departmentLocation = {
    1 : "Department Number",
    2 : "Department Location"
}

dependent = {
    1 : "Employee SSN",
    2 : "Dependent Name",
    3 : "Sex",
    4 : "Birthdate",
    5 : "Relationship"
}

department = {
    1 : "Department Name",
    2 : "Department Number",
    3 : "Manager SSN",
    4 : "Manager Start Date"
}

employeeFields = {
    1 : "Fname",
    2 : "Minit", 
    3 : "Lname",
    4 : "Ssn",
    5 : "Bdate", 
    6 : "Address",
    7 : "Sex", 
    8 : "Salary", 
    9 : "Super_ssn",
    10: "Dno"
}

## ================ MySQL ================ 

## Execute query, not used for SELECT Queries
def executeQuery(query, values=None) :
    cursor = db.cursor()
    if (values) :
        cursor.execute(query,values)
    else :
        cursor.execute(query)
    db.commit()

## Execute queries that are returning results
## Display the results in a nice table
def returnQuery(query, fields) :
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    display = PrettyTable()
    display.field_names = fields
    
    for x in result :
        rowList = list()
        for y in x :
            rowList.append(y)
        display.add_row(rowList)
    
    if (len(display.rows) == 0) : print(bcolors.WARNING + "No records" + bcolors.ENDC)
    else : print(display)

## Execute queries, catch any errors
## Set opt to 1 if the query will be returning values and needs to be displayed
def handleQueryError(query, values=None, opt=0) :
    try :
        if opt == 0 :
            if values :
                executeQuery(query, values)
            else :
                executeQuery(query)
        else :
            returnQuery(query,values)
        return False
    except mysql.connector.DataError as e :
        os.system('clear')
        print(bcolors.BOLD + "Wrong Data Type" + bcolors.ENDC)
        print(e)
        return True
    except mysql.connector.IntegrityError as e :
        os.system('clear')
        print(bcolors.BOLD + "Integrity Constraint Violation" + bcolors.ENDC)
        print(e)
        return True
    except mysql.connector.errors.ProgrammingError as e :
        os.system('clear')
        print(bcolors.BOLD + "Invalid Input For Field(s)" + bcolors.ENDC)
        print(e)
        return True
    except mysql.connector.Error as e :
        os.system('clear')
        print(bcolors.BOLD + "MySQL Error" + bcolors.ENDC)
        print(e)
        return True

## Lock table or tables, set rw to READ to lock as READ
def lockTable(tables, rw="WRITE") :
    if (len(tables) == 1) :
        query = "LOCK TABLES " + tables[0] + " " + rw
    else :
        query = "LOCK TABLES "
        for t in range(len(tables)) :
            query += str(tables[t]) + " " + rw
            if t != (len(tables) - 1) :
                query += ","
    executeQuery(query)

## Unlock tables
def unlockTables() :
    query = "UNLOCK TABLES"
    executeQuery(query)

##  == Check for Foreign Key Violations ==

def getTablesReferencedForKey(key,value) :

    cursor = db.cursor()

    cursor.execute("select database()")
    db_name = cursor.fetchone()[0]

    unlockTables()
    query = "SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '%s' AND REFERENCED_COLUMN_NAME = '%s'" % (db_name, key)

    cursor.execute(query)
    result = cursor.fetchall()

    constraints = list()

    for x in result : 
        table_name = x[0]
        column_name = x[1]
        row = {
            "table": table_name,
            "column": column_name
        }
        constraints.append(row)
    
    ## Constraints: [(table: "", row: "")]

    constraint_violations = dict()
    field_names = dict()

    for x in constraints :
        q = "SELECT * FROM %s WHERE %s='%s'" % (x["table"], x["column"], value)
        cursor.execute(q)

        result = cursor.fetchall()
        ## Constraint_violations[table] = ()
        constraint_violations[x["table"]] = list()
        for y in result :
            ## Constraint_violations[table] = (..., y, ...)
            constraint_violations[x["table"]].append(y)
        
        fieldQuery = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='%s'" % (x["table"])
        cursor.execute(fieldQuery)
        field_result = cursor.fetchall()
        _field_names = list()
        for i in field_result :
            _field_names.append(str(i[0]))
        
        field_names[x["table"]] = _field_names

    for x in constraint_violations.keys() :
        _table_name = x
        display = PrettyTable()
        display.field_names = field_names[_table_name]

        rowList = constraint_violations[_table_name]
        display.add_rows(rowList)
        
        if (len(display.rows) > 0) :
            print(bcolors.UNDERLINE + bcolors.WARNING + "Warning" + bcolors.ENDC)
            print(bcolors.BOLD + bcolors.WARNING + "The following records will be deleted" + bcolors.ENDC)
            print(bcolors.HEADER + "\nTable: " + str(_table_name).upper() + bcolors.ENDC)
            print(display)

## ================ Formatting ================ 

def clear() :
    os.system('clear')

def stringToBorder(line, totalSz) :
    size = totalSz - len(line)
    return (" " * size) + "*"

def printBorder(sz) :
    print("*" * sz)

def getHeader(_header) :
    header = (bcolors.BOLD + _header + bcolors.ENDC)
    header = ("*" * len(_header)) + "\n" + header +"\n" + ("*" * len(_header))
    return header

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

## ================ Display Headers ================

def employeeHeader(values=None) :
    row = PrettyTable()
    row.field_names = employee.values()
    if (values is None) :
        row.add_row(["","","","","","","","","",""])
    else :
        rowList = list()
        for v in values :
            rowList.append(v)
        for i in range(len(rowList), 10) :
            rowList.append("")
        row.add_row(rowList)
    return row

def departmentLocationHeader(values=None) :
    row = PrettyTable()
    row.field_names = departmentLocation.values()
    if (values is None) :
        row.add_row(["",""])
    else :
        rowList = list()
        for v in values :
            rowList.append(v)
        for i in range(len(rowList), 2) :
            rowList.append("")
        row.add_row(rowList)
    return row

def dependentHeader(values=None) :
    row = PrettyTable()
    row.field_names = dependent.values()
    if (values is None) :
        row.add_row(["","","","",""])
    else :
        rowList = list()
        for v in values :
            rowList.append(v)
        for i in range(len(rowList), 5) :
            rowList.append("")
        row.add_row(rowList)
    return row

def departmentHeader(values=None) :
    row = PrettyTable()
    row.field_names = department.values()
    if (values is None) :
        row.add_row(["","","",""])
    else :
        rowList = list()
        for v in values :
            rowList.append(v)
        for i in range(len(rowList), 4) :
            rowList.append("")
        row.add_row(rowList)
    return row

## =============== Helpers ============
## For updating display so it remains a continuous display
def processInput(inputName, values, header, headerFunction) :
    values.append(inputName)
    os.system('clear')
    print(header)
    print(headerFunction(values))

## ================ Add ================
def addEmployee() :
    not_commit = True

    while (not_commit) :
        _header = "* Add Employee *"
        header = getHeader(_header)
        print(header)

        values = list()
        print(employeeHeader())

        try :
            fname = input("First Name: ")
            processInput(fname, values, header, employeeHeader)

            minit = input("Middle Initial: ")
            processInput(minit, values, header, employeeHeader)

            lname = input("Last Name: ")
            processInput(lname, values, header, employeeHeader)

            ssn = input("SSN: ")
            processInput(ssn, values, header, employeeHeader)

            bdate = input("Birthdate (yyyy-mm-dd): ")
            processInput(bdate, values, header, employeeHeader)

            address = input("Address: ")
            processInput(address, values, header, employeeHeader)

            sex = input("Sex (M/F): ")
            processInput(sex, values, header, employeeHeader)

            salary = input("Salary: $")
            processInput(salary, values, header, employeeHeader)

            superssn = input("Supervisor SSN: ")
            processInput(superssn, values, header, employeeHeader)

            dno = input("Department Number: ")
            processInput(dno, values, header, employeeHeader)
    
        except (EOFError, KeyboardInterrupt) :
            return

        confirm = input("Commit New Employee (Y/N): ")
        
        query = "INSERT INTO EMPLOYEE VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (fname, minit, lname, ssn, bdate, address, sex, salary, superssn, dno)
        
        not_commit = handleQueryError(query, values)

def addDepartmentLocation() :
    not_commit = True

    while (not_commit) :

        _header = "* Add Department Location *"
        header = getHeader(_header)
        print(header)

        values = list()
        print(departmentLocationHeader())

        try :
            dnumber = input("Department Number: ")
            processInput(dnumber, values, header, departmentLocationHeader)
        except (KeyboardInterrupt, EOFError) :
            return
        
        lockTable(("DEPARTMENT", "DEPT_LOCATIONS"))

        viewDepartment(dnumber,0)

        try :

            dlocation = input("Department Location: ")
            processInput(dlocation, values, header, departmentLocationHeader)
        
        except (EOFError, KeyboardInterrupt) :
            return

        confirm = input("Commit New Department Location (Y/N): ")
        
        query = "INSERT INTO DEPT_LOCATIONS VALUES (%s, %s)"
        values = (dnumber, dlocation)
        
        not_commit = handleQueryError(query, values)
        unlockTables()

def addDependent() :
    not_commit = True

    while not_commit :
        
        _header = "* Add Dependent *"
        header = getHeader(_header)
        print(header)

        values = list()

        try :
            essn = input("Employee SSN: ")
            processInput(essn, values, header, dependentHeader)
        
        except (EOFError, KeyboardInterrupt) :
            return
        
        os.system('clear')
        print(bcolors.OKGREEN + "Existing Dependents" + bcolors.ENDC)
        viewDependents(essn)
        tables = list()
        tables.append("DEPENDENT")
        lockTable(tables)
        print(getHeader(_header))
        print(dependentHeader())
        try :
            dependentname = input("Dependent Name: ")
            processInput(dependentname, values, header, dependentHeader)

            sex = input("Sex (M/F): ")
            processInput(sex, values, header, dependentHeader)

            bdate = input("Birthdate (YYYY-MM-DD): ")
            processInput(bdate, values, header, dependentHeader)

            relationship = input("Relationship: ")
            processInput(relationship, values, header, dependentHeader)

        except (EOFError, KeyboardInterrupt) :
            return

        confirm = input("Commit New Dependent (Y/N): ")

        query = "INSERT INTO DEPENDENT VALUES ('%s', '%s', '%s', '%s', '%s')" % (essn, dependentname, sex, bdate, relationship)
        not_commit = handleQueryError(query, None)
        unlockTables()

def addDepartment() :

    not_commit = True
    while not_commit :
        
        _header = "* Add Department *"
        header = getHeader(_header)
        print(header)
        
        values = list()
        print(departmentHeader())

        try :
            dname = input("Department Name: ")
            processInput(dname, values, header, departmentHeader)
            
            dnumber = input("Department Number: ")
            processInput(dnumber, values, header, departmentHeader)

            mgrssn = input("Manager SSN: ")
            processInput(mgrssn, values, header, departmentHeader)

            mgrstartdate = input("Manager Start Date (YYYY-MM-DD): ")
            processInput(mgrstartdate, values, header, departmentHeader)

        except (KeyboardInterrupt, EOFError) :
            return

        confirm = input("Commit New Department (Y/N): ")
        query = "INSERT INTO DEPARTMENT VALUES (%s,%s,%s,%s)"
        values = (dname,dnumber,mgrssn,mgrstartdate)

        not_commit = handleQueryError(query, values)

## ================ View ================ 

# viewEmployee / viewDepartment :
# If main is 1, then view is being called from a menu, not a function, so pause to allow user to see the result
def viewEmployee(ssn=None, main=0) :
    if (ssn is None) :
        
        _header = "* View Employee *"
        print(getHeader(_header))

        try :
            ssn = input("SSN: ")
            if (ssn == "") : return
        except (KeyboardInterrupt, EOFError) :
            return

    query = "SELECT * FROM EMPLOYEE WHERE Ssn=%s" % (ssn)

    handleQueryError(query, employee.values(), 1)
    
    if (main == 1) :
        try :
            input("...")
            return
        except (EOFError, KeyboardInterrupt) :
            return
    return

def viewDepartment(dno=None, main=0) :

    if dno is None :
        _header = "* View Department *"
        print(getHeader(_header))

        try :
            dno = input("Department Number: ")
        except(KeyboardInterrupt, EOFError) :
            return
    
    query = "SELECT * FROM DEPARTMENT WHERE Dnumber=%s" % (dno)

    handleQueryError(query, department.values(), 1)

    if (main == 1) :
        try :
            input("...")
            return
        except (EOFError, KeyboardInterrupt) :
            return
    return

def viewDependents(essn) :
    query = "SELECT * FROM DEPENDENT WHERE Essn=%s" % (essn)
    handleQueryError(query, dependent.values(), 1)

def viewDependent(essn, fname) :
    query = "SELECT * FROM DEPENDENT WHERE Essn=%s AND Dependent_name='%s'" % (essn, fname)
    handleQueryError(query, dependent.values(),1)

def viewDepartmentLocations(dno) :
    query = "SELECT * FROM DEPT_LOCATIONS WHERE Dnumber='%s'" % (dno)
    handleQueryError(query, departmentLocation.values(),1)

def viewDepartmentLocation(dno, location=None) :
    if location is None :
        query = "SELECT * FROM DEPT_LOCATIONS WHERE Dnumber='%s'" % (dno)
    else :
        query = "SELECT * FROM DEPT_LOCATIONS WHERE Dnumber='%s' AND Dlocation='%s'" % (dno, location)
    handleQueryError(query, departmentLocation.values(),1)
## ================ Modify ================  

def modifyEmployee() :
    
    _header = "* Modify Employee *"
    print(getHeader(_header))

    try :
        ssn = input("SSN: ")
    except (KeyboardInterrupt, EOFError) :
        return
    
    tables = list()
    tables.append("EMPLOYEE")
    lockTable(tables)
        
    while (1) :
        os.system('clear')
        viewEmployee(ssn)

        printBorder(35)
        print("* %sModify Employee Options %s%s" % (bcolors.BOLD, bcolors.ENDC, stringToBorder(" * Modify Employee Options", 34)))
        
        optionLine = ("* 0.) Exit")
        print(optionLine + stringToBorder(optionLine,34))
        for option in employee :
            if option == 4 : continue
            optionLine = ("* %d.) %s" % (option, employee[option]))
            print(optionLine + stringToBorder(optionLine,34))
        printBorder(35)
        
        while (1) :
            try :
                option = int(input("Enter Option: "))
                if (option == 0) : unlockTables(); return
                value = input("Change Value to: ")
                break
            except (KeyboardInterrupt, EOFError) :
                return

        query = "UPDATE EMPLOYEE SET %s='%s' WHERE Ssn=%s" % (employeeFields[option], value, ssn)
        if(handleQueryError(query)) :
            input("Continue ... ")
        unlockTables()

## ================ Remove ================ 
def executeRemove(query) :
    if (handleQueryError(query)) :
        print("Unable to Delete Record")
    else :
        print("Successfully Deleted Record")
    unlockTables()
    input("...")

def confirmDeletion() :
    confirm = str(input("Confirm Deletion of Record (Y/N): "))
    if (confirm != 'Y' and confirm != 'y') :
        print(bcolors.WARNING + "Deletion Abandoned" + bcolors.ENDC)
        input("...")
        return 0
    return 1

def removeEmployee() : ## ssn

    _header = "* Remove Employee *"
    print(getHeader(_header))

    try :
        ssn = input("SSN: ")
    except (KeyboardInterrupt, EOFError) :
        return
    
    tables = list()
    tables.append("EMPLOYEE")
    lockTable(tables)
    os.system('clear')

    getTablesReferencedForKey("Ssn", ssn)
    viewEmployee(ssn)
    
    if (confirmDeletion() == 0) : return
    
    query = "DELETE FROM EMPLOYEE WHERE Ssn=%s" % (ssn)

    executeRemove(query)
    
def removeDependent() : ## essn

    _header = "* Remove Dependent *"
    print(getHeader(_header))

    try :
        essn = input("Employee SSN: ")
    except (EOFError, KeyboardInterrupt) :
        return
    
    tables = list()
    tables = ("EMPLOYEE", "DEPENDENT")
    lockTable(tables)

    clear()
    _header = "* Remove Dependent *"
    viewDependents(essn)
    try :
        name = input("Enter First Name: ")
    except (KeyboardInterrupt, EOFError) :
        return

    clear()
    viewDependent(essn, name)
    if (confirmDeletion() == 0) : return

    query = "DELETE FROM DEPENDENT WHERE Essn=%s AND Dependent_name='%s'" % (essn, name)

    executeRemove(query)

def removeDepartment() : ## Dnumber
    
    _header = "* Remove Department *"
    print(getHeader(_header))

    try :
        dno = input("Department Number: ")
    except (KeyboardInterrupt, EOFError) :
        return
    
    tables = list()
    tables.append("DEPARTMENT")
    lockTable(tables)
    os.system('clear')

    _header = "* Remove Department *"
    print(getHeader(_header))

    getTablesReferencedForKey("Dnumber", dno)
    viewDepartment(dno,0)

    if (confirmDeletion() == 0) : return

    query = "DELETE FROM DEPARTMENT WHERE Dnumber=%s" % (dno)

    executeRemove(query)

def removeDepartmentLocation() : ## Dnumber

    _header = "* Remove Department Location *"
    print(getHeader(_header))
    
    try :
        dno = input("Department Number: ")
    except (KeyboardInterrupt, EOFError) :
        return
    
    lockTable(("DEPARTMENT", "DEPT_LOCATIONS"))
    os.system('clear')

    print(getHeader(_header))
    viewDepartmentLocation(dno)
    
    locationName = input("Location Name: ")

    os.system('clear')
    viewDepartmentLocation(dno, locationName)
    if (confirmDeletion() == 0) : return

    query = "DELETE FROM DEPT_LOCATIONS WHERE Dnumber=%s AND Dlocation='%s'" % (dno, locationName)

    executeRemove(query)

## ================ Category Options ================ 
employeeOptions = {
    1:("Add Employee", addEmployee),
    2:("View Employee", viewEmployee),
    3:("Modify Employee", modifyEmployee),
    4:("Remove Employee", removeEmployee)
}

dependentOptions = {
    1:("Add Dependent", addDependent),
    2:("Remove Dependent", removeDependent)

}

departmentOptions = {
    1:("Add Department", addDepartment),
    2:("View Department", viewDepartment),
    3:("Remove Department", removeDepartment),
}

deptLocOptions = {
    1:("Add Department Location", addDepartmentLocation),
    2:('Remove Department Location', removeDepartmentLocation)
}

## ================ Category Menus ================ 
def generalMain(optionsDict) :
    
    clear()
    printBorder(35)
    print("* %sOptions%s%s" % (bcolors.BOLD, bcolors.ENDC, stringToBorder("* Options", 34)))
    
    for option in optionsDict :
        optionLine = "* %d.) %s" % (option, optionsDict[option][0])
        print(optionLine + stringToBorder(optionLine, 34))
    
    printBorder(35)

def employeeMain() :
   
   generalMain(employeeOptions)
   option = int(input("Choose an Option: "))
   os.system('clear')
   if option  == 2 : employeeOptions[option][1](None, 1)
   else : employeeOptions[option][1]()

def departmentMain() :
    
    generalMain(departmentOptions)
    option = int(input("Choose an Option: "))
    os.system('clear')
    if option == 2 : departmentOptions[option][1](None, 1)
    else : departmentOptions[option][1]()

def deptLocMain() :
    
    generalMain(deptLocOptions)
    option = int(input("Choose an Option: "))
    os.system('clear')
    deptLocOptions[option][1]()

def dependentMain() :
   
   generalMain(dependentOptions)
   option = int(input("Choose an Option: "))
   os.system('clear')
   dependentOptions[option][1]()

## ================ Main ================ 
mainOptions = {
    1: ("Employee", employeeMain),
    2: ("Department", departmentMain),
    3: ("Department Location", deptLocMain),
    4: ("Dependent", dependentMain),
    0: ("Exit", sys.exit)
}

if __name__ == '__main__' :
    initialLaunch = True
    while (1) :
        if not initialLaunch :
            input('Continue ... ')
        os.system('clear')
        
        while(1) :
            try :
                os.system('clear')
                printBorder(35)
                print("* %sOptions%s%s" % (bcolors.BOLD, bcolors.ENDC, stringToBorder("* Options", 34)))
                for option in mainOptions :
                    optionLine = "* %d.) %s" % (option, mainOptions[option][0])
                    print(optionLine + stringToBorder(optionLine, 34))
                printBorder(35)
                option = int(input("Choose an Option: "))
                if option not in mainOptions.keys() :
                    raise KeyError
                os.system('clear')
                mainOptions[option][1]()
                initialLaunch = False
            except (ValueError,KeyError) :
                os.system('clear')
                print(bcolors.FAIL + "\nEnter Valid Option\n" + bcolors.ENDC)
                input("OK...")
            except (EOFError, KeyboardInterrupt) :
                os.system('clear')


