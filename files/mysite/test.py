import re
class Solution:
    # @param {string} s
    # @return {integer}
    import re
    def calculate(self, s):
        s = re.sub(' ', '', s)
        result, end = self.sub(s, 0)
        return result
    def sub(self, s, i):
        
        operators = []
        operands = []
        while i < len(s):
            if s[i] == '+' or s[i] == '-':
                operators.append(s[i])
                i = i + 1
            elif s[i] == '(':
                operand, i = self.sub(s, i+1)
                operands.append(operand)
            elif s[i] == ')':
                i = i + 1
                break
            else:
                start = i
                while i < len(s) and s[i] <= '9' and s[i] >= '0':
                    i = i + 1
                operands.append(int(s[start:i]))
                
        result = operands[0]
        for u,v in zip(operands[1:], operators):
            if v is '+':
                result = result + u
            else:
                reuslt = result - u
        return result, i

s = Solution()
a=s.calculate("1 + 1")
print a