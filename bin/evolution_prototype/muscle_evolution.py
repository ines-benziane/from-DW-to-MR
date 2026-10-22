from domain.entities.t2_stats import T2Stats

class MuscleEvolution:
    """Represents the evolution of a stat for a muscle between two exams"""
    
    def __init__(self, old, new):
        """Initialize comparison data"""
        if type(old) != type(new):
            raise ValueError(f"Can't compare to differents stats type.")
        self.old = old
        self.new = new

    @property
    def percentage_change(self) -> float:
        """Calculate percentage change"""
        return ((self.new.mean - self.old.mean) / self.old.mean * 100)
    
    @property
    def is_significant(self) -> bool:
        """Check if change >= 5%"""
        return abs(self.percentage_change) >= 5.0

    @property
    def evolution_status(self) -> str:
        """Return: 'degradation', 'stable', or 'improvement'"""
        if self.is_significant == False:
            return "stable"
        if self.percentage_change > 0:
            return "degradation"
        elif self.percentage_change < 0:
            return "improvement"
