def mergeSort(mergeThis):

    # Checks if the list is atomic
    if len(mergeThis) > 1:
        # Splits the list into two halves
        mergeList1, mergeList2 = mergeThis[:int(len(mergeThis)/2)], mergeThis[int(len(mergeThis)/2):]
        mergeList1 = mergeSort(mergeList1)
        mergeList2 = mergeSort(mergeList2)
        
    else:
        # If list IS atomic, return list of size 1
        return mergeThis

    mergeThis = []

    # MERGE
    while (len(mergeList1) > 0) or (len(mergeList2) > 0):
        
        # Merges lists if other list is empty
        if len(mergeList1) == 0:
            mergeThis = mergeThis + mergeList2
            mergeList2 = []
        elif len(mergeList2) == 0:
            mergeThis = mergeThis + mergeList1
            mergeList1 = []

        # Compares the values of list[0] and merges    
        else:
            #if len(mergeList1[0]) == len(mergeList2[0]):
            if mergeList1[0] <= mergeList2[0]:
                mergeThis.append(mergeList1.pop(0))
            else:
                mergeThis.append(mergeList2.pop(0))
            #elif len(mergeList1[0]) < len(mergeList2[0]):
            #    mergeThis.append(mergeList1.pop(0))
            #else:
            #    mergeThis.append(mergeList2.pop(0))

    return mergeThis