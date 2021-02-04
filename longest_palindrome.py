

def longestPalindrome(s):

  length = len(s)
  is_even = True
  count = 1
  all_counts = []
  
  if length % 2 == 1:
      is_even = False
  s = '0' + s + '0'   

  for i in range(1, len(s)-1):
      for j in range(1, len(s)-1):

        if not (j+i > len(s)-2 or j-i < 1):
          if(s[j+i] == s[j-i]):
            count = count + 1
        all_counts.append(count)
      count = 0
  print(max(all_counts))
                # print(i,s[j-1], s[i],s[j+1])






def longestPalindrome2(s):
  m = ''  # Memory to remember a palindrome
  for i in range(len(s)):  # i = start, O = n
      for j in range(len(s), i, -1):  # j = end, O = n^2
          print('---------')
          print(s[i:j])
          print(s[i:j][::-1])
          if len(m) >= j-i:  # To reduce time
              break
          elif s[i:j] == s[i:j][::-1]:
              m = s[i:j]
              break
  return m


print(longestPalindrome2("baaasdfacbcab"))