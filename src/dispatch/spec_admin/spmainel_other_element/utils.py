def get_formula_list(self):
    formula_list = ["CEV001", "CEV002", "CEV003", "CEV004", "CEV005", "CEV006", "CEV007", "CEV008", "CEV009", "CEV010"]

    formula = ""

    spmainel_other = None

    for record in self.spmaniel_oe:
        if record.spec_id == self.spec.id:
            spmainel_other = record
            break

    for x in range(len(formula_list)):
        formula_name = formula_list[x].ljust(8)[:8]
        formula_min = getattr(spmainel_other, f"main_el_min_value_{formula_list[x]}").ljust(9)[:9]
        formula_max = getattr(spmainel_other, f"main_el_max_value_{formula_list[x]}").ljust(9)[:9] 
        formula_oum = getattr(spmainel_other, f"uom_{formula_list[x]}").ljust(1)[:1]
        formula_prec = getattr(spmainel_other, f"precision_{formula_list[x]}").ljust(1)[:1]
        formula += formula_name + formula_min + formula_max + formula_oum + formula_prec
    
    # Fill remaining space of 10 iterations
    formula = formula.ljust(280)

    return formula