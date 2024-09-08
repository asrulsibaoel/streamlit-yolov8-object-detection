from machine_learning.config import Settings


class App:
    
    def __init__(self, config: Settings) -> None:
        self.config = config
        
    def init_vector_db(self) -> None:
        pass
    
    async def init_amqp_connection(self) -> None:
        pass
    
    async def run(self) -> None:
        
        return