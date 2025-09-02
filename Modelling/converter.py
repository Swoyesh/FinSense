def l_t_id_converter(unique_labels):
    return {label: i for i, label in enumerate(unique_labels)}

def id_t_l_converter(l_to_id):
    return {i: label for label, i in l_to_id.items()}

loader = l_t_id_converter(['Personal Care', 'Education'])
ider = id_t_l_converter(loader)
