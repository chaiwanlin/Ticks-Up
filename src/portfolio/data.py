class Data:
    def __init__(self, value, data):
        self.value = value
        self.data = data
    
    def sort_range(data, value, range):
        upper_bound = value * (1 + range)
        lower_bound = value * (1 - value)

        result = []
        count = 0
        for e in data:
            if lower_bound <= e.value <= upper_bound:
                result[count] = e
                count = count + 1
        
        return result