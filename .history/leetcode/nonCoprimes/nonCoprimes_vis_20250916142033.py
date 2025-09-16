
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
    
@cache
def pgcd(a, b): return gcd(a, b)
@cache
def ppcm(a, b): return a * b // pgcd(a, b)

desc = "https://leetcode.com/problems/replace-non-coprime-numbers-in-array/description/"
class App(AlgorithmVisualizer):
    def __init__(self, title = "Replace Non-Coprime Numbers in Array", description = desc,
                 nums = []):
        self.res = DoubleLinkedList(nums)
        super().__init__(title, description)
    def run_algorithm(self):
        res = self.res
        now = res.head
        self.add_step(
                variables = {
                    "now": now,
                    "res": res
                }
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
                    "res": res
                }
            )
            self.res = res
        
        # return super().run_algorithm()
        return self.res
    
    def get_complexity(self):
        return {
            "time": "O(n^2) worst-case", 
            "space": "O(n)"
            }
    
    
test = App(nums = [287,41,49,287,899,23,23,20677,5,825])
test.show()