

from utils.visualize import AlgorithmVisualizer

class App(AlgorithmVisualizer):
    def __init__(self, title = "1239. Maximum Length of a Concatenated String with Unique Characters", 
                 problem_url = "https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters", 
                 code_url = "https://github.com/Vic-Nas/PythonSolutions/blob/main/leetcode/maxConcatString/maxConcatString.vn.py", 
                 arr = []
                 ):
        self.inp = arr
        super().__init__(title,problem_url=problem_url, code_url=code_url)
        
    def run_algorithm(self):
        inp = self.inp
        arr = self.inp.copy()
        totalSubsets = 2 ** (len(arr))
        for i in range(len(inp)):
            s = inp[i]
            arr[i] = 0
            for carac in s:
                j = ord(carac) - ord("a")
                if arr[i] & (1 << j):
                    # strings with duplicates are considered empty
                    arr[i] = 0
                    break
                arr[i] |= (1 << j)
        self.add_step(
            variables = {
                "arr": inp,
                "Converted arr": arr
            }
        )
        
        dp = [
        (0, 0) for _ in range(totalSubsets)
    ]
        from copy import deepcopy
        for mask in range(totalSubsets):
            for j in range(len(arr)):
                if mask == (1 << j):
                    dp[mask] = (arr[j].bit_count(), arr[j])
                if mask & (1 << j):
                    maskWithoutJ = mask & ~(1 << j)
                    if dp[maskWithoutJ][0] > 0 and (dp[maskWithoutJ][1] & arr[j] == 0):
                        dp[mask] = (
                            dp[maskWithoutJ][0] + arr[j].bit_count(),
                            dp[maskWithoutJ][1] | arr[j]
                        )
                included = [inp[i] for i in range(len(inp)) if mask & (1 << i)]
                step = (j, inp[j])
                maskSaved = (f"{mask:0{len(arr)}b}"[::-1], included)
                dpSaved = [
                    (x, "".join(c for c in "abcdefghijklmnopqrstuvwxyz" if y & (1 << "abcdefghijklmnopqrstuvwxyz".index(c)))) for x, y in dp
                ]
                inpSaved = deepcopy(inp)
                self.add_step(
                    variables = {
                        "inp": inpSaved,
                        "mask": maskSaved,
                        "j": step,
                        "dp": dpSaved,
                    },
                    highlight = [mask],
                    notToHighlight = [maskSaved, step, inpSaved]
                )
        dpSaved = [
                    (x, "".join(c for c in "abcdefghijklmnopqrstuvwxyz" if y & (1 << "abcdefghijklmnopqrstuvwxyz".index(c)))) for x, y in dp
                ]
        res = max(dp)[0]
        self.add_step(
            variables = {
                "final dp": dpSaved,
                "res = max(dp)[0]": res
            }
        )
        return res
    
    def get_complexity(self):
        return {
            "time": "O(n * 2^n)",
            "space": "O(2^n)"
        }


App(arr = ["cha","r","act","ers"]).show()