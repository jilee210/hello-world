#!/usr/bin/python
# http://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/
# https://www.python-course.eu/
# JL 091417 to demonstate python powerful/concise list comprehensions to replace most loops
# sudoku.py uses lots of list comprehensions
# JL 11/09/17 Added Extra dict comprehension and generator expression, using A-Z a-z two range expr
#==================================================================================================

# Create a new list using for/while loop
new_list = []
for i in range(1,101):
  if i % 2 == 0: # even numbers, odd_numbers => if i % 2: 
    new_list.append(i)
print("* new_list from FOR loop:\n"), new_list
new_list = []
i = 1
while i <= 100:
  if i % 2 == 0:
    new_list.append(i)
  i += 1
print("* new_list from WHILE loop:\n"), new_list

# list comprehensions 
new_list = [n for n in range(1,101) if n % 2 == 0] # numbers is list of 1..100 integers
print("* new_list from LIST_COMPREHENSION: "), new_list

# lambda function with filter/map
new_list = map(lambda n:n, filter(lambda n: n % 2 == 0, range(1,101)))
print("* new_list from LAMBDA with filter/map:\n"), new_list

# nested
print "*** Nested loops (matrix) into list comprehension"
matrix = [[a for a in range(10)], [b for b in range(10,20)]]
print "* matrix:\n", matrix

flattened = []
for row in matrix:
  for n in row:
    flattened.append(n)
print "* flattened matrix using FOR loop:\n", flattened
flattened = [n for row in matrix for n in row]
print "* flattened matrix using list COMPREHENSION:\n", flattened
flattened = [n for row in matrix for n in row if n%2 == 0]
print "* flattened matrix using list COMPREHENSION with IF:\n", flattened

print "* Pythagorean triples:" 
xyz = [(x,y,z) for x in range(1,30) for y in range(x,30) for z in range(y,30) if x**2 + y**2 == z**2]
print(xyz) 

print "* Example from sudoku.py"
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)

print "* sudoku grid squares by 9x9: \n", squares

### EXTRA: 2.7+ dict comprehension as well
### list(range(x)) in python 3  due to xrange in v2 becomes range in v3
### also can use list(itertools.chain(list1,list2,...)) lists

print "\n* EXTRA dict comprehension in 2.7+"
print("d = {chr(k): k for k in range(65, 65+26) + range(97, 97+26)}") # d = {'A':65, ..., 'Z':90, 'a':95,...,'z':122")
d = {chr(k): k for k in range(65, 65+26) + range(97, 97+26)} # d = {'A':65, ..., 'Z':90, 'a':97...'z':122}
# sum of ord values using generator expr
print "* EXTRA sum of d.items key, value, using generator expression"
print("sum(v for k, v in d.items())")
print(sum(v for k, v in d.items()))
print("sum(ord(k) for k, v in d.items())")
print(sum(ord(k) for k, v in d.items()))
