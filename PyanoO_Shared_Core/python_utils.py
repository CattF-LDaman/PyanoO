
def merge_dict(start_d,merge_d):

    return {**start_d,**merge_d}

def list_difference(l1,l2):

    return [i for i in l1 if i not in l2]

def list_difference_symmetric(l1,l2):

    return set(l1).symmetric_difference(l2)