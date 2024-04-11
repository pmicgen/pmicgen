class LDO:
    def __init__(self, psr_condition, load_regulation_condition, phase_margin_condition, size_condition):
        if psr_condition=="min":
            self.psr_condition = float('inf')
        else:
            self.psr_condition = psr_condition

        if load_regulation_condition=="min":
            self.load_regulation_condition = float('inf')
        else:
            self.load_regulation_condition = load_regulation_condition

        if phase_margin_condition=="max":
            self.phase_margin_condition = float('-inf')
        else:
            self.phase_margin_condition = phase_margin_condition

        if size_condition=="min":
            self.size_condition = float('inf')
        else:
            self.size_condition = size_condition