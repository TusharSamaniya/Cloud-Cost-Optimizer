from abc import ABC, abstractmethod

class CloudMLModel(ABC):
    """
    Abstract Base Class for all ML Models.
    This guarantees every model we build will have the exact same structure.
    """
    
    @abstractmethod
    def run(self, user_id: int):
        """Executes the machine learning algorithm."""
        pass
        
    @abstractmethod
    def save_results(self, user_id: int, results):
        """Saves the AI predictions back into the PostgreSQL database."""
        pass