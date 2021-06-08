#returns the index of the cloest 2 values in a 2-tuple,
# returns the same values if:
#   the value exist in the dataset
#   the value is less than the min
#   the value is more than the max
# for this project, distinction seems unnecessary but maybe a third value in
# the tuple such as "found, min, max" can help distinguish the output
def bin_search_closest(val, dataset):
    max = len(dataset) - 1
    low, high = 0, max

    while low <= high:
        mid = (high - low)//2 + low

        if val < dataset[mid]:
            high = mid - 1
        elif val > dataset[mid]:
            low = mid + 1
        else:
            low_index = mid
            high_index = mid
            status = "FOUND"
            break
    else:
        if high < 0:
            low_index, high_index = 0, 0
            status = "MIN"
        elif low > max:
            low_index, high_index = max, max
            status = "MAX"
        else:
            low_index, high_index = high, low
            status = "IN_RANGE"
    return (low_index, high_index, status)


