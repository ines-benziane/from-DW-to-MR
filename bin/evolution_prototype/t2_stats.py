class T2Stats:
    """
    T2 stats of a muscle
    
    Attributs:
        mean (float): T2 mean value in ms
        sd (float): standard deviationdu T2
    """
    
    def __init__(self, mean: float, sd: float):
        """
        Initialize T2 values.
        
        Args:
            mean (float): T2 mean value in ms
            sd (float): standard deviationdu T2
            
        Raises:
            ValueError: If invalid values
        """
        if mean < 0 :
            raise ValueError(f"T2 mean can't be negative: {mean}")
        if sd < 0 :
            raise ValueError(f"T2 sd can't be negative: {sd}")
        self.mean = mean
        self.sd = sd
    
    def __repr__(self) -> str:
        """Représentation string pour debug"""
        return f"T2(mean={self.mean}, sd={self.sd})"
    
    def __eq__(self, other) -> bool:
        """Compare deux T2Stats"""
        if not (isinstance(other, T2Stats)):
            return False
        return self.mean == other.mean and self.sd == other.sd