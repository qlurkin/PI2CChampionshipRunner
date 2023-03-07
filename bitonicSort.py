import random
import asyncio
from collections import defaultdict

c = defaultdict(lambda: 0)


async def compareInt(a, b):
    print(a, '<>', b)
    c[a] += 1
    c[b] += 1
    await asyncio.sleep(2)
    if a < b:
        return a, b
    return b, a


def greatestPowerOfTwoLessThan(n):
    assert n > 1
    res = 0
    next = 1
    while next < n:
        res = next
        next = next*2
    return res


async def compare(L, i, j, ascending, comp):
    if ascending:
        L[i], L[j] = await comp(L[i], L[j])
    else:
        L[j], L[i] = await comp(L[i], L[j])


async def bitonicSort(L, start, length, ascending, comp):
    if length > 1:
        m = length//2
        await asyncio.gather(
            bitonicSort(L, start, m, not ascending, comp),
            bitonicSort(L, start+m, length-m, ascending, comp)
        )
        await bitonicMerge(L, start, length, ascending, comp)


async def bitonicMerge(L, start, length, ascending, comp):
    if length > 1:
        m = greatestPowerOfTwoLessThan(length)
        await asyncio.gather(*[
            compare(L, i, i+m, ascending, comp)
            for i in range(start, start+length-m)
        ])
        await asyncio.gather(
            bitonicMerge(L, start, m, ascending, comp),
            bitonicMerge(L, start+m, length-m, ascending, comp)
        )


async def sort(L, comp):
    await bitonicSort(L, 0, len(L), True, comp)


async def main():
    L = list(range(12))
    L = L + L
    random.shuffle(L)
    print(L)
    await sort(L, compareInt)
    print(L)


asyncio.run(main())
print(c)
