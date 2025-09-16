
from utils.visualize import AlgorithmVisualizer

desc = "https://leetcode.com/problems/replace-non-coprime-numbers-in-array/description/"
class App(AlgorithmVisualizer):
    def __init__(self, title = "Replace Non-Coprime Numbers in Array", description = desc,
                 nums = []):
        self.nums = nums
        super().__init__(title, description)
    def run_algorithm(self):
        from math import gcd
        
        return super().run_algorithm()