class LDO:
    def __init__(self, psr_condition, load_regulation_condition, phase_margin_condition, size_condition):
        optimize = {}
        if psr_condition=="min":
            self.psr_condition = float('inf')
            optimize["psr_condition"]="min"
        else:
            self.psr_condition = psr_condition

        if load_regulation_condition=="min":
            self.load_regulation_condition = float('inf')
            optimize["load_regulation_condition"]="min"
        else:
            self.load_regulation_condition = load_regulation_condition

        if phase_margin_condition=="max":
            self.phase_margin_condition = float('-inf')
            optimize["phase_margin_condition"]="max"
        else:
            self.phase_margin_condition = phase_margin_condition

        if size_condition=="min":
            self.size_condition = float('inf')
            optimize["size_condition"]="min"
        else:
            self.size_condition = size_condition

        self.optimize = optimize