

def replaceNonCoprimes(self, nums: list[int]) -> list[int]:
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

    res = DoubleLinkedList(nums)
    @cache
    def pgcd(a, b): return gcd(a, b)
    @cache
    def ppcm(a, b): return a * b // pgcd(a, b)

    now = res.head
    while now != res.tail:
        # If we got to the tail, we're done
        nxt = now.next
        if pgcd(now.val, nxt.val) > 1:
            new = Node(ppcm(now.val, nxt.val))
            # Update the links to replace old nodes by one
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

    return list(res)
