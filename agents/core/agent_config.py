"""
Configuration file for agent learning parameters.
These parameters control how agents learn and adapt their bidding strategies.
"""

class AgentConfig:
    """
    Configuration class for agent learning parameters.
    These parameters can be tuned to adjust agent behavior.
    """
    
    # Default learning parameters
    DEFAULT_CONFIG = {
        # Learning rate parameters
        "learning_rate": 0.05,        # How quickly the agent adapts its bidding strategy (0-1)
        "exploration_rate": 0.1,      # Probability of exploring new tasks (0-1)
        "decay_rate": 0.99,           # Rate at which exploration decays over time (0-1)
        "min_exploration_rate": 0.01, # Minimum exploration rate (0-1)
        
        # Bidding strategy parameters
        "min_utility_threshold": 30,  # Minimum utility to consider bidding (0-100)
        "confidence_factor": 0.8,     # How confident the agent is in its capabilities (0-1)
        "risk_tolerance": 0.5,        # How much risk the agent is willing to take (0-1)
        "workload_sensitivity": 0.2,  # How sensitive the agent is to workload (0-1)
        
        # EMA parameters
        "ema_alpha": 0.7,             # EMA factor for capability updates (0-1)
        
        # Workload parameters
        "max_workload": 10,           # Maximum workload capacity
        
        # Polling interval for blockchain monitoring (seconds)
        "polling_interval": 30,
        
        # Sync interval for blockchain state (seconds)
        "sync_interval": 300,         # 5 minutes
    }
    
    # Profiles for different agent types
    AGENT_PROFILES = {
        "balanced": DEFAULT_CONFIG,
        
        "aggressive": {
            **DEFAULT_CONFIG,
            "exploration_rate": 0.2,
            "risk_tolerance": 0.8,
            "confidence_factor": 0.9,
            "workload_sensitivity": 0.1,
        },
        
        "conservative": {
            **DEFAULT_CONFIG,
            "exploration_rate": 0.05,
            "risk_tolerance": 0.3,
            "confidence_factor": 0.7,
            "workload_sensitivity": 0.4,
            "min_utility_threshold": 40,
        },
        
        "explorer": {
            **DEFAULT_CONFIG,
            "exploration_rate": 0.3,
            "min_exploration_rate": 0.1,
            "decay_rate": 0.995,
            "risk_tolerance": 0.6,
        },
        
        "specialist": {
            **DEFAULT_CONFIG,
            "exploration_rate": 0.05,
            "confidence_factor": 0.95,
            "min_utility_threshold": 50,
        },
        
        "workload_sensitive": {
            **DEFAULT_CONFIG,
            "workload_sensitivity": 0.5,
            "max_workload": 8,
        },
    }
    
    @classmethod
    def get_profile(cls, profile_name="balanced"):
        """
        Get configuration for a specific agent profile.
        
        Args:
            profile_name: Name of the profile to use
            
        Returns:
            Dictionary with configuration parameters
        """
        if profile_name in cls.AGENT_PROFILES:
            return cls.AGENT_PROFILES[profile_name]
        else:
            return cls.DEFAULT_CONFIG
    
    @classmethod
    def create_custom_profile(cls, base_profile="balanced", **overrides):
        """
        Create a custom profile by overriding specific parameters.
        
        Args:
            base_profile: Name of the base profile to extend
            **overrides: Parameters to override
            
        Returns:
            Dictionary with configuration parameters
        """
        base_config = cls.get_profile(base_profile)
        return {**base_config, **overrides}


# Example usage
if __name__ == "__main__":
    # Get default balanced profile
    balanced_config = AgentConfig.get_profile()
    print(f"Balanced profile learning rate: {balanced_config['learning_rate']}")
    
    # Get aggressive profile
    aggressive_config = AgentConfig.get_profile("aggressive")
    print(f"Aggressive profile risk tolerance: {aggressive_config['risk_tolerance']}")
    
    # Create custom profile
    custom_config = AgentConfig.create_custom_profile(
        base_profile="conservative",
        learning_rate=0.1,
        exploration_rate=0.15
    )
    print(f"Custom profile learning rate: {custom_config['learning_rate']}")
    print(f"Custom profile risk tolerance: {custom_config['risk_tolerance']}")  # Inherited from conservative 