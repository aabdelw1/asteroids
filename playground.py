array = [1,2,3,3,2,1]
s = ")()())"

def checkDuplicates(array):
    if(len(array) == len(set(array))):
        return False
    else:
        return True


def replaceDuplicates(array):
    for i in range(len(array)):
        for j in range(i+1,len(array)):

            if(i+1 <= len(array)):
                if(array[i] == array[j]):
                    array[j] = array[i] = -1

    return array

def replaceDuplicates2(array):

    duplicateInt = 100000
    
    for i in range(len(array)):
        if array.count(array[i]) > 1:
            duplicateInt = array[i]

        if duplicateInt == array[i]:
            array[i] = -1
            

    print(array)


def longestValidParentheses(s):
        
        solution = ""
        
        for i in range(len(s)):
            if i+1 <= len(s):
                if s[i] == "(" and s[i+1] == ")":
                    solution = solution + s[i] + s[i+1]

        print(solution)
        return len(solution)


longestValidParentheses(s)