
from utils.visualize import AlgorithmVisualizer
from functools import cache
from math import gcd

class Node:
        def __init__(self, val, prev = None, nxt = None):
            self.val = val
            self.prev = prev
            self.next = nxt

        def __repr__(self):
            return f"{self.prev.val if self.prev else None}<-{self.val}->{self.next.val if self.next else None}"

class DoubleLinkedList:
    def __init__(self, iterable):
        self.head = Node(iterable[0])
        prev = self.head
        for el in iterable[1:]:
            prev.next = Node(el, prev = prev)
            prev = prev.next
        self.tail = prev

    def __iter__(self):
        now = self.head
        while now:
            yield now.val
            now = now.next

    def __repr__(self):
        return str(list(self))
    
    def index(self, node):
        idx = 0
        current = self.head
        while current:
            if current is node:
                return idx
            current = current.next
            idx += 1
        return -1  # Return -1 if node is not found
    
@cache
def pgcd(a, b): return gcd(a, b)
@cache
def ppcm(a, b): return a * b // pgcd(a, b)

class App(AlgorithmVisualizer):
    def __init__(self, title = "Replace Non-Coprime Numbers in Array", 
                 desc = "",
                 problem_url = "https://leetcode.com/problems/replace-non-coprime-numbers-in-array",
                 code_url = "https://github.com/Vic-Nas/PythonSolutions/blob/main/leetcode/nonCoprimes/nonCoprimes.vn.py",
                 nums = []):
        self.res = DoubleLinkedList(nums)
        super().__init__(title, problem_url = problem_url, description = desc, code_url = code_url)
    def run_algorithm(self):
        res = self.res
        now = res.head
        self.add_step(
                variables = {
                    "now": now,
                    "res": list(res)
                },
                highlight = [0]
            )
        while now and now.next:
            nxt = now.next
            if pgcd(now.val, nxt.val) > 1:
                new = Node(ppcm(now.val, nxt.val))
                
                if nxt != res.tail:
                    nxt.next.prev = new
                    new.next = nxt.next
                else:
                    res.tail = new
                if now != res.head:
                    now.prev.next = new
                    new.prev = now.prev
                    now = new.prev
                else:
                    res.head = new
                    now = new
            else:
                now = now.next
            self.add_step(
                variables = {
                    "now": now,
                    "res": list(res)
                },
                highlight = [res.index(now)]
            )
            self.res = res
        
        # return super().run_algorithm()
        return self.res
    
    def get_complexity(self):
        return {
            "time": "O(n^2) worst-case", 
            "space": "O(n)"
            }
    
App(
    nums = [287,41,49,287,899,23,23,20677,5,825]
).show()