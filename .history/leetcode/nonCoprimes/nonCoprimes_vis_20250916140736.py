
from utils.visualize import AlgorithmVisualizer

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

desc = "https://leetcode.com/problems/replace-non-coprime-numbers-in-array/description/"
class App(AlgorithmVisualizer):
    def __init__(self, title = "Replace Non-Coprime Numbers in Array", description = desc,
                 nums = []):
        self.res = DoubleLinkedList(nums)
        super().__init__(title, description)
    def run_algorithm(self):
        from math import gcd
        
        return super().run_algorithm()