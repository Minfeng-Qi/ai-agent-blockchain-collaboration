"""
Utility functions for agent learning and bidding strategy.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any


def calculate_ema(old_value: float, new_value: float, alpha: float) -> float:
    """
    Calculate Exponential Moving Average (EMA) update.
    
    Args:
        old_value: Previous value
        new_value: New value
        alpha: EMA factor (0-1), higher values give more weight to old value
        
    Returns:
        Updated EMA value
    """
    return (alpha * old_value + (100 - alpha) * new_value) / 100


def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize a score to be within a specified range.
    
    Args:
        score: Score to normalize
        min_val: Minimum value of the range
        max_val: Maximum value of the range
        
    Returns:
        Normalized score
    """
    return max(min_val, min(max_val, score))


def calculate_capability_match(
    task_capabilities: List[str], 
    agent_capabilities: Dict[str, float]
) -> Tuple[float, float]:
    """
    Calculate how well an agent's capabilities match a task's requirements.
    
    Args:
        task_capabilities: List of capabilities required for the task
        agent_capabilities: Dictionary mapping capability tags to weights
        
    Returns:
        Tuple of (capability_match_score, total_possible_weight)
    """
    capability_match = 0
    total_weight = 0
    
    for cap in task_capabilities:
        if cap in agent_capabilities:
            capability_match += agent_capabilities[cap]
            total_weight += 100
    
    return capability_match, total_weight


def calculate_workload_penalty(workload: int, sensitivity: float) -> float:
    """
    Calculate penalty for current workload.
    
    Args:
        workload: Current agent workload
        sensitivity: How sensitive the agent is to workload
        
    Returns:
        Workload penalty score
    """
    # Non-linear penalty that increases more rapidly at higher workloads
    base_penalty = workload * sensitivity * 10
    
    # Add exponential component for high workloads
    if workload > 5:
        exponential_penalty = math.pow(1.5, workload - 5) * sensitivity * 5
        return base_penalty + exponential_penalty
    
    return base_penalty


def apply_exploration_factor(utility: float, exploration_rate: float) -> float:
    """
    Apply exploration factor to utility calculation.
    
    Args:
        utility: Base utility score
        exploration_rate: Probability of applying exploration
        
    Returns:
        Utility with exploration factor applied
    """
    if random.random() < exploration_rate:
        # Add some randomness for exploration
        # More bias toward positive exploration to encourage trying new things
        exploration_boost = random.uniform(-10, 20)
        return utility + exploration_boost
    
    return utility


def calculate_bid_position(utility: float, risk_tolerance: float) -> float:
    """
    Calculate bidding position based on utility and risk tolerance.
    
    Args:
        utility: Utility score (0-100)
        risk_tolerance: Risk tolerance factor (0-1)
        
    Returns:
        Bid position factor (0-1), where lower means more aggressive bid
    """
    # Invert utility (higher utility means lower bid)
    utility_factor = 1 - (utility / 100)
    
    # Apply risk tolerance (higher risk tolerance means more aggressive bidding)
    risk_factor = 1 - risk_tolerance
    
    # Combine factors
    bid_position = utility_factor * risk_factor
    
    return bid_position


def calculate_task_type_preference_boost(
    task_capabilities: List[str],
    task_type_preferences: Dict[str, float]
) -> float:
    """
    Calculate preference boost based on past performance on similar tasks.
    
    Args:
        task_capabilities: List of capabilities required for the task
        task_type_preferences: Dictionary mapping task types to preference scores
        
    Returns:
        Preference boost score
    """
    task_type_key = "_".join(sorted(task_capabilities))
    
    if task_type_key in task_type_preferences:
        preference_score = task_type_preferences[task_type_key]
        # Boost based on past performance on similar tasks (-10 to +10)
        return (preference_score - 50) * 0.2
    
    return 0


def adjust_confidence_factor(
    confidence_factor: float,
    avg_score: float,
    learning_rate: float
) -> float:
    """
    Adjust confidence factor based on recent performance.
    
    Args:
        confidence_factor: Current confidence factor
        avg_score: Average recent score
        learning_rate: Learning rate for adjustment
        
    Returns:
        Adjusted confidence factor
    """
    if avg_score > 70:
        # Good performance, increase confidence
        return min(1.0, confidence_factor + learning_rate)
    elif avg_score < 50:
        # Poor performance, decrease confidence
        return max(0.5, confidence_factor - learning_rate)
    
    return confidence_factor


def adjust_risk_tolerance(
    risk_tolerance: float,
    reputation: int,
    learning_rate: float
) -> float:
    """
    Adjust risk tolerance based on reputation.
    
    Args:
        risk_tolerance: Current risk tolerance
        reputation: Agent's reputation
        learning_rate: Learning rate for adjustment
        
    Returns:
        Adjusted risk tolerance
    """
    if reputation > 70:
        # High reputation, can take more risks
        return min(0.8, risk_tolerance + learning_rate * 0.5)
    elif reputation < 40:
        # Low reputation, be more conservative
        return max(0.2, risk_tolerance - learning_rate * 0.5)
    
    return risk_tolerance


def adjust_workload_sensitivity(
    workload_sensitivity: float,
    workload: int,
    learning_rate: float
) -> float:
    """
    Adjust workload sensitivity based on current workload.
    
    Args:
        workload_sensitivity: Current workload sensitivity
        workload: Current workload
        learning_rate: Learning rate for adjustment
        
    Returns:
        Adjusted workload sensitivity
    """
    if workload > 5:
        # High workload, be more sensitive
        return min(0.5, workload_sensitivity + learning_rate)
    elif workload < 2:
        # Low workload, be less sensitive
        return max(0.1, workload_sensitivity - learning_rate)
    
    return workload_sensitivity


def decay_exploration_rate(
    exploration_rate: float,
    decay_rate: float,
    min_exploration_rate: float
) -> float:
    """
    Decay exploration rate over time, but maintain minimum.
    
    Args:
        exploration_rate: Current exploration rate
        decay_rate: Rate at which exploration decays
        min_exploration_rate: Minimum exploration rate
        
    Returns:
        Decayed exploration rate
    """
    return max(min_exploration_rate, exploration_rate * decay_rate)


def should_bid_on_task(
    reputation: int,
    min_reputation: int,
    utility: float,
    min_utility_threshold: float,
    workload: int,
    max_workload: int,
    task_type_key: str,
    task_type_preferences: Dict[str, float],
    exploration_rate: float
) -> Tuple[bool, str]:
    """
    Decide whether the agent should bid on a task.
    
    Args:
        reputation: Agent's reputation
        min_reputation: Minimum reputation required for the task
        utility: Calculated utility of the task
        min_utility_threshold: Minimum utility to consider bidding
        workload: Current agent workload
        max_workload: Maximum workload capacity
        task_type_key: Key for the task type
        task_type_preferences: Dictionary mapping task types to preference scores
        exploration_rate: Probability of exploring new tasks
        
    Returns:
        Tuple of (should_bid, reason)
    """
    # Check if agent meets minimum reputation requirement
    if reputation < min_reputation:
        return False, f"Reputation too low: {reputation} < {min_reputation}"
    
    # Check if utility meets minimum threshold
    if utility < min_utility_threshold:
        return False, f"Utility too low: {utility} < {min_utility_threshold}"
    
    # Check workload capacity
    if workload >= max_workload:
        return False, f"Workload too high: {workload} >= {max_workload}"
    
    # Check task type preferences
    if task_type_key in task_type_preferences:
        preference = task_type_preferences[task_type_key]
        if preference < 40 and random.random() > exploration_rate:
            return False, f"Low preference for task type: {preference} < 40"
    
    # Apply exploration rate
    if random.random() < exploration_rate:
        return True, "Exploration triggered: bidding despite parameters"
            
    return True, "Task meets bidding criteria" 