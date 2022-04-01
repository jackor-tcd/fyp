import numpy as np
import cvxpy as cp
import pandas as pd
import csv


def check_if_int(string):

    # Returns true if the arguement passed is an integer
    try:
        int(string)
    except ValueError:
        return False
    return True


def read_given_csv_and_add_to_lists(csvName, studentsL, modulesL, resultsL):

    # Read csv file
    df1 = pd.read_csv(csvName).T
    df2 = pd.read_csv(csvName)

    # Strings that are searched for in csv file
    substring1 = 'Exam '
    substring2 = 'Module'

    # Locate strings in csv file
    fullExamNumCol = df1[df1.apply(lambda row: row.astype(str).str.contains(substring1, case=False).any(), axis=1)]
    fullExamNumRow = df2[df2.apply(lambda row: row.astype(str).str.contains(substring1, case=False).any(), axis=1)]
    fullModNumCol = df1[df1.apply(lambda row: row.astype(str).str.contains(substring2, case=False).any(), axis=1)]
    fullModNumRow = df2[df2.apply(lambda row: row.astype(str).str.contains(substring2, case=False).any(), axis=1)]

    studentRowIndex = int(fullExamNumRow.index[0])
    studentColIndex = int(df2.columns.get_loc(fullExamNumCol.index[0]))
    moduleRowIndex = int(fullModNumRow.index[0])
    moduleColIndex = int(df2.columns.get_loc(fullModNumCol.index[0]))

    # Read student data into relevant arrays
    it = 1
    flag = True
    while flag:
        cell = df1.iloc[studentColIndex, studentRowIndex + it]
        if check_if_int(cell):
            for i in range(moduleColIndex, len(df1)):
                if str(df1.iloc[i, moduleRowIndex])[-5:].isdigit():
                    tcell = df1.iloc[i, studentRowIndex + it]
                    if check_if_int(tcell):
                        studentsL.append(cell)
                        modulesL.append(df1.iloc[i, moduleRowIndex])
                        resultsL.append(tcell)
            it += 1
        else:
            flag = False


def check_number_of_modules_sat(student, studentsL):

    # Returns the number of modules sat by a given student
    return studentsL.count(student)


def check_number_of_students_in_module(module, modulesL):

    # Returns the number of students who sat a given module
    return modulesL.count(module)


def create_list_of_student_modules(student, studentsL, modulesL):

    # Returns a list containing all modules sat by a given student
    listOfModules = []
    for i in range(len(studentsL)):
        if studentsL[i] == student:
            listOfModules.append(modulesL[i])
    return listOfModules


def create_list_of_students_in_module(module, studentsL, moduleL):

    # Returns a list containing all students who sat a given module
    listOfStudents = []
    for i in range(len(moduleL)):
        if moduleL[i] == module:
            listOfStudents.append(studentsL[i])
    return listOfStudents


def find_overall_average(resultsL):

    # Returns the average of all grades
    sum = 0
    for i in range(len(resultsL)):
        sum = sum + float(resultsL[i])
    return sum / len(resultsL)


def find_student_mark_in_module(student, module, studentsL, moduleL, resultsL):

    # Returns a given students grade in a given module
    for i in range(len(studentsL)):
        if studentsL[i] == student:
            if moduleL[i] == module:
                return resultsL[i]


def find_linear_component_for_varlist(i, varList, studentsL, modulesL, resultsL, numStudents):

    # Returns the linear component of an offset

    # Since the first elements held in our variableList are the students offsets, we first consider their linear components.
    if i < numStudents:
        sum = 0.
        for j in create_list_of_student_modules(varList[i], studentsL, modulesL):
            sum = sum + find_overall_average(resultsL) - float(find_student_mark_in_module(varList[i], j, studentsL, modulesL, resultsL))
        return 2 * sum
    # We now consider the modules offsets
    else:
        sum = 0.
        for j in create_list_of_students_in_module(varList[i], studentsL, modulesL):
            sum = sum + float(find_student_mark_in_module(j, varList[i], studentsL, modulesL, resultsL))
        return (2 * len(create_list_of_students_in_module(varList[i], studentsL, modulesL)) * find_overall_average(resultsL)) - (2 * sum)


def find_matrix_entry_for_varlist(i, j, varList, studentsL, modulesL, numStudents):

    # Returns the (i, j) entry for the quadratic form

    # This concerns the upper triangle
    if i <= j:
        if i < numStudents:
            if i == j:
                return 2 * check_number_of_modules_sat(varList[i], studentsL)
            elif j < numStudents:
                return 0
            else:
                if varList[j] in create_list_of_student_modules(varList[i], studentsL, modulesL):
                    return 2
                else:
                    return 0
        else:
            if i == j:
                return 2 * check_number_of_students_in_module(varList[j], modulesL)
            else:
                return 0
    # The lower triangle
    else:
        # Since the matrix is symmetric
        return find_matrix_entry_for_varlist(j, i, varList, studentsL, modulesL, numStudents)


def find_constraint_array(i, j, numStudents):

    # Returns the (i, j) entry of the constraint array
    if i == 1:
        if j < numStudents:
            return 1
        else:
            return 0
    else:
        if j < numStudents:
            return 0
        else:
            return 1


def find_offset(studentOrModule, varList, output):

    # Returns the offset for the given student or module
    for i in range(len(varList)):
        if varList[i] == studentOrModule:
            return output[i]


def find_residual(student, module, varList, studentsL, modulesL, resultsL, output):

    # Returns the residual for the given student and module
    return float(find_student_mark_in_module(student, module, studentsL, modulesL, resultsL)) - find_overall_average(resultsL) - find_offset(student, varList, output) - find_offset(module, varList, output)


def find_index_of_magnitude(moduleL):

    # Returns an index for the arrangement of moduleL from highest to lowest
    index = []
    tmodule = list(moduleL)
    for j in range(len(tmodule)):
        max = float(tmodule[0])
        maxIndex = 0
        for i in range(len(tmodule)):
            if max < float(tmodule[i]):
                max = float(tmodule[i])
                maxIndex = i
        index.append(maxIndex)
        tmodule[maxIndex] = -10000
    return index


def find_index_of_abs_magnitude(moduleL):

    # Returns an index for the arrangement of the absolute values of elements from moduleL from highest to lowest
    index = []
    tmodule = list(moduleL)
    for j in range(len(tmodule)):
        max = abs(float(tmodule[0]))
        maxIndex = 0
        for i in range(len(tmodule)):
            if max < abs(float(tmodule[i])):
                max = abs(float(tmodule[i]))
                maxIndex = i
        index.append(maxIndex)
        tmodule[maxIndex] = 0
    return index


# Declaration of main arrays
studentArray = []
moduleArray = []
resultsArray = []
csvList = []

# Get csv file information from user
option = input('Input a file Y/N?')
if option.upper() == 'N':
    quit()
else:
    csvList.append(input("Please enter file name in the form filename.csv (Make sure file is in the same directory as this program):"))
    escape = True
    while escape:
        escape = input('Input another file Y/N?')
        if escape.upper() == 'N':
            escape = False
        else:
            csvList.append(input("Please enter file name in the form filename.csv (Make sure file is in the same directory as this program):"))

# Read csv information into main arrays
for i in csvList:
    read_given_csv_and_add_to_lists(i, studentArray, moduleArray, resultsArray)

# Get simple information from arrays
studentList = list(dict.fromkeys(studentArray))
moduleList = list(dict.fromkeys(moduleArray))
numberOfStudents = len(studentList)
numberOfModules = len(moduleList)

# Create list to be attributed to offsets
variableList = studentList + moduleList

# Instantiate important arrays for optimisation
quadraticArray = np.empty([len(variableList), len(variableList)])
linearComponent = np.empty([len(variableList)])
constraintArray = np.empty([2, len(variableList)])
zeroArray = np.zeros(2)

# Create main array for quadratic form
for i in range(len(variableList)):
    for j in range(len(variableList)):
        quadraticArray[i, j] = find_matrix_entry_for_varlist(i, j, variableList, studentArray, moduleArray,
                                                             numberOfStudents)

# Create array for linear component
for i in range(len(variableList)):
    linearComponent[i] = find_linear_component_for_varlist(i, variableList, studentArray, moduleArray, resultsArray,
                                                           numberOfStudents)

# Create constraint array
for i in range(2):
    for j in range(len(variableList)):
        constraintArray[i, j] = find_constraint_array(i, j, numberOfStudents)

# Formulate optimisation problem
x = cp.Variable(len(variableList))
prob = cp.Problem(cp.Minimize((1 / 2) * cp.quad_form(x, quadraticArray) + linearComponent.T @ x),
                  [constraintArray @ x == zeroArray])

# Find optimal offsets using cvxpy
prob.solve()

# Instantiate important arrays for solution data
residualArray = np.empty([len(studentArray)])
studentOffsetArray = np.empty([len(studentArray)])
moduleOffsetArray = np.empty([len(moduleArray)])

# Read residuals into form compatible with earlier important arrays
for i in range(len(studentArray)):
    residualArray[i] = find_residual(studentArray[i], moduleArray[i], variableList, studentArray, moduleArray,
                                     resultsArray, x.value)

# Read student offsets into form compatible with earlier important arrays
for i in range(len(studentArray)):
    studentOffsetArray[i] = find_offset(studentArray[i], variableList, x.value)

# Read module offsets into form compatible with earlier important arrays
for i in range(len(moduleArray)):
    moduleOffsetArray[i] = find_offset(moduleArray[i], variableList, x.value)

# Data for csv export
csv_header = ['Student Number', 'Module Code', 'Result', 'Student Offset', 'Module Offset', 'Residual']
csv_data = []

# Prompt for data export format
dataExportOption = int(input('Would you like your data ordered by 1 - Student Offset, 2 - Module Offset, 3 - Residual, 4 - Magnitude of Residual. Please enter number:'))

# Data formatting
if dataExportOption == 1:
    # Orders data by students offset from largest to smallest
    for i in find_index_of_magnitude(studentOffsetArray):
        csv_data.append(
            [studentArray[i], moduleArray[i], float(resultsArray[i]), studentOffsetArray[i], moduleOffsetArray[i],
             residualArray[i]])
elif dataExportOption == 2:
    # Orders data by module offset from largest to smallest
    for i in find_index_of_magnitude(moduleOffsetArray):
        csv_data.append(
            [studentArray[i], moduleArray[i], float(resultsArray[i]), studentOffsetArray[i], moduleOffsetArray[i],
             residualArray[i]])
elif dataExportOption == 3:
    # Orders data by residual from largest to smallest
    for i in find_index_of_magnitude(residualArray):
        csv_data.append(
            [studentArray[i], moduleArray[i], float(resultsArray[i]), studentOffsetArray[i], moduleOffsetArray[i],
             residualArray[i]])
elif dataExportOption == 4:
    # Orders data by absolute value of residual from largest to smallest
    for i in find_index_of_abs_magnitude(residualArray):
        csv_data.append(
            [studentArray[i], moduleArray[i], float(resultsArray[i]), studentOffsetArray[i], moduleOffsetArray[i],
             residualArray[i]])
else:
    # If nothing is selected it exports in its standard from
    for i in range(len(studentArray)):
        csv_data.append([studentArray[i], moduleArray[i], float(resultsArray[i]), studentOffsetArray[i], moduleOffsetArray[i], residualArray[i]])

# Read to csv file
with open('data.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)
    writer.writerows(csv_data)

# Indicate completion of code to user
print("Exported data.csv")
